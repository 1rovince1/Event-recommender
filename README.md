# Event-recommender
This is an event recommendation system leveraging content-based and collaborative filtering. It also has some additional features like semantic and gemini search to provide the user with events matching his preferences.



# Note
- You need to add your own GOOGLE_API_KEY in .env file to use gemini-search functionality in search_engine. If you do not see a ".env" file in modules directory, create a file named ".env" only and put your GOOGLE_API_KEY as "GOOGLE_API_KEY = "XXXXXXX"", with the appropriate credentials
- The data received from the APIs in the api_request_test_folder directory is the expected response format for this application to work

## If you need to change the ports for various APIs or applications
- To change the port of data-sending APIs, you would need to edit the port in the command to run those APIs. The port would also need to be reflected in the "links.py" files in "modules" and "streamlit_app" directories for the respective APIs
- Similarly, if the port number for the application APIs is needed to be changed, it would need to be reflected in the "links.py" file of the "streamlit_app" directory



# How to run the app?

## Initial setup
- Create a python virtual environment in the main directory
- Activate the newly created virtual environment
- Use command "pip install -r requirements.txt" in CLI to install the required packages

## Running data sending APIs
- Activate the virtual environment and change the working/current directory to "api_request_test_folder"
- Use command "uvicorn test_api:app --port=5000" to get the data sending APIs live
- Data APIs will run on port 5000 of localhost

## Running the application APIs
- In a different terminal in the main directory, again activate the virtual environment
- Change the working dorectory to "modules"
- Use command "uvicorn app:app" to get the application APIs live
- Application API will run on default port set by uvicorn, i.e., 8000 at the time of writing this

## Running the Streamlit application
- In yet another different terminal, again activate the virtual environment
- Change the working directory to "streamlit_app" this time
- Use command "streamlit run all_events.py" to run the streamlit application in your browser.
- Streamlit application will run on default port for streamlit, i.e., 8501 at the time of writing this