import streamlit as st
from lab1 import lab1 
from lab2 import lab2  

pages = [
    st.Page(lab1, title="Lab 1"),
    st.Page(lab2, title="Lab 2")
]

pg = st.navigation(pages, position="sidebar")

pg.run()
