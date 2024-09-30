import streamlit as st
from lab01 import lab1 
from lab02 import lab2 
from lab03 import lab3
from lab04 import lab4


with st.sidebar:
    selected_page = st.radio("Select a page", ["Lab 1", "Lab 2", "Lab 3","Lab 4"])

# Display the selected page
if selected_page == "Lab 1":
    lab1()
elif selected_page == "Lab 2":
    lab2()
elif selected_page == "Lab 3":
    lab3()
elif selected_page == "Lab 4":
    lab4()
    