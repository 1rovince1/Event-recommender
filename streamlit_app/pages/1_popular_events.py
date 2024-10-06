import requests
import streamlit as st

from utilities import links, card_view


# setting the stremlit app's layout to a wider view
st.set_page_config(layout='wide')

# setting all the required API request links
app_url = links.app_url
popular_events_endpoint = links.popular_events_endpoint











max_recommendations = st.text_input('Enter the maximum number of recommendations: ', value=6)
popular_events_endpoint = popular_events_endpoint.format(max_recommendations = max_recommendations)
response = requests.get(popular_events_endpoint)

if response.status_code == 200:

        data = response.json()
        events = data['data']
        if events is None:
            st.title("No popular event")
        else:
            st.title(data['label'])
            cards = card_view.convert_json_to_cards(events)
            card_view.display_as_cards(cards)

else:
        
        st.write('Error. Couldn\'t load')