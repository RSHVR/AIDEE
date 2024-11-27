import gradio as gr
from local_tools import compile_research as cr
from local_tools import pmc_scraper as ps
import os
# import model as md
from langchain_cohere import ChatCohere
import model2 as md


import uuid
from dotenv import load_dotenv

BASE_PATH = './'
SAVE_PATH = os.path.join(BASE_PATH, 'corpus/')
gr.set_static_paths(paths=[SAVE_PATH])
load_dotenv() 
api_key = os.getenv('COHERE_API_KEY')
app_description = """# AIDEE: Auto-Immune Diseases and Environmental effects on underlying Epigenetics
                    AIDEE allows you to collect research papers from PMC and query their knowledge using a chatbot.
                    Furthermore, it also allows you to input patient profiles to determine the likely environmental factors that affect the patient's epigenetics in a more quantitative manner. 
                    This app is powered by Cohere's Command-R model and the Langchain library.\n
                    <sub>pronounced 'addy'</sub> """

with gr.Blocks() as demo:
    research_paper_titles = gr.State([])
    with gr.Tab("Corpus"):
        with gr.Row():
            gr.Markdown(app_description)
        with gr.Row():
            with gr.Column():
                # api = gr.Textbox(placeholder="Enter API Key", label="Cohere API Key", type="password", submit_btn=True)
                gr.Markdown("# Collect All Research Papers")
                pass
            with gr.Column():
                url = gr.Textbox(placeholder="Enter PMC URL", label="PMC URL", type="text", submit_btn=True)
            
            
            def collect_all_research_papers(url):
                scraper=ps.ArticleScraper(url)
                original_article=scraper.scrape_save()
                corpus_compiler=cr.ResearchCompiler(original_article)
                all_references=corpus_compiler.collect_references(original_article)
                corpus_compiler.compile_references(all_references)

            url.submit(collect_all_research_papers, [url], None).then
        @gr.render(triggers=[url.submit])
        def display_corpus():
            display_corpus = cr.ResearchCompiler(SAVE_PATH)
            corpus=display_corpus.document_corpus()
            with gr.Row():
                with gr.Column():
                    gr.Files(value=[corpus.values], label="Dataset")
                with gr.Column():
                    gr.Markdown("## Article Content")
    
    chatbot_tab = md.create_chatbot_interface(api_key)
    # with gr.Tab("Chatbot"):
    #     with gr.Row():
    #         gr.Markdown("# Query Research Papers")
    #     with gr.Row():
    #         with gr.Group():
    #             chatbot = gr.Chatbot(type="messages")
    #             msg = gr.Textbox(interactive=True, submit_btn=True)
    #             uuid_state = gr.State(uuid.uuid4().hex)  # Initialize UUID state
    #             last_response = gr.State("")  # Store the last LLM response
    #             chat_history = []
    #             SYSTEM_PROMPT = """You are a helpful AI model that can answer questions about research papers. 
    #                     You are connected to a vector store of research papers. 
    #                     Use this vector store to answer questions about the given research papers truthfully without making up any information. 
    #                     If you don't know the answer, you can say 'This information is out-of-scope of the provided research papers'. 
    #                     User may also provide you with an imaginary patient profile. 
    #                     Your job is to compare this patient profile with the research papers and determine which environmental factors affect the patient's epigenetics.
    #                     You must only use the provided database for your answers, but can use your own knowledge to fill in logic gaps to search for the answer in the database."""
                    
    #             def display_chat_history(chat_history):
    #                 return chat_history
                
    #             def append_chat_history(role,message):
    #                 chat_history.append(f"role: {role}, content: {message}")
    #                 return chat_history
                
    #             def talk_to_llm(message, chat_history):
    #                 print('Starting the chat. Type "quit" to end.\n')
                    
    #                 append_chat_history("User", message)
    #                 # User message
    #                 message = chat_history + [f"User: {message} \n"]

                    
    #                 llm = ChatCohere(cohere_api_key=api_key,              
    #                         model="command-r-plus-08-2024",
    #                         user_agent=uuid.uuid4().hex,
    #                         preamble=SYSTEM_PROMPT,
    #                         streaming=True,
    #                         verbose=False,
    #                         )
                    
    #                 response = llm.invoke(message).content
            
    #                 append_chat_history("Chatbot", response)

    #                 yield response, chat_history

    #             msg.submit(talk_to_llm, [msg, chatbot], [last_response, chatbot]) #.then(display_chat_history, [chatbot], [chatbot])
                

    with gr.Tab("Patient Profiles"):
        with gr.Row():
            gr.Markdown("# Patient Profiles")
        with gr.Row():
            gr.Dropdown(["Patient 1", "Patient 2", "Patient 3", "New Patient"], label="Patient Profiles")
        with gr.Row():
            with gr.Column():
                age = gr.Number(value=19, label="Age", interactive=True, minimum=19, maximum=120, step=1, precision=0)
                hometown = gr.Textbox(placeholder="Enter Hometown", label="Hometown", interactive=True)
                ethnicity = gr.Dropdown(["European", "African", "East Asian", "South Asian", "Middle Eastern", "Native American", "Polynesian", "Aboriginal", "Indigineous/Metis", "Inuit", "Other"], label="Ethnicity", multiselect=True, interactive=True)
                sex = gr.Radio(choices=['Male', 'Female'], label = "Sex at Birth", interactive=True)
                abuse = gr.Checkbox(value=None, label = "History of Abuse", interactive=True)
            pre_existing_conditions = gr.CheckboxGroup(choices=['Diabetes', 'Hypertension', 'Cancer', 'HIV/AIDS', 'Other'], label="Pre-existing Conditions", interactive=True)
            rec_drugs_used = gr.CheckboxGroup(choices=['Opioids', 'Cocaine', 'Marijuana', 'Methamphetamine', 'Other'], label="Recreational Drugs Used", interactive=True)
            household_products_used = gr.CheckboxGroup(choices=['Bleach', 'Dish Soap', 'Floor Cleaner', 'Disinfectant', 'Other'], label="Household Products Used", interactive=True)
            mental_health = gr.CheckboxGroup(choices=['Depression', 'Anxiety', 'PTSD', 'Other'], label="Mental Health Diagnoses", interactive=True)
        with gr.Column():
            with gr.Row():
                gr.TextArea(label = "Likely Environmental Factors based on Patient Profile", value = "placeholder")
            with gr.Row():
                gr.TextArea(label="Effects on Epigenetics", value = "placeholder")

demo.launch(allowed_paths=[SAVE_PATH])