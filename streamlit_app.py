import streamlit as st
from lab01 import lab1 
from lab02 import lab2 

with st.sidebar:
    selected_page = st.radio("Select a page", ["Lab 1", "Lab 2"])

# Display the selected page
if selected_page == "Lab 1":
    lab1()
elif selected_page == "Lab 2":
    lab2()