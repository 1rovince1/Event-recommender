# API urls to be used


# local server urls
events_data_url = 'http://127.0.0.1:5000/event_data'  # API from local server (inside the api_request_test_folder), for events' data
users_data_url = 'http://127.0.0.1:5000/user_data'  # API from local server (inside the api_request_test_folder), for order history data

# BM server urls
# server_url = 'https://1f4e-157-119-213-251.ngrok-free.app'  # remote server url
# events_data_url = server_url + '/api/bm/events' # remote server endpoint to obtain the data of all events (currently does not allow data of events more than the pagesize)
# users_data_url = server_url + '/api/bm/get-order-user'  # remote server url to obtain the data of order history

# EM server url
# events_data_url = 'https://60fc-2401-4900-5d9f-2ba9-99c5-de43-8b4b-e5a.ngrok-free.app/api/em/event' # data from event module