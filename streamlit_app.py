AI APP  - HW1

Deep Chandreshbhai Patoliya
​
Raghuveera Narasimha
​
import streamlit as st
from lab1 import lab1
from lab2 import lab2

pg = st.navigation([
    st.Page(lab2, title = "Lab 2"),
    st.Page(lab1, title = "Lab 1")
], position = "sidebar")


pg.run()
