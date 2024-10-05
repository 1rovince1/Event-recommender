import streamlit as st
import requests

import card_view
import links

st.set_page_config(layout='wide')

gemini_search_endpoint = links.gemini_search_endpoint

st.title('What are you looking for?')
user_query = st.text_input('Tell us about what would you like to see:')


if user_query != "":

    gemini_search_endpoint = gemini_search_endpoint.format(user_query = user_query)
    response = requests.get(gemini_search_endpoint)

    if response.status_code == 200:

        received = response.json()
        st.write(received['gemini_response'])
        # events = received['gemini_response']
        # cards = card_view.convert_json_to_cards(events)
        # card_view.display_as_cards(cards)

    else:
        st.write('Error couldn\'t load.')