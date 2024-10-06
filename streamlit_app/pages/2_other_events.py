import requests
import pandas as pd
import streamlit as st

from utilities import links, card_view

# setting the stremlit app's layout to a wider view
st.set_page_config(layout='wide')

# setting all the required API request links
app_url = links.app_url
other_similar_events_endpoint = links.other_similar_events_endpoint
events_also_liked_by_ohter_users_endpoint = links.events_also_liked_by_ohter_users_endpoint











events_endpoint = links.server_url
events_list = []
description_dict = {}
date_dict = {}


response = requests.get(events_endpoint)

if response.status_code == 200:
    response_obj = response.json()
    events = response_obj['data']

    for event in events:
          event_id = event['id']
          event_title = event['title']
          event_description = event['description']
          event_date = pd.to_datetime(event['startDateTime']).date()
          events_list.append(f'{event_id}. {event_title}')
          description_dict[event_id] = (event_description)
          date_dict[event_id] = event_date

else:
    st.write('Error. Couldn\'t load.')


selection = st.selectbox('Select event: ',
                        options = events_list,
                        index = None,
                        placeholder = '0')

if selection is not None:
    event_id = int(selection.split()[0][:-1])
    st.write(f'Description: {description_dict[event_id]}')
    st.write(f'Date: {date_dict[event_id]}')
else:
    event_id = 0
# event_id = st.text_input('Enter event id: ', value = 0)
# max_recommendations = st.text_input('Enter the maximum number of recommendations: ', value=3)
max_recommendations = 4




other_similar_events_endpoint = other_similar_events_endpoint.format(current_event_id = event_id, max_recommendations = max_recommendations)
response = requests.get(other_similar_events_endpoint)

if response.status_code == 200:

        data = response.json()
        events = data['data']
        if events is None:
            st.header("No similar events available yet")
        else:
            st.header(data['label'])
            cards = card_view.convert_json_to_cards(events)
            card_view.display_as_cards(cards)

else:

        st.write('Error. Couldn\'t load')






events_also_liked_by_ohter_users_endpoint = events_also_liked_by_ohter_users_endpoint.format(current_event_id = event_id, max_recommendations = max_recommendations)
response = requests.get(events_also_liked_by_ohter_users_endpoint)

if response.status_code == 200:

        data = response.json()
        events = data['data']
        if events is None:
            st.header("No users-also-liked data available")
        else:
            st.header(data['label'])
            cards = card_view.convert_json_to_cards(events)
            card_view.display_as_cards(cards)

else:

        st.write('Error. Couldn\'t load')