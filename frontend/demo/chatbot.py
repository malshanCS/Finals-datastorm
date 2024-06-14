import streamlit as st
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from pathlib import Path
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Set up Streamlit app
st.title("Your Virtual Assistant")

# Initialize OpenAI client

# Session state for messages and OpenAI model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Set up LangChain OpenAI client for RAG
    langchain_client = ChatOpenAI(api_key='sk-proj-tiF6IMRa0jWHMbLr759UT3BlbkFJGxs97SwfOLb4VvvtxvVT', streaming=True,temperature=0.3, model_kwargs={"top_p": 0.9})

    # check if vectorstore exists



    # Define paths and model names
    vectorstore_path = Path("/Users/vihidun/Desktop/Finals_Datastorm_5/Finals-datastorm/frontend/demo/vector_stores/promotional_texts")

    # Check if the vector store directory exists
    if vectorstore_path.exists():
        # Load the existing vector store
        embedding = HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore_x = FAISS.load_local(
            folder_path=str(vectorstore_path),
            embeddings=embedding,
            allow_dangerous_deserialization=True
        )
    else:
        # Load and process the documents
        loader = PyPDFDirectoryLoader('/Users/vihidun/Desktop/Finals_Datastorm_5/Finals-datastorm/frontend/demo/promotional_text')
        docs = loader.load()

        embedding = HuggingFaceBgeEmbeddings(model_name='')
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        doc_chunks = text_splitter.split_documents(docs)

        # Create the vector store
        vectorstore_x = FAISS.from_documents(
            documents=doc_chunks,
            embedding=embedding,
        )

        # Save the vector store
        vectorstore_x.save_local(str(vectorstore_path))

    # Create the retriever
    retriever = vectorstore_x.as_retriever()

    # Create the prompt template
    template = """You are an virtual assistant chatbot who uses a knowledge base with promotional texts with product available in the store. Refer the below context for the knowledge base.
    {context}
    Question: {question}
    Here are the tasks you should be able to perform:
    1. Creating recipes based on the food products available in the store.
    2. Generating promotional content for the products available in the store. (refer example promotions from the knowledge base and customize them for products available in the store)
    3. Providing information about the products available in the store.
     

    """
    prompt_template = ChatPromptTemplate.from_template(template)

    # Set up memory
    memory = ConversationSummaryMemory(
        llm=langchain_client, memory_key="chat_history", return_messages=True
    )

    # Set up the ConversationalRetrievalChain
    qa = ConversationalRetrievalChain.from_llm(
        langchain_client, 
        retriever=retriever, 
        memory=memory, 
        combine_docs_chain_kwargs={"prompt": prompt_template}
    )

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt_template
        | langchain_client
        | StrOutputParser()
    )
    details = rag_chain.stream(prompt)

    # Get the response from the RAG model
    # response = qa.call({"question": prompt, "chat_history": st.session_state.messages})

    with st.chat_message("assistant"):
        response = st.write_stream(details)

    st.session_state.messages.append({"role": "assistant", "content": response})