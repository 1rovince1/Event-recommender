from engines import updation_engine as updater


# returning the list of events that are currently available (events which have not started yet)
def event_availability(recommendation_list):

    available_events_list = [event for event in recommendation_list if event in updater.retrieved_recommendable_events_list]
    return available_events_list




# checking if the user's data is present in the user-item matrix or not
def user_activeness(user_id):
    
    if user_id is None:
        return False

    if user_id not in updater.retrieved_user_item_matrix_df.index:
        return False
    
    return True




# checking whether the event has activity
def event_activeness(event_id):

    if event_id is None:
        return False
    
    if event_id not in updater.retrieved_user_item_matrix_df.columns:
        return False
    
    return True




# checking if the event's data is present in the dataframe of all events or not
def event_in_memory(event_id):

    if event_id is None:
        return False

    if not event_id in updater.retrieved_event_df['id'].values:
        return False
    
    return True










