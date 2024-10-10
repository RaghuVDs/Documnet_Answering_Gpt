import streamlit as st
from openai import OpenAI
from openai import AuthenticationError
from tiktoken import encoding_for_model
import uuid
import os

# Force the use of pysqlite3
import pysqlite3  
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
from chromadb.utils import embedding_functions
import PyPDF2

# Initialize ChromaDB client
client = chromadb.Client()


def create_vector_db():
    """
    Creates the ChromaDB collection if it doesn't exist in session state.
    """
    if "Lab4_vectorDB" not in st.session_state:
        folder_path = "Data/"  # Replace with your actual path

        try:
            if not os.path.exists(folder_path):
                raise FileNotFoundError(
                    f"Error: Folder '{folder_path}' not found. Please check the path and try again."
                )

            pdf_files = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.endswith(".pdf")
            ]

            # Use an appropriate OpenAI embedding model
            embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=st.secrets["api_key"],
                model_name="text-embedding-ada-002"
            )

            collection = client.create_collection(
                name="Lab4Collection",
                embedding_function=embedding_function
            )

            for pdf_file in pdf_files:
                with open(pdf_file, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    num_pages = len(pdf_reader.pages)
                    text = ""
                    for page_num in range(num_pages):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text()

                chunk_size = 500
                text_chunks = [
                    text[i: i + chunk_size] for i in range(0, len(text), chunk_size)
                ]
                collection.add(
                    documents=text_chunks,
                    metadatas=[{"source": pdf_file}] * len(text_chunks),
                    ids=[f"{pdf_file}_{i}" for i in range(len(text_chunks))],
                )

            st.session_state.Lab4_vectorDB = collection

        except (FileNotFoundError, IOError, PyPDF2.utils.PdfReadError) as e:
            st.error(f"Error loading or processing PDFs: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


def lab4():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("🤖 Chat with GPT about your PDFs")
    st.markdown(
        "Ask me anything about the PDFs I've been trained on! I can provide summaries, answer questions, and more."
    )

    openai_api_key = st.secrets["api_key"]
    if not openai_api_key:
        st.error(
            "OpenAI API key not found in secrets. "
            "Make sure you've added it to your Streamlit secrets file."
        )
        st.stop()

    try:
        client = OpenAI(api_key=openai_api_key)

        with st.sidebar:
            st.subheader("Model Options")
            use_advanced_model = st.checkbox("Use Advanced Model (gpt-4)")
            model_name = "gpt-4" if use_advanced_model else "gpt-3.5-turbo"
            encoding = encoding_for_model(model_name)

        create_vector_db()

        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input for questions
        if prompt := st.chat_input("You:"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get relevant context from ChromaDB
            collection = st.session_state.Lab4_vectorDB
            results = collection.query(
                query_texts=[prompt],
                n_results=3  # Get top 3 most relevant chunks
            )

            # Construct the context from retrieved chunks
            context = "\n".join(results['documents'][0])

            # Calculate token count for the new prompt
            new_prompt_tokens = len(encoding.encode(prompt))

            # Maintain a conversation buffer, limiting it to 'max_tokens'
            max_tokens = 3000  # Adjust this as needed
            conversation_buffer = []
            total_tokens = 0
            for message in reversed(st.session_state.messages):
                message_tokens = len(encoding.encode(message["content"]))
                if total_tokens + message_tokens > max_tokens:
                    break
                conversation_buffer.insert(0, message)
                total_tokens += message_tokens

            # Add system message and context tokens
            total_tokens += len(
                encoding.encode(
                    "You are a helpful AI assistant. Use the following context to answer the question: \n"
                    + context
                )
            )

            # Display token count information
            st.write(f"Total tokens used for this request: {total_tokens}")
            if total_tokens > max_tokens:
                st.warning(
                    f"Conversation buffer truncated to fit within {max_tokens} tokens."
                )

            # Construct the full message history for context
            messages_for_request = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Use the following context to answer the question: \n" + context
                }
            ] + conversation_buffer

            # Stream the response
            response_container = st.empty()
            full_response = ""
            for chunk in client.chat.completions.create(
                model=model_name, messages=messages_for_request, stream=True
            ):
                content = chunk.choices[0].delta.content or ""
                full_response += content
                response_container.markdown(full_response + "▌")
            response_container.markdown(full_response)

            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

            # ... (rest of your "More Information" logic)

    except AuthenticationError:
        st.error(
            "Invalid OpenAI API key. "
            "Please double-check your key and ensure it's correct."
        )
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    lab4()