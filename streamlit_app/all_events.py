import streamlit as st
import requests

from utilities import links
from utilities import card_view


st.set_page_config(layout='wide')

st.header('All Events')


events_endpoint = links.events_data_url

response = requests.get(events_endpoint)

if response.status_code == 200:
    response_obj = response.json()
    events = response_obj['data']
    cards = card_view.convert_json_to_cards(events)
    card_view.display_as_cards(cards)

else:
    print('Error. Couldn\'t load.')

