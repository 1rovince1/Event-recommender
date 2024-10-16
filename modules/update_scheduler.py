import threading
import time

from engines import updation_engine as updater
from engines import search_engine as search
from utilities import similarity_weights as wconfig


# creating a thread lock mechanism to protect files while they are being updated
update_lock = threading.Lock()











# creating some global variables to be used in the APIs
retrieved_recommendable_events_info = None
retrieved_events_list = None
retrieved_indices = None




# we create an events_list to hold the data of the events that can be recommended
# this is done to easily get the response info to be sent to the front-end.
def update_events_list():

    with update_lock:

        global retrieved_recommendable_events_info
        retrieved_recommendable_events_info = updater.recommendable_events_info_list

        global events_list
        events_list = retrieved_recommendable_events_info

        global indices
        indices = {event['id']: i for i, event in enumerate(events_list)}











# function to update the content similarity matrix
def retrieve_event_data():

    event_data_retrieval_and_processing_start_time = time.time()

    try:

        updater.update_event_df()  # updating the events data
        event_data_retrieval_and_processing_end_time = time.time()
        print(f'Event data retrieved and processed successfully! ({(event_data_retrieval_and_processing_end_time - event_data_retrieval_and_processing_start_time):.6f} seconds)')

    except Exception as e:

        event_data_retrieval_and_processing_end_time = time.time()
        print(f'Failed to retrieve and process event data: {str(e)} ({(event_data_retrieval_and_processing_end_time - event_data_retrieval_and_processing_start_time):.6f} seconds)')




# function to update the content similarity matrix
def retrieve_user_order_data():

    user_order_data_retrieval_and_processing_start_time = time.time()

    try:

        updater.update_user_order_df()  # updating the user-order history data
        user_order_data_retrieval_and_processing_end_time = time.time()
        print(f'User-order history data retrieved successfully! ({(user_order_data_retrieval_and_processing_end_time - user_order_data_retrieval_and_processing_start_time):.6f} seconds)')

    except Exception as e:

        user_order_data_retrieval_and_processing_end_time = time.time()
        print(f'Failed to retrieve user-order history data: {str(e)} ({(user_order_data_retrieval_and_processing_end_time - user_order_data_retrieval_and_processing_start_time):.6f} seconds)')




# function to update the content similarity matrix
def update_content_similarity_matrix():

    content_based_updation_start_time = time.time()

    try:

        updater.update_content_recommendation_matrix(
            wconfig.weight_title_description_of_event,
            wconfig.weight_price_of_event,
            wconfig.weight_duration_of_event,
            wconfig.weight_venue_of_event,
            wconfig.weight_organizer_of_event,
            wconfig.weight_performer_of_event,
            wconfig.weight_date_of_event,
            wconfig.weight_time_of_event
        )  # updating the content recommendation matrix
        content_based_updation_end_time = time.time()
        print(f'Content based matrix updated successfully! ({(content_based_updation_end_time - content_based_updation_start_time):.6f} seconds)')

    except Exception as e:

        content_based_updation_end_time = time.time()
        print(f'Failed to update content similarity matrix: {str(e)} ({(content_based_updation_end_time - content_based_updation_start_time):.6f} seconds)')




# function to update user-item matrix
def update_user_item_matrix():

    user_item_update_start_time = time.time()

    try:

        updater.update_user_item_matrix()   # updating the user-item matrix
        user_item_update_end_time = time.time()
        print(f'User Item matrix updated successfully! ({(user_item_update_end_time - user_item_update_start_time):.6f} seconds)')

    except Exception as e:

        user_item_update_end_time = time.time()
        print(f'Failed to update user-item matrix: {str(e)} ({(user_item_update_end_time - user_item_update_start_time):.6f} seconds)')




# function to update events' info list
def update_events_info_list():

    events_list_update_start_time = time.time()

    try:

        update_events_list()    # updating the recommendable events list from the json file
        events_list_update_end_time = time.time()
        print(f"Upcoming published events' info list updated successfully! ({(events_list_update_end_time - events_list_update_start_time):.6f} seconds)")

    except Exception as e:

        events_list_update_end_time = time.time()
        print(f'Failed to update events\' info list: {str(e)} ({(events_list_update_end_time - events_list_update_start_time):.6f} seconds)')




