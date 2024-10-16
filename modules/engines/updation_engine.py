import threading
# import string
import os

import pickle
import requests
import numpy as np
import pandas as pd
from pandas import json_normalize
from sklearn.preprocessing import OneHotEncoder
# from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
# from nltk.stem import WordNetLemmatizer
# from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from currency_converter import CurrencyConverter

from utilities import links


# Download stopwords and other necessary corpora if you haven't done so (For first time use. Run the nltk_downloader.py file in the terminal to perform this action)
# nltk.download('stopwords')  
# nltk.download('wordnet')  # For lemmatizer
# nltk.download('omw-1.4')  # For lemmatizer if needed


# API urls to be used
events_data_url = links.events_data_url # API endpoint to get events data
users_data_url = links.users_data_url   # API endpoint to get the uesr-order-history data


# creating a thread lock mechanism to protect files while they are being updated
update_lock = threading.Lock()


# setting some nltk initialisers and variables
# stopwords_eng = set(stopwords.words("english"))
# punct = set(string.punctuation)
# lemma = WordNetLemmatizer()


# fetching the sentence-transformer model
model_dir = 'models/'
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# model_path = os.path.join(model_dir, 'paraphrase-MiniLM-L6-v2.pkl')
# model_path = os.path.join(model_dir, 'paraphrase-mpnet-base-v2.pkl')
model_path = os.path.join(model_dir, 'all-mpnet-base-v2.pkl')

try:
    with open(model_path, 'rb') as file:
        lang_model = pickle.load(file)

except FileNotFoundError:
    # lang_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    # lang_model = SentenceTransformer('paraphrase-mpnet-base-v2')
    lang_model = SentenceTransformer('all-mpnet-base-v2')

    with open(model_path, 'wb') as file:
        pickle.dump(lang_model, file)



# some global variables to be kept in-memory
retrieved_combined_content_similarity_df = None # dataframe format of the combined content-similarity matrix
retrieved_item_similarity_df = None # dataframe format of the combined item-similarity matrix
retrieved_user_item_matrix_df = None    # dataframe format of the user-item matrix
retrieved_event_df = None   # dataframe that holds the data of all the events
retrieved_user_order_df = None    # dataframe that holds the data of past orders
retrieved_recommendable_events_list = None # a list that holds the event ids of the events that can be recommended
recommendable_events_info_list = None   # a list containing all the event data in the json respose format for each event












# DATA COLLECTION AND HELPER FUNCTIONS

# function to perform text pre-processing
# def clean(document):
  
#   stopwords_removed = ' '.join([i for i in document.lower().split() if i not in stopwords_eng])   # removing stopwords
#   punctuations_removed = ''.join(ch for ch in stopwords_removed if ch not in punct)   # removing punctuations
#   normalized = ' '.join(lemma.lemmatize(word) for word in punctuations_removed.split())   # converting words to their root form
#   return normalized




