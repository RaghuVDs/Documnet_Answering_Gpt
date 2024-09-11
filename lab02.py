import streamlit as st
from openai import OpenAI
from openai import AuthenticationError

def lab2():
        
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
                "Upload a Document (.txt or .md  or .pdf)", type=("txt", "md","pdf")
            )

            if uploaded_file and st.button("Generate Summary"):
                # Process the file
                document = uploaded_file.read().decode()

                # Construct prompt based on selected summary option
                if summary_option == "100 words":
                    prompt = f"Summarize the following document in 100 words:\n\n{document}"
                elif summary_option == "2 paragraphs":
                    prompt = f"Summarize the following document in 2 connecting paragraphs:\n\n{document}"
                else:  # 5 bullet points
                    prompt = f"Summarize the following document in 5 bullet points:\n\n{document}"

                # Generates summary
                with st.spinner("Generating summary..."):
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )

                # Displays the summary
                st.subheader("Summary")
                st.write(response.choices[0].message.content)

        except AuthenticationError:
            st.error("Invalid OpenAI API key. Please check your key and try again.")
