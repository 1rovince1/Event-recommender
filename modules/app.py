from typing import Optional, Dict, Any
import json

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

import update_scheduler as sch_update
from engines import recommendation_engine as recommender
from engines import search_engine as search


# initialising app and scheduler
app = FastAPI()
scheduler = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:8501'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)











@app.on_event('startup')
def scheduler_on():

    sch_update.periodic_update() # updating matrices just at the startup
    # scheduler.add_job(sch_update.periodic_update, 'interval', seconds=10)
    scheduler.add_job(sch_update.periodic_update, 'interval', minutes=30)
    scheduler.start()
    print('Scheduler started. Recommendation matrices and related files will be updated every 30 minutes.')




@app.on_event('shutdown')
def scheduler_off():

    scheduler.shutdown()
    print('Scheduler shutdown.')

# we might need to setup a log file for these status/info messages instead of printing in the console











# api endpoint to get popular events
@app.get("/api/bm/recommendations/popular_events", response_model=Dict[str,Any])
async def popular_events(
    max_recommendations: Optional[int] = Query(5, description="Number of recommendations required")):

    try:
        # calling the recommendation logic
        recommendation_response = recommender.popular_events()

        if recommendation_response["data"] is not None:
            recommended_event_ids = recommendation_response["data"][:max_recommendations]

            # getting the events info in the required response format from the events_list
            recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        else:
            recommended_events = None

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Popular events",
            "label" : recommendation_response["label"],
            "data" : recommended_events
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint to get recommended events for a user
@app.get("/api/bm/recommendations/user_recommendations", response_model=Dict[str,Any])
async def personal_recommendations_for_user(
    current_user_id: int = Query(..., description="User ID of the current user"),
    max_recommendations: Optional[int] = Query(5, description="Number of recommendations required")):

    try:
        if current_user_id is None:
            raise HTTPException(status_code=400, detail="Missing 'current_user_id' in request parameters.")

        # calling the recommendation logic
        recommendation_response = recommender.collaborative_item_based_recommendations(current_user_id)

        if recommendation_response["data"] is not None:
            recommended_event_ids = recommendation_response["data"][:max_recommendations]

            # getting the events info in the required response format from the events_list
            recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        else:
            recommended_events = None

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Events recommended for the user",
            "label" : recommendation_response["label"],
            "data" : recommended_events
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint to get similar events
@app.get("/api/bm/recommendations/similar_events", response_model=Dict[str,Any])
async def events_similar_to_this_event(
    current_event_id: int = Query(..., description="Event ID of the selected event"),
    max_recommendations: Optional[int] = Query(2, description="Number of recommendations required")):

    try:
        if current_event_id is None:
            raise HTTPException(status_code=400, detail="Missing 'current_event_id' in request parameters.")

        # calling the recommendation logic
        recommendation_response = recommender.content_based_recommendations(current_event_id)

        if recommendation_response["data"] is not None:
            recommended_event_ids = recommendation_response["data"][:max_recommendations]

            # getting the events info in the required response format from the events_list
            recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        else:
            recommended_events = None

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Similar events",
            "label" : recommendation_response["label"],
            "data" : recommended_events
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint to get users-also-liked events
@app.get("/api/bm/recommendations/users_also_liked", response_model=Dict[str,Any])
async def other_users_also_liked(
    current_event_id: int = Query(..., description="Event ID of the selected event"),
    max_recommendations: Optional[int] = Query(2, description="Number of recommendations required")):

    try:
        if current_event_id is None:
            raise HTTPException(status_code=400, detail="Missing 'current_event_id' in request parameters.")

        # calling the recommendation logic
        recommendation_response = recommender.users_also_liked(current_event_id)

        if recommendation_response["data"] is not None:
            recommended_event_ids = recommendation_response["data"][:max_recommendations]

            # getting the events info in the required response format from the events_list
            recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        else:
            recommended_events = None

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Users-also-liked events",
            "label" : recommendation_response["label"],
            "data" : recommended_events
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")





# api endpoint to trigger update in similarity calculation

class UpdateConfig(BaseModel):
    tit_des: float
    pr: float
    dur: float
    ven: float
    org: float
    perf: float
    dat: float
    tim: float

@app.post("/api/bm/recommendations/update_similarity", response_model=Dict[str,Any])
async def update_similarity_config(config: UpdateConfig):

    try:
        sch_update.customize_content_similarity_matrix(
            config.tit_des,
            config.pr,
            config.dur,
            config.ven,
            config.org,
            config.perf,
            config.dat,
            config.tim
        )

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Customized configurations!"
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint for semantic search
@app.get("/api/bm/recommendations/semantic_search", response_model = Dict[str, Any])
async def semantic_search(
    query: str = Query(..., description="Search query text"),
    max_recommendations: Optional[int] = Query(10, description="Number of recommendations required")):
    
    try:
        # calling the search logic
        search_response = search.semantic_search(query)

        if search_response["data"] is not None:
            recommended_event_ids = search_response["data"][:max_recommendations]

            # getting the events info in the required response format from the events_list
            recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

        else:
            recommended_events = None

        # creating the response body
        response_content = {
            "status" : "success",
            "message" : "Popular events",
            "label" : search_response["label"],
            "data" : recommended_events
        }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")
    




# api endpoint to invoke gemini based event search
@app.get("/api/bm/recommendations/gemini_search", response_model = Dict[str, Any])
async def gemini_search(
    query: str = Query(..., description="Search query text"),
    max_recommendations: Optional[int] = Query(10, description="Number of recommendations required")):
    
    try:
        # calling the search logic
        search_response = search.gemini_search(query)
        print(type(search_response))
        print(search_response)

        recommended_event_ids = json.loads(search_response)
        print(type(recommended_event_ids))
        print(recommended_event_ids)

        # getting the events info in the required response format from the events_list
        recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]
        print(recommended_events)

        response_content = {
            'status': 'Success',
            'gemini_response': recommended_events
        }

        # try:
            # if search_response["data"] is not None:
            # import json
            # recommended_event_ids = json.loads(search_response)
            # print(type(recommended_event_ids))

            # # getting the events info in the required response format from the events_list
            # recommended_events = [sch_update.events_list[sch_update.indices[i]] for i in recommended_event_ids]

            # response_content = {
            #     'status': 'Success',
            #     'gemini_response': recommended_events
            # }

        # except:
        #     response_content = {
        #         'status': 'Success',
        #         'gemini_response': search_response
        #     }


        # else:
        #     recommended_events = None

        # # creating the response body
        # response_content = {
        #     "status" : "success",
        #     "message" : "Popular events",
        #     "label" : search_response["label"],
        #     "data" : recommended_events
        # }

        return response_content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occured: {str(e)}")