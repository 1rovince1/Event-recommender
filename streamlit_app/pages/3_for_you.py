import requests
import streamlit as st

from utilities import links, card_view


# setting the stremlit app's layout to a wider view
st.set_page_config(layout='wide')

# setting all the required API request links
app_url = links.app_url
personal_recommendations_endpoint = links.personal_recommendations_endpoint











user_id = st.text_input('Enter user id: ', value = 0, placeholder = 0)
max_recommendations = st.text_input('Enter the maximum number of recommendations:', value=6)

if user_id is None:
    st.title('New user (Not logged in)')

else:

    personal_recommendations_endpoint = personal_recommendations_endpoint.format(current_user_id = user_id, max_recommendations = max_recommendations)
    response = requests.get(personal_recommendations_endpoint)

    if response.status_code == 200:

            data = response.json()
            events = data['data']
            if events is None:
                st.title("No recommedations available yet")
            else:
                st.title(data['label'])
                cards = card_view.convert_json_to_cards(events)
                card_view.display_as_cards(cards)

    else:

            st.write('Error. Couldn\'t load')