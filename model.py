from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereEmbeddings
from langchain_cohere import ChatCohere
from langchain_cohere import CohereRerank, CohereRagRetriever
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import WebBaseLoader
import uuid

import os
from dotenv import load_dotenv

load_dotenv() 
api_key = os.getenv('COHERE_API_KEY')

# Define the Cohere LLM

SYSTEM_PROMPT = """You are a helpful AI model that can answer questions about research papers. 
                    You are connected to a vector store of research papers. 
                    Use this vector store to answer questions about the given research papers truthfully without making up any information. 
                    If you don't know the answer, you can say 'This information is out-of-scope of the provided research papers'. 
                    User may also provide you with an imaginary patient profile. 
                    Your job is to compare this patient profile with the research papers and determine which environmental factors affect the patient's epigenetics.
                    You must only use the provided database for your answers, but can use your own knowledge to fill in logic gaps to search for the answer in the database."""

db = None

def embed_knowledge(path):

    embeddings = CohereEmbeddings(cohere_api_key=api_key,
                              model="embed-english-light-v3.0")
    raw_documents = DirectoryLoader(path=path, glob="**/*.txt", loader_cls=TextLoader)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)

    # Create a vector store from the documents
    db = Chroma.from_documents(documents, embeddings)

    return db

def ground_knowledge(user_query):

    reranker = CohereRerank(cohere_api_key=api_key, 
                        model="rerank-english-v3.0")
    
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=db.as_retriever()
    )
    compressed_docs = compression_retriever.get_relevant_documents(user_query)
    return compressed_docs

def talk_to_llm():
    print('Starting the chat. Type "quit" to end.\n')
    
    while True:
    
        # User message
        message = input("User: ")
        
        # Typing "quit" ends the conversation
        if message.lower() == 'quit':
            print("Ending chat.")
            break

        llm = ChatCohere(cohere_api_key=api_key,              
                 model="command-r-plus-08-2024",
                 user_agent=uuid.uuid4().hex,
                 preamble=SYSTEM_PROMPT,
                 streaming=True,
                 verbose=False,
                 )
        
        # rag = CohereRagRetriever(llm=llm, connectors=[])
        # docs = rag.get_relevant_documents(
        #     message,
        #     documents=ground_knowledge(message))
        
        # answer = docs[-1].page_content
        # print(f"Answer: {answer} \n", end='')


        # print(f"Chatbot: {llm.invoke(message).content} {answer} \n", end='')
        print(f"Chatbot: {llm.invoke(message).content} \n", end='')

talk_to_llm()