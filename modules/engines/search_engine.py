import numpy as np
import pickle
import os

from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from engines import updation_engine as updater
from utilities import utility_functions as utils











# MODEL LOADING AND CONFIGURATION

# fetching the sentence-transformer model
model_dir = 'models/'
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

model_path = os.path.join(model_dir, 'paraphrase-MiniLM-L6-v2.pkl')
# model_path = os.path.join(model_dir, 'paraphrase-mpnet-base-v2.pkl')

try:
    with open(model_path, 'rb') as file:
        lang_model = pickle.load(file)

except FileNotFoundError:
    lang_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    # lang_model = SentenceTransformer('paraphrase-mpnet-base-v2')

    with open(model_path, 'wb') as file:
        pickle.dump(lang_model, file)


# configuring gemini model
from dotenv import load_dotenv
load_dotenv(dotenv_path = 'utilities/.env')

api_key = os.environ['GOOGLE_API_KEY']

llm = GoogleGenerativeAI(
    model = 'gemini-1.5-flash',
    google_api_key = api_key,
    temperature = 0.9
)

prompt_template = PromptTemplate.from_template(
    """You are a recommendation system.
    You will be given a json format list with the data of all the available events.
    You will also be given a search query.
    The query would be a human input, so treat it as required.
    Your task is to give a json list of data of events that match the search query, in order of best recommendation to worst recommendation.
    Use your JSON-only format.
    Give upto 1 best matches.

    Query and data:
    Search query: {query}
    Events data: {event_data}"""
)

llm_chain = prompt_template | llm











# DB MANAGEMENT

embedded_descs = None

# db management for semantic search
def update_semantic_search_db():

    global embedded_descs
    embedded_descs = lang_model.encode(updater.retrieved_event_df['CombinedDescription'])



# we need to store the event data in memory of llm too at once
def update_gemini_memory():

    pass










# FUNCTIONALITIES


# function to give results based on sentence embeddings on CombinedDescription (title + description)
def semantic_search(query):

    response_dict = {}

    embedded_query = lang_model.encode(query)
    search_similarity_matrix = cosine_similarity(embedded_query[np.newaxis, :], embedded_descs)

    sorted_indices = np.argsort(search_similarity_matrix[0])[::-1]
    matching_events_list = updater.retrieved_event_df['id'].iloc[sorted_indices].tolist()

    matching_available_events_list = utils.event_availability(matching_events_list)

    response_dict['label'] = 'Events based on search query'
    response_dict['data'] = matching_available_events_list

    return response_dict





# function to invoke gemini api for search results
def gemini_search(query):
    
    return llm_chain.invoke({
        'query': query,
        'event_data': updater.recommendable_events_info_list
    })