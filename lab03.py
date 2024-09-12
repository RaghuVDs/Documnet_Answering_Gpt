import streamlit as st
from openai import OpenAI
from openai import AuthenticationError
import PyPDF2

# Function to read PDF files
def read_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def lab3():
    # Initialize chat history if not present in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Title and description
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

    # API key handling
    openai_api_key = st.secrets["api_key"]
    if not openai_api_key:
        st.error("OpenAI API key not found in secrets.")
        st.stop()

    try:
        client = OpenAI(api_key=openai_api_key)

        # Sidebar with summary options and model choice
        with st.sidebar:
            st.subheader("Summary Options")
            summary_option = st.radio(
                "Choose summary type:",
                ("100 words", "2 paragraphs", "5 bullet points")
            )
            use_advanced_model = st.checkbox("Use Advanced Model (gpt-4o)")
            model_name = "gpt-4o" if use_advanced_model else "gpt-4o-mini"

        # File uploader
        uploaded_file = st.file_uploader(
            "Upload a Document (.txt, .md, or .pdf)", type=("txt", "md", "pdf")
        )

        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input for questions or document upload
        if prompt := st.chat_input("You:"):
            # If a document is not uploaded yet and the user types something,
            # assume it's a question about the app itself
            if 'document' not in st.session_state:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant for a document Q&A app."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
                with st.chat_message("assistant"):
                    st.markdown(response.choices[0].message.content)
            else:  # Document is uploaded, process the question
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Construct the prompt for the LLM, including only the last two messages
                context_messages = st.session_state.messages[-3:]  # Include the previous assistant's response for context
                messages = [
                    {"role": "system", "content": f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {st.session_state['document']}"}
                ] + context_messages 

                # Generate the answer with streaming
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for response in client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        stream=True  # Enable streaming
                    ):
                        full_response += response.choices[0].delta.get("content", "")
                        message_placeholder.markdown(full_response)  # Update the placeholder with the accumulated response
                    message_placeholder.markdown(full_response)  # Finalize the response 

                # Keep only the last two messages in the history
                st.session_state.messages = st.session_state.messages[-2:]

        elif uploaded_file and st.button("Process Document"):  # Handle document upload
            try:
                # Process the file
                if uploaded_file.type == "application/pdf":
                    document = read_pdf(uploaded_file)
                else:
                    document = uploaded_file.read().decode("utf-8")

                st.session_state['document'] = document
                st.success("File processed successfully! You can now ask questions about it.")

            except UnicodeDecodeError:
                try:
                    document = uploaded_file.read().decode("latin-1")
                    st.session_state['document'] = document
                    st.success("File processed successfully! You can now ask questions about it.")
                except UnicodeDecodeError:
                    st.error("Error decoding file. Please ensure the file is in UTF-8 or Latin-1 encoding.")
            except Exception as e:
                st.exception(e)

    except AuthenticationError:
        st.error("Invalid OpenAI API key. Please check your key and try again.")