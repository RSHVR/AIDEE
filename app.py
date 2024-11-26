import gradio as gr
from local_tools import compile_research as cr
from local_tools import pmc_scraper as ps
import os
import model as md

BASE_PATH = './'
SAVE_PATH = os.path.join(BASE_PATH, 'corpus/')
gr.set_static_paths(paths=[SAVE_PATH])

with gr.Blocks() as demo:
    research_paper_titles = gr.State([])
    with gr.Tab("Corpus"):
        with gr.Row():
            gr.Markdown("# Collect All Research Papers")
            
        with gr.Row():
            url = gr.Textbox(placeholder="Enter PMC URL", label="PMC URL", type="text", submit_btn=True)
            
            
            def collect_all_research_papers(url):
                scraper=ps.ArticleScraper(url)
                original_article=scraper.scrape_save()
                corpus_compiler=cr.ResearchCompiler(original_article)
                all_references=corpus_compiler.collect_references(original_article)
                corpus_compiler.compile_references(all_references)

            url.submit(collect_all_research_papers, [url], None)
        @gr.render(triggers=[url.submit])
        def display_corpus():
            display_corpus = cr.ResearchCompiler(SAVE_PATH)
            corpus=display_corpus.document_corpus()
            with gr.Row():
                with gr.Column():
                    gr.Files(value=[corpus.values], label="Dataset")
                with gr.Column():
                    gr.Markdown("## Article Content")
    with gr.Tab("Chatbot"):
        with gr.Row():
            gr.Markdown("# Query Research Papers")
        with gr.Row():
            gr.Chatbot(type="messages")
    with gr.Tab("Patient Profiles"):
        with gr.Row():
            gr.Markdown("# Patient Profiles")
        with gr.Row():
            gr.Dropdown(["Patient 1", "Patient 2", "Patient 3", "New Patient"], label="Patient Profiles")
        with gr.Row():
            age = gr.Number(value=19, label="Age", interactive=True, minimum=19, maximum=120, step=1, precision=0)
            hometown = gr.Textbox(placeholder="Enter Hometown", label="Hometown", interactive=True)
            ethnicity = gr.Dropdown(["European", "African", "East Asian", "South Asian", "Middle Eastern", "Native American", "Polynesian", "Aboriginal", "Indigineous/Metis", "Inuit", "Other"], label="Ethnicity", multiselect=True, interactive=True)
            sex = gr.Radio(choices=['Male', 'Female'], label = "Biological Sex", interactive=True)
            abuse = gr.Checkbox(value=None, label = "History of Abuse", interactive=True)
            pre_existing_conditions = gr.CheckboxGroup(choices=['Diabetes', 'Hypertension', 'Cancer', 'HIV/AIDS', 'Other'], label="Pre-existing Conditions", interactive=True)
            rec_drugs_used = gr.CheckboxGroup(choices=['Opioids', 'Cocaine', 'Marijuana', 'Methamphetamine', 'Other'], label="Recreational Drugs Used", interactive=True)
            household_products_used = gr.CheckboxGroup(choices=['Bleach', 'Ammonia', 'Hydrogen Peroxide', 'Other'], label="Household Products Used", interactive=True)
            mental_health = gr.CheckboxGroup(choices=['Depression', 'Anxiety', 'PTSD', 'Other'], label="Mental Health Diagnoses", interactive=True)
        with gr.Row():
            gr.TextArea(label = "Likely Environmental Factors based on Patient Profile", value = "placeholder")
        with gr.Row():
            gr.TextArea(label="Effects on Epigenetics", value = "placeholder")

demo.launch(allowed_paths=[SAVE_PATH])