# function to update semantic_search embeddings
def update_semantic_search_db():

    semantic_search_db_update_start_time = time.time()

    try:

        search.update_semantic_search_db()  # updating the embeddings in the sematntic_search db
        semantic_search_db_update_end_time = time.time()
        print(f'Semantic-search embeddings updated successfully! ({(semantic_search_db_update_end_time - semantic_search_db_update_start_time):.6f} seconds)')

    except Exception as e:

        semantic_search_db_update_end_time = time.time()
        print(f'Failed to update semantic-search embeddings: {str[e]} ({(semantic_search_db_update_end_time - semantic_search_db_update_start_time):.6f} seconds)')




# function to update memory of gemini with latest all-events' data
def update_gemini_memory():

    gemini_memory_update_start_time = time.time()

    try:

        search.update_gemini_memory()   # updating memory of llm to hold the latest events data
        gemini_memory_update_end_time = time.time()
        print(f'Memory of Gemini-LLM updated successfull! ({(gemini_memory_update_end_time - gemini_memory_update_start_time):.6f} seconds)')

    except Exception as e:

        gemini_memory_update_end_time = time.time()
        print(f'Failed to update memory of Gemini-LLM: {str(e)} ({(gemini_memory_update_end_time - gemini_memory_update_start_time):.6f} seconds)')




# handling periodic updates of the similarity matrix saved
def periodic_update():

    # calculating the time elapsed in updation
    updation_start_time = time.time()

    print('Updating recommendations...')

    retrieve_event_data()
    retrieve_user_order_data()
    update_content_similarity_matrix()
    update_user_item_matrix()
    update_events_info_list()
    update_semantic_search_db()
    update_gemini_memory()

    updation_end_time = time.time()
    print(f'Total time elapsed in updation = {(updation_end_time - updation_start_time):.6f} seconds')











# function to update the similarity matrix on custom weights
def customize_content_similarity_matrix(
        weight_title_description_of_event,
        weight_price_of_event,
        weight_duration_of_event,
        weight_venue_of_event,
        weight_organizer_of_event,
        weight_performer_of_event,
        weight_date_of_event,
        weight_time_of_event
):

    try:

        content_based_customization_start_time = time.time()
        updater.update_content_recommendation_matrix(
            weight_title_description_of_event,
            weight_price_of_event,
            weight_duration_of_event,
            weight_venue_of_event,
            weight_organizer_of_event,
            weight_performer_of_event,
            weight_date_of_event,
            weight_time_of_event
        )  # updating the content recommendation matrix
        content_based_customization_end_time = time.time()
        print(f'Content based matrix customized successfully! ({(content_based_customization_end_time - content_based_customization_start_time):.6f} seconds)')

        new_config = '\n'.join([
            "# adjustable weights:",
            "\n",
            f"weight_title_description_of_event = {weight_title_description_of_event}",
            f"weight_price_of_event = {weight_price_of_event}",
            f"weight_duration_of_event = {weight_duration_of_event}",
            f"weight_venue_of_event = {weight_venue_of_event}",
            f"weight_organizer_of_event = {weight_organizer_of_event}",
            f"weight_performer_of_event = {weight_performer_of_event}",
            f"weight_date_of_event = {weight_date_of_event}",
            f"weight_time_of_event = {weight_time_of_event}",

            "\n\n\n",
            "# default weights:",
            "\n",
            "# weight_title_description_of_event = 35.0",
            "# weight_price_of_event = 5.0",
            "# weight_duration_of_event = 2.5",
            "# weight_venue_of_event = 15.0",
            "# weight_organizer_of_event = 2.5",
            "# weight_performer_of_event = 25.0",
            "# weight_date_of_event = 7.5",
            "# weight_time_of_event = 7.5"
        ])

        with open('utilities/similarity_weights.py', 'w') as file:
            file.write(new_config)

        print('Updated the config file successfully!')

    except Exception as e:

        content_based_customization_end_time = time.time()
        print(f'Failed to customize content similarity matrix: {str(e)} ({(content_based_customization_end_time - content_based_customization_start_time):.6f} seconds)')