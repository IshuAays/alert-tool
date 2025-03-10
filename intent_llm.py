import openai
import json
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
# load_dotenv()

AZURE_OPENAI_API_KEY = st.secrets["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
DEPLOYMENT_NAME = st.secrets["DEPLOYMENT_NAME"]
API_VERSION = st.secrets["API_VERSION"]



# Get Azure OpenAI Credentials from .env
# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
# API_VERSION = os.getenv("API_VERSION")

# Initialize OpenAI client
client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def clean_json_response(response_text):
    """Cleans the JSON response by removing markdown formatting."""
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove the leading ```json
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove the trailing ```
    return response_text.strip()

def categorize_query(query):
    prompt = f"""
    You are a Query Classifier with 100% accuracy.
    Your task is to classify a user query into one of three categories:  
    1. **alert_tool_query** → Related to Power BI issues or ServiceNow requests related to alerts, tickets, or reporting.  
    2. **greeting** → Simple greetings like "Hello".  
    3. **generic_question** → General knowledge or informational questions.  

    Examples:
    - "My Power BI dashboard is not refreshing" → `"alert_tool_query"`
    - "Hey, how are you?" → `"greeting"`
    - "Tell me about SQL queries" → `"generic_question"`
    - "Could you please update the ServiceNow ticket to include my name, Ishu Jangid, in the 'Raised By' field and set the 'Raised Date' to 10/03/2025?" → `"alert_tool_query"`
    - "Create an alert in ServiceNow if Power BI fails to refresh" → `"alert_tool_query"`
    - "What is the capital of France?" → `"generic_question"`

    Classify this query: "{query}"  
    Respond ONLY with a JSON object in this format:  
    {{
        "original_query": "{query}",
        "task": "<correct_category>"
    }}
    """


    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a highly accurate query classifier."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        raw_response = response.choices[0].message.content
        # print("Raw LLM Response:", raw_response)  # Debugging print

        cleaned_response = clean_json_response(raw_response)
        extracted_data = json.loads(cleaned_response)  # Convert string to JSON

        return extracted_data.get("task", "task:unknown")  # Default fallback if missing

    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return "task:unknown"
    except Exception as e:
        print("Unexpected Error:", e)
        return "task:error"