# function to update the in-memory dataframe of all the events
def update_event_df():

    # getting data of all events from the events_data_url
    response = requests.get(events_data_url)
    if response.status_code == 200:
        json_obj = response.json()
    else:
        error_message = "error: " + str(response.status_code)
        return error_message

    # df = json_normalize(json_obj['data']).rename(columns={'base_price': 'price','organizer_id': 'organizerId', 'performer_id': 'performerId', 'start_date_time': 'startDateTime', 'end_date_time': 'endDateTime', 'venue.city_id': 'venue.cityId', 'venue.state_id': 'venue.stateId', 'venue.country_id': 'venue.country' })    
    df = json_normalize(json_obj['data']) # converting the complex json data format to a simpler tabular format
    event_df = df[['id', 'title', 'description', 'price', 'currency', 'status', 'organizerId', 'performerId', 'startDateTime', 'endDateTime', 'venue.cityId', 'venue.stateId', 'venue.country']].copy()
    event_df = event_df.dropna() # removing any event that has these values as null (not possible, but kept to avoid unwanted errors)
    event_df = event_df[event_df['status'] == "Published"]
    # event_df = event_df[event_df['status'] == 1]

    # editing df
    # event_df['CombinedDescription'] = ((event_df['title'] + ' ') + event_df['description']).apply(lambda x: clean(x))    # CombinedDescription column holds the title and description words (preprocessed using clean function)
    event_df['CombinedDescription'] = ((event_df['title'] + '. ') + event_df['description'])    # No need to clean text now, as we are using a embedding model
    # event_df['CombinedDescription'] = (event_df['description'])    # Not using title as of now beacause it biased towards titles having years like 2024, 2025 etc.

    # converting the datetime columns to datetime format
    event_df['startDateTime'] = pd.to_datetime(event_df['startDateTime'])
    event_df['endDateTime'] = pd.to_datetime(event_df['endDateTime'])
    event_df['Duration'] = (event_df['endDateTime'] - event_df['startDateTime']).dt.total_seconds() / 3600  # Duration column hold the length of the event

    current_utc_datetime = pd.to_datetime('now', utc=True)
    # current_utc_datetime = pd.to_datetime('now')
    event_df['Upcoming'] = (event_df['startDateTime'] - current_utc_datetime)  # Upcoming column hold the time duration which is left before the startDateTime of event arrives

    # converting currencies to a standard value for comparison (INR)
    currconv = CurrencyConverter()
    event_df['priceINR'] = event_df.apply(lambda item: currconv.convert(item['price'], item['currency'], 'INR'), axis=1)
    
    # creating and saving a list of the events that can be recommended (only the events in the future are saved in this list)
    recommendable_events_list = event_df['id'][event_df['startDateTime'] > current_utc_datetime].tolist()

    # extracting the info of the events that can be recommended, in the json format to be saved and returned as response when required
    recommendable_json_obj = [event_info for event_info in json_obj['data'] if event_info['id'] in recommendable_events_list]

    # saving the new calculations to the global variables and the json file
    with update_lock:

        global retrieved_event_df
        retrieved_event_df = event_df

        global retrieved_recommendable_events_list
        retrieved_recommendable_events_list = recommendable_events_list

        global recommendable_events_info_list
        recommendable_events_info_list = recommendable_json_obj




# function to update the in-memory dataframe holding the data of past orders
def update_user_order_df():

    # getting response from the past order details of users
    response = requests.get(users_data_url)
    if response.status_code == 200:
        user_json_obj = response.json()
    else:
        error_message = "error: " + str(response.status_code)
        return error_message
    
    user_order_df = pd.DataFrame(user_json_obj)

    with update_lock:

        global retrieved_user_order_df
        retrieved_user_order_df = user_order_df




# function to get title and description similarity matrix
def title_desc_similarity():

    # using tfidf to calculate similarity among events based on the combined description
    # we can improve recommendations by using more advanced models like word embeddings, BERT etc., in future, which will be able to understand the meaning of the title and description
    # tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0.0, stop_words='english')
    # tfidf_matrix = tfidf.fit_transform(retrieved_event_df['CombinedDescription'])
    # desc_similarity_matrix = linear_kernel(tfidf_matrix, tfidf_matrix)

    # using embedding model (sentence-transformer) instead of simple tfidf to improve similarity based on description
    global lang_model
    embedded_descs = lang_model.encode(retrieved_event_df['CombinedDescription'])
    desc_similarity_matrix = cosine_similarity(embedded_descs, embedded_descs)

    return desc_similarity_matrix




# function to get price similarity matrix
def price_similarity():

    price_arr = np.array(retrieved_event_df['priceINR'])
    num_prices = len(price_arr)
    price_similarity_matrix = np.zeros((num_prices, num_prices))

    min_price = np.min(price_arr)
    max_price = np.max(price_arr)
    diff_price_min_max = max_price - min_price

    for i in range(num_prices):
        for j in range(i, num_prices):
            diff = abs(price_arr[i] - price_arr[j]) # calculating the absoute difference b/w the price of 2 events
            norm_val = 1 - (diff / (diff_price_min_max))    # normalizing the absolute difference
            price_similarity_matrix [i, j] = price_similarity_matrix [j, i] = norm_val

    return price_similarity_matrix




