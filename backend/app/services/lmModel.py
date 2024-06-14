import openai
import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOpenAI

# Load environment variables from .env file
load_dotenv()

# Ensure the API key is taken from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI()
llm = ChatOpenAI(api_key=openai.api_key, temperature=0.90, model_kwargs={"top_p": 0.9})

async def generate_gpt3(prompt: str):
    try:
        # Asynchronously call the OpenAI API if the SDK supports it. For now, it's a regular call.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.5
        )
        # Ensure response is successful and has content
        if response:
            return response.choices[0].message.content
        else:
            return "No valid response received."
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return "Error processing your request."
    

async def simple_rag(vectorstore_path:str, source_path: str):
    pdf_loader = PyPDFDirectoryLoader(source_path)
    docs = pdf_loader.load()

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=20)
    split_docs = text_splitter.split_documents(docs)

    embeddings = HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = FAISS.from_documents(
        documents=split_docs,
        embedding=embeddings,
    )

    vector_store.save_local(vectorstore_path)

    return vectorstore_path

async def simple_rag_query(vectorstore_path:str, prompt_template: ChatPromptTemplate,inputs: str):
    vector_store = FAISS.load_local(vectorstore_path, embeddings=HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"), allow_dangerous_deserialization=True )

    retriever = vector_store.as_retriever()

    rag_chain = (
        {'offer_context': retriever, 'customer_info': RunnablePassthrough()} 
        | prompt_template
        | llm
        | StrOutputParser()
    )

    response = rag_chain.invoke(str(inputs))

    return response

