import streamlit as st
import requests
import importlib

from utilities import links
from utilities import similarity_weights as wconfig
# import utilities.similarity_weights as wconfig

tit_des = st.text_input('Enter weight of title and description: ', value = wconfig.weight_title_description_of_event)
pr = st.text_input('Enter weight of event price: ', value = wconfig.weight_price_of_event)
dur = st.text_input('Enter weight of event duration: ', value = wconfig.weight_duration_of_event)
ven = st.text_input('Enter weight of event venue: ', value = wconfig.weight_venue_of_event)
org = st.text_input('Enter weight of event organizer: ', value = wconfig.weight_organizer_of_event)
perf = st.text_input('Enter weight of event performer: ', value = wconfig.weight_performer_of_event)
dat = st.text_input('Enter weight of event date: ', value = wconfig.weight_date_of_event)
tim = st.text_input('Enter weight of event time: ', value = wconfig.weight_time_of_event)


if st.button('Customize'):
    config_updation_endpoint = links.config_updation_endpoint
    payload = {
        "tit_des": tit_des,
        "pr": pr,
        "dur": dur,
        "ven": ven,
        "org": org,
        "perf": perf,
        "dat": dat,
        "tim": tim
    }
    

    response = requests.post(config_updation_endpoint, json=payload)

    if response.status_code == 200:
        res = response.json()
        st.markdown('<p style="color: green;">Success!</p>', unsafe_allow_html=True)
        st.write(res['message'])

        new_config = '\n'.join([
            "# adjustable weights:",
            "\n",
            f"weight_title_description_of_event = {tit_des}",
            f"weight_price_of_event = {pr}",
            f"weight_duration_of_event = {dur}",
            f"weight_venue_of_event = {ven}",
            f"weight_organizer_of_event = {org}",
            f"weight_performer_of_event = {perf}",
            f"weight_date_of_event = {dat}",
            f"weight_time_of_event = {tim}",

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

        # importlib.reload(utilities.similarity_weights)
        # st.experimental_rerun()

    else:
        st.write('Error!')