#function to get duration similarity matrix
def duration_similarity():

    duration_arr = np.array(retrieved_event_df['Duration'])
    num_durations = len(duration_arr)
    duration_similarity_matrix = np.zeros((num_durations, num_durations))

    min_duration = np.min(duration_arr)
    max_duration = np.max(duration_arr)
    diff_duration_min_max = max_duration - min_duration

    for i in range(num_durations):
        for j in range(i, num_durations):
            diff = abs(duration_arr[i] - duration_arr[j])   # calculating the abslute difference in durations of 2 events
            norm_val = 1 - (diff / diff_duration_min_max)   # normalizing the absolute difference
            duration_similarity_matrix [i, j] = duration_similarity_matrix [j, i] = norm_val
    
    return duration_similarity_matrix




# function to get venue similarity matrix
def venue_similarity():

    ohenc = OneHotEncoder()

    city_encoded = ohenc.fit_transform(retrieved_event_df[['venue.cityId']])  # encoding the city values
    state_encoded = ohenc.fit_transform(retrieved_event_df[['venue.stateId']])    # encoding the state values
    country_encoded = ohenc.fit_transform(retrieved_event_df[['venue.country']])    # encoding the country values

    # cosine_similarites for venue components
    venue_city_similarity = linear_kernel(city_encoded, city_encoded)   # matrix representing similarity in city
    venue_state_similarity = linear_kernel(state_encoded, state_encoded)    # matrix representing similarity in state
    venue_country_similarity = linear_kernel(country_encoded, country_encoded)  # matrix representing similarity in country

    weight_country = 0.75
    weight_state = 0.20
    weight_city = 0.05

    venue_similarity_matrix = (
        (weight_country * venue_country_similarity) + 
        (weight_state * venue_state_similarity) +
        (weight_city * venue_city_similarity)
    )

    return venue_similarity_matrix




# function to get organizer similarity matrix
def organizer_similarity():

    ohenc = OneHotEncoder()

    organizer_encoded = ohenc.fit_transform(retrieved_event_df[['organizerId']])    # encoding the organizer ids

    organizer_similarity_matrix = linear_kernel(organizer_encoded)  # matrix representing similarity in organizer

    return organizer_similarity_matrix




# function to get performer similarity matrix (based on performerId)
def performer_similarity():

    ohenc = OneHotEncoder()

    performer_encoded = ohenc.fit_transform(retrieved_event_df[['performerId']])    # encoding the organizer ids

    performer_similarity_matrix = linear_kernel(performer_encoded)  # matrix representing similarity in organizer

    return performer_similarity_matrix




# function to get date similarity
def date_similarity():
    
    dates = retrieved_event_df['startDateTime']
    
    num_dates = len(dates)
    date_similarity_matrix = np.zeros((num_dates, num_dates))
    
    min_date = dates.min()
    max_date = dates.max()
    diff_date_min_max = (max_date - min_date).days
    
    if(diff_date_min_max == 0.0):
        diff_date_min_max = 1.0 

    for i in range(num_dates):
        for j in range(i, num_dates):
            diff = abs(dates.iloc[i] - dates.iloc[j]).days
            norm_val = 1 - (diff / (diff_date_min_max))
            date_similarity_matrix [i, j] = date_similarity_matrix [j, i] = norm_val
                            
    return date_similarity_matrix




# function to get time(hour) similarity
def time_similarity():
    
    hour_arr = np.array(retrieved_event_df['startDateTime'].dt.hour)
    
    num_times = len(hour_arr)
    hour_similarity_matrix = np.zeros((num_times, num_times))
            
    for i in range(num_times):
        for j in range(i, num_times):
            diff = abs(hour_arr[i] - hour_arr[j])
            norm_val = 1 - (diff / 23.0)
            hour_similarity_matrix [i, j] = hour_similarity_matrix [j, i] = norm_val
                            
    return hour_similarity_matrix











# CRAETION OF MATRICES AND THEIR UPDATION

