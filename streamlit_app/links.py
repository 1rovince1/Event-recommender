# local
server_url = 'http://127.0.0.1:5000/event_data'

# for popular_events
app_url = 'http://127.0.0.1:8000'
popular_events_endpoint = app_url + '/api/bm/recommendations/popular_events?max_recommendations={max_recommendations}'

# for other_events
other_similar_events_endpoint = app_url + '/api/bm/recommendations/similar_events?current_event_id={current_event_id}&max_recommendations={max_recommendations}'
events_also_liked_by_ohter_users_endpoint = app_url + '/api/bm/recommendations/users_also_liked?current_event_id={current_event_id}&max_recommendations={max_recommendations}'

# for for_you
personal_recommendations_endpoint = app_url + '/api/bm/recommendations/user_recommendations?current_user_id={current_user_id}&max_recommendations={max_recommendations}'

# for update_config
config_updation_endpoint = app_url + '/api/bm/recommendations/update_similarity'

# for semantic_search
search_api_endpoint = 'http://127.0.0.1:8000/api/bm/recommendations/semantic_search?query={user_query}'

# for gemini search
gemini_search_endpoint = 'http://127.0.0.1:8000/api/bm/recommendations/gemini_search?query={user_query}'




# BM
# server_url = 'https://dcec-157-119-213-251.ngrok-free.app/api/bm/events'  # remote server url

# EM
# server_url = 'https://310e-117-243-214-166.ngrok-free.app/api/em/event?Page=1&Size=100'