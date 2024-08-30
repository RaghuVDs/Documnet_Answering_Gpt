import streamlit as st
from openai import OpenAI
from openai import AuthenticationError

st.set_page_config(layout="wide")

st.markdown(
    "<h1 style='text-align: center;'>📄 Document Question Answering</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>Upload a document and ask questions about it – GPT will answer!</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>To use this app, you need to provide an OpenAI API key, which you can get <a href='https://platform.openai.com/account/api-keys'>here</a>.</p>",
    unsafe_allow_html=True,
)


openai_api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key here")


if not openai_api_key:
    st.warning("Please add your OpenAI API key to continue.")
else:
    # created an OpenAI client to check if the key is valid
    try:
        client = OpenAI(api_key=openai_api_key)

        # Columns for better layout
        col1, col2 = st.columns([3, 1])

        # File uploader in the first column
        with col1:
            uploaded_file = st.file_uploader(
                "Upload a Document (.txt or .md)", type=("txt", "md")
            )

        # Question input and button in the second column
        with col2:
            question = st.text_area(
                "Ask a Question",
                placeholder="Can you give me a short summary?",
                height=150,  # Adjust height as needed
                disabled=not uploaded_file,
            )
            if st.button("Get Answer", disabled=not (uploaded_file and question)):
                # Process the file and question
                document = uploaded_file.read().decode()
                messages = [
                    {
                        "role": "user",
                        "content": f"Here's a document: {document} \n\n---\n\n {question}",
                    }
                ]

                # Generating the answers 
                with st.spinner("Generating answer..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",  # or any other suitable model
                        messages=messages
                    )

                    # Displaying the answer
                    st.write(response.choices[0].message.content) 

    except AuthenticationError:
        st.error("Invalid OpenAI API key. Please check your key and try again.")