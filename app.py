import streamlit as st
import tabula
import webbrowser
from PyPDF2 import PdfFileReader
import base64
from io import BytesIO
import pandas as pd
import re
import pdfplumber
from collections import namedtuple

###############################################################################################################################################################
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Helper function to set a background image of our choice


st.markdown(
    """
<style>
.sidebar .sidebar-content {
    background-image: linear-gradient(#fed8b1,#808080);
    color: white;
}
</style>
""",
    unsafe_allow_html=True,
)


from PIL import Image
logo = Image.open('wns.jpg')
st.sidebar.image(logo, use_column_width=True)

st.sidebar.text("Designed by QBE Team")

###############################################################################################################################################################

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc


###############################################################################################################################################################

html_temp = """
            <div style="background-color:Black ;padding:10px">
            <h2 style="color:Orange;text-align:center;">Document Analysis</h2>
            </div>
            """
st.markdown(html_temp, unsafe_allow_html=True)

###############################################################################################################################################################
### Upload a dataset.
st.header("Upload your PDF file")
data_file = st.file_uploader("Upload pdf", type=['pdf'])
#count = read_pdf(data_file)
st.set_option('deprecation.showfileUploaderEncoding', False)
if data_file is not None:
    file_details = {"Filename": data_file.name, "FileType": data_file.type,
                    "FileSize": data_file.size
                    }
    st.text(file_details)
    dfs = tabula.read_pdf(data_file, pages="all", stream=True)
    a = len(dfs)
    page_details = {"Number of Tables in the uploaded PDF is ": a}
    st.text(page_details)
    for i in range(a):
        st.subheader("Table {}".format(i+1))
        st.dataframe(dfs[i].head())

    b = st.number_input('Which table you want to download', min_value = 1, max_value = a, step = 1)
    b = int(b)-1
    df = dfs[b]
    st.markdown(get_table_download_link(df), unsafe_allow_html=True)


###############################################################################################################################################################
st.header("Lets look into more")
st.subheader("PDF-1")

first = Image.open('1.PNG')
st.image(first, use_column_width=500)

Line = namedtuple('Line', 'company_id company_name doctype reference currency voucher inv_date due_date open_amt_tc open_amt_bc current months1 months2 months3')
company_re = re.compile(r'(V\d+) (.*) Phone:')
line_re = re.compile(r'\d{2}/\d{2}/\d{4} \d{2}/\d{2}/\d{4}')
lines = []
total_check = 0
with pdfplumber.open("Sample Report.pdf") as pdf:
    pages = pdf.pages
    for page in pdf.pages:
        text = page.extract_text()
        for line in text.split('\n'):
            print(line)
            comp = company_re.search(line)
            if comp:
                vend_no, vend_name = comp.group(1), comp.group(2)

            elif line.startswith('INVOICES'):
                doctype = 'INVOICE'

            elif line.startswith('CREDITNOTES'):
                doctype = 'CREDITNOTE'

            elif line_re.search(line):
                items = line.split()
                lines.append(Line(vend_no, vend_name, doctype, *items))

            elif line.startswith('Supplier total'):
                tot = float(line.split()[2].replace(',', ''))
                total_check += tot
df = pd.DataFrame(lines)
df['inv_date'] = pd.to_datetime(df['inv_date'])
df['due_date'] = pd.to_datetime(df['due_date'])
for col in df.columns[-6:]:
    df[col] = df[col].map(lambda x: float(str(x).replace(',', '')))
st.dataframe(df)
st.markdown(get_table_download_link(df), unsafe_allow_html=True)

###############################################################################################################################################################
st.subheader("PDF-2")

second = Image.open('2.PNG')
st.image(second, use_column_width=500)

Line = namedtuple('Line', 'No Article Desc Quant UOM MRP BaseCost IGST_perc IGST_INR Total_Base HSN_SAC_Code Site')
line_re = re.compile(r'\d \d{2,}')
def numbify(num):
    return float(num.replace('$', '').replace(',', ''))
with pdfplumber.open("samp.pdf") as pdf:
    page = pdf.pages[0]
    text = page.extract_text(x_tolerance=2, y_tolerance=0)
    data = []

    with pdfplumber.open("samp.pdf") as pdf:
        page = pdf.pages[0]
        text = page.extract_text(x_tolerance=2, y_tolerance=0)

        for line in text.split('\n'):
            if line_re.search(line):
                in_lines = True
                no, article, *desc, quant, uom, mrp, basecost, igstp, igst_inr, total_base = line.split()
                desc = ' '.join(desc)
            elif line.startswith('Grand'):
                break
            elif re.match(r'\d{4}', line):
                hsn_code = line
            elif re.match(r'T\S{3}', line):
                site = line
                line_info = Line(no, article, desc, quant, uom, mrp, basecost, igstp, igst_inr, total_base, hsn_code,
                                 site)
                data.append(line_info)
df = pd.DataFrame(data)
df['Total_Base'] = df['Total_Base'].map(numbify)
df['IGST_INR'] = df['IGST_INR'].map(numbify)
st.dataframe(df)
st.markdown(get_table_download_link(df), unsafe_allow_html=True)


