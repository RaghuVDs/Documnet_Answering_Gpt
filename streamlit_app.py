import streamlit as st

# Define the pages using the new Streamlit navigation feature
pages = {
    "Lab 1": st.Page(lab1.py, title="Lab 1"),
    "Lab 2": st.Page(lab2.py, title="Lab 2")
}

# Pass the 'pages' dictionary to st.navigation
current_page = st.navigation(pages)

# Run the selected page
current_page.run() 