# function to create a new similartiy matrix from the all-events api response
# in future we can use the separate similarity matrices which comprise of the combined_content_similarity matrix to provide recommendations based on user-criteria
# for this purpose, we can either use the separate matrices for separate use-cases, and combine the results as per requirements
# for eg, if user wants 'food' events with price of around '500', we can comine the description and price similarities (w.r.t user-entered values) separately for this purpose,
# and either assign the weights to other criterias (if we want other criterias to weigh-in by default) based on some calculation, or leave them out completely
def update_content_recommendation_matrix(
        weight_title_description_of_event,
        weight_price_of_event,
        weight_duration_of_event,
        weight_venue_of_event,
        weight_organizer_of_event,
        weight_performer_of_event,
        weight_date_of_event,
        weight_time_of_event
):

    #calculation of new similarity matrix
    title_desc_similarity_matrix = title_desc_similarity()
    price_similarity_matrix = price_similarity()
    duration_similarity_matrix = duration_similarity()
    venue_similarity_matrix = venue_similarity()
    organizer_similarity_matrix = organizer_similarity()
    performer_similarity_matrix = performer_similarity()
    date_similarity_matrix = date_similarity()
    time_similarity_matrix = time_similarity()
    # these different types of similarities can also be used separately in future

    # configurable weights
    total_weight = (
        weight_title_description_of_event +
        weight_price_of_event +
        weight_duration_of_event +
        weight_venue_of_event +
        weight_organizer_of_event +
        weight_performer_of_event +
        weight_date_of_event +
        weight_time_of_event
    )

    weight_desc = weight_title_description_of_event / total_weight
    weight_price = weight_price_of_event / total_weight
    weight_duration = weight_duration_of_event / total_weight
    weight_venue = weight_venue_of_event / total_weight
    weight_organizer = weight_organizer_of_event / total_weight
    weight_performer = weight_performer_of_event / total_weight
    weight_date = weight_date_of_event / total_weight
    weight_time = weight_time_of_event / total_weight
    # we have separated date and time similarity to allow the flexibility to assign different weightage to these attributes
    # in future these weights can be assigned dynamically based on users' preferences about certain criterias (like price etc.)
    # (currently they are set in the config file)
    # the attributes that the user selects/enters can be used to change these weights dynamically so that the recommendations are more personalised

    combined_content_similarity_matrix = (
        (weight_desc * title_desc_similarity_matrix) +
        (weight_price * price_similarity_matrix) +
        (weight_duration * duration_similarity_matrix) +
        (weight_venue * venue_similarity_matrix) +
        (weight_organizer * organizer_similarity_matrix) +
        (weight_performer * performer_similarity_matrix) +
        (weight_date * date_similarity_matrix) +
        (weight_time * time_similarity_matrix)
    )

    # converting the similarity matrix to a dataframe for easier access and manipulation
    content_similarity_df = pd.DataFrame(combined_content_similarity_matrix, index=retrieved_event_df['id'], columns=retrieved_event_df['id'])

    # updating the memory with latest events and matrix
    with update_lock:

        global retrieved_combined_content_similarity_df
        retrieved_combined_content_similarity_df = content_similarity_df




# for now, we are creating the whole user-item matrix from scratch every time
# but we can use an incremental approach where only new changes are added to the matrix (the sample code is present in a text file in the modules folder)
# in future, as a different approach we can use neural networks to fill the user-item matrix, instead of relying on cosine similarity
# but to use neural networks, we need actual meaningful data to train the model correctly. also the training of the neural network needs to be scheduled in a similar way
# function to create a new user-item matrix using order history (GetOrderUser) api response
def update_user_item_matrix():

    user_item_matrix = pd.pivot_table(retrieved_user_order_df, index='userId', columns='eventId', aggfunc='size', fill_value=0)

    # here we are converting every user-item interaction to 0 or 1 (binary) to prevent skewness/bias
    # this also allows us to get similarity of events based on the different users that interact with it, without taking into account the number of tickets one user books
    user_item_matrix = pd.DataFrame(
        np.where(user_item_matrix > 0, 1, 0),
        index=user_item_matrix.index,
        columns=user_item_matrix.columns
    )

    # calculating cosine similarity between items and storing the matrix as a dataframe for easier access and manipulation
    item_similarity_matrix = cosine_similarity(user_item_matrix.T)
    item_similarity_df = pd.DataFrame(item_similarity_matrix, index=user_item_matrix.columns, columns=user_item_matrix.columns)

    # saving the new results to the global variables
    with update_lock:

        global retrieved_user_item_matrix_df
        retrieved_user_item_matrix_df = user_item_matrix

        global retrieved_item_similarity_df
        retrieved_item_similarity_df = item_similarity_df