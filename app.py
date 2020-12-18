import streamlit as st
import tabula
import webbrowser

### Upload a dataset.
st.header("Upload your PDF file")
data_file = st.file_uploader("Upload pdf", type=['pdf'])
st.set_option('deprecation.showfileUploaderEncoding', False)
if data_file is not None:
    file_details = {"Filename": data_file.name, "FileType": data_file.type, "FileSize": data_file.size}
    st.write(file_details)
    dfs = tabula.read_pdf(data_file, pages="all", stream=True)
    a = len(dfs)
    for i in range(a):
        st.dataframe(dfs[i])






