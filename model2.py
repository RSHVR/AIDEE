import uuid
import gradio as gr
from langchain_cohere import ChatCohere, CohereEmbeddings, CohereRerank, CohereCitation, CohereRagRetriever
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.retrievers import ContextualCompressionRetriever


class ResearchPaperChatbot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.SYSTEM_PROMPT = """You are a helpful AI model that can answer questions about research papers. 
        You are connected to a vector store of research papers. 
        Use this vector store to answer questions about the given research papers truthfully without making up any information. 
        If you don't know the answer, you can say 'This information is out-of-scope of the provided research papers'. 
        User may also provide you with an imaginary patient profile. 
        Your job is to compare this patient profile with the research papers and determine which environmental factors affect the patient's epigenetics.
        You must only use the provided database for your answers, but can use your own knowledge to fill in logic gaps to search for the answer in the database."""
        
        self.chat_history = []
        self.uuid = uuid.uuid4().hex

    def append_chat_history(self, role, message):
        """Append a new message to the chat history."""
        self.chat_history.append({"role": role, "content": message})

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

    def talk_to_llm(self, message, history):
        try:
            llm = ChatCohere(
                cohere_api_key=self.api_key,              
                model="command-r-plus-08-2024",
                user_agent=self.uuid,
                preamble=self.SYSTEM_PROMPT,
                streaming=True,
                verbose=False,
            )
            
            # Prepare LLM messages
            llm_messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
            for msg in history:
                llm_messages.append({"role": msg["role"], "content": msg["content"]})
            
            llm_messages.append({"role": "user", "content": message})
            response = llm.invoke(llm_messages).content
            
            # Return updated history
            yield "", history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
        
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            yield "", history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": error_message}
            ]

    def rag_bot(self, message, history):
        try:
            # Initialize LLM
            llm = ChatCohere(
                cohere_api_key=self.api_key,
                model="command-r-plus-08-2024",
                user_agent=self.uuid,
                preamble=self.SYSTEM_PROMPT,
                streaming=True,
                verbose=False,
            )

            # Initialize RAG Retriever
            rag = CohereRagRetriever(
                llm=llm,
                connectors=[]  # Configure connectors to your vector store or data source
            )
            
            # Fetch relevant documents
            relevant_docs = rag.get_relevant_documents(
                query=message,
                documents=self.ground_knowledge(message)  # Define ground_knowledge function separately
            )
            
            # Combine retrieved documents into context
            doc_context = "\n\n".join([doc.page_content for doc in relevant_docs])
            extended_prompt = f"{self.SYSTEM_PROMPT}\n\nRelevant Context:\n{doc_context}"

            # Prepare LLM messages
            llm_messages = [{"role": "system", "content": extended_prompt}]
            for msg in history:
                llm_messages.append({"role": msg["role"], "content": msg["content"]})
            
            llm_messages.append({"role": "user", "content": message})
            
            # Invoke LLM
            response = llm.invoke(llm_messages).content
            
            # Stream response updates
            yield "", history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
        
        except Exception as e:
            # Handle errors gracefully
            error_message = f"An error occurred: {str(e)}"
            yield "", history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": error_message}
            ]


def create_chatbot_interface(api_key):
    """Create Gradio interface for the chatbot."""
    chatbot_instance = ResearchPaperChatbot(api_key)

    with gr.Tab("Chatbot"):
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("# Query Research Papers")
                with gr.Group():
                    chatbot = gr.Chatbot(type="messages", show_copy_all_button=True)
                    msg = gr.Textbox(label="Enter your message", interactive=True)
            with gr.Column(scale=1):
                with gr.Group():
                    clear = gr.Button("Clear Chat")
                    toggle_mode = gr.Radio(
                        choices=["Standard Chat", "RAG-enabled Chat"], 
                        value="Standard Chat", 
                        label="Select Chat Mode"
                    )
        
        def process_message(message, history, mode):
            """Determines which chatbot functionality to use based on mode."""
            if mode == "Standard Chat":
                return "", chatbot_instance.talk_to_llm(message, history)
            else:  # RAG-enabled Chat
                return "", chatbot_instance.rag_bot(message, history)

        # # Submit message event
        # msg_submit = msg.submit(
        #     fn=process_message,
        #     inputs=[msg, chatbot, toggle_mode],
        #     outputs=[msg, chatbot]
        # )

        msg_submit = msg.submit(
            fn=chatbot_instance.talk_to_llm,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )

        # Clear chat functionality
        clear.click(
            fn=lambda: None, 
            inputs=None, 
            outputs=[msg, chatbot]
        )

    return chatbot

# Usage would be:
# interface = create_chatbot_interface(your_api_key)
# interface.launch()