import streamlit as st
import requests

from utilities import links, card_view


st.set_page_config(layout='wide')

search_api_endpoint = links.search_api_endpoint

st.title('What type of events are you looking for?')
user_query = st.text_input('Enter keywords or short description about events you would like to see:')


if user_query != "":

    search_api_endpoint = search_api_endpoint.format(user_query = user_query)
    response = requests.get(search_api_endpoint)

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
        st.write('Error couldn\'t load.')