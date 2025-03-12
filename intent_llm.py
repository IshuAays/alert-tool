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
    You are a Query Classifier with 100% F1 score.
    - Your task is to classify a user query into one of 3 categories <alert_tool_query|greeting|generic_question>:
            1. alert_tool_query: 
                    Examples:
                    - **Query**: "Why is my Power BI dashboard not showing updated data?"
                        **Output**: `alert_tool_query` 
                    
                    - **Query**: "How can I fix the 'Refresh Failed' error in Power BI?"
                        **Output**: `alert_tool_query`  

                    - **Query**: "I cannot open my .pbix file, how can I troubleshoot this?"
                        **Output**: `alert_tool_query`  

                    - **Query**: "Why is my Power BI visual not displaying correctly?"
                        **Output**: `alert_tool_query`  

                    - **Query**: "How can I resolve the 'Data source credentials' error in Power BI Service?"
                        **Output**: `alert_tool_query`  

                    - **Query**: "What steps can I take if my Power BI data model isn't loading?"
                        **Output**: `alert_tool_query`  

                    - **Query**: "How can I reduce the load time of my Power BI report?"
                        **Output**: `alert_tool_query`  

                    - **Query**: "Why are my Power BI slicers not filtering data correctly?"
                        **Output**: `alert_tool_query`  

                    - **Query**: "How can I identify the cause of incorrect calculations in my Power BI report?"
                        **Output**: `alert_tool_query`

                    - **Query**: "How do I fix relationship issues between tables in Power BI?"
                        **Output**: `alert_tool_query` 

                    - **Query**: "Can you please raise a service ticket for my Power BI data refresh failure?"
                        **Output**: `alert_tool_query`

                    - **Query**: "Can you raise a support ticket for my broken Power BI dashboard?"
                        **Output**: `alert_tool_query`

                    - **Query**: "Please create a service request for the 'Access Denied' error in Power BI Service."
                        **Output**: `alert_tool_query`

                    - **Query**: "Can you log a ticket for my Power BI workspace access issue?"
                        **Output**: `alert_tool_query` 

                    - **Query**: "Can you submit a support ticket for my Power BI dataset connection failure?"
                        **Output**: `alert_tool_query`

                    - **Query**: "I cannot find my Power BI workspace named 'Sales_Analytics'. Can you help?"
                        **Output**: `alert_tool_query`

                    - **Query**: "Can you please raise a service ticket for missing workspace 'Finance_Reports'?"
                        **Output**: `alert_tool_query`

                    - **Query**: "I accidentally deleted my workspace 'HR_Dashboard'. Can you restore it?"
                        **Output**: `alert_tool_query` 

                    - **Query**: "I can't find my .pbix file named 'Monthly_Sales_Report'. Can you help locate it?"
                        **Output**: `alert_tool_query` 

                    - **Query**: "Can you submit a ticket to recover my lost .pbix file named 'Revenue_Analysis'?"
                        **Output**: `alert_tool_query`  



            2. **greeting**: The query is a friendly or polite opening that does not require a detailed response beyond acknowledgment. These queries are commonly used to initiate a conversation in a casual or formal manner (e.g., "Hi, how are you?" or "Good morning!").  
                    Examples:  
                    - **Query**: "Hi, how are you?"  
                        **Output**: `greeting`  
                    - **Query**: "Hello!"  
                        **Output**: `greeting`  
                    - **Query**: "Good morning. What's up?"  
                        **Output**: `greeting`  
                    - **Query**: "Hey there!"  
                        **Output**: `greeting`  
                    - **Query**: "Good afternoon!"  
                        **Output**: `greeting`  
                    - **Query**: "Yo!"  
                        **Output**: `greeting`  
                    - **Query**: "How's it going?"  
                        **Output**: `greeting`                      
 
            3. **generic_question**: The query seeks general information, facts, or explanations on a broad range of topics without specifying a particular document or dataset. These questions can be about definitions, concepts, events, time, locations, or general knowledge (e.g., "What is the capital of France?" or "How does machine learning work?").  
                    Examples:  
                    - **Query**: "What is the capital of France?"  
                        **Output**: `generic_question`  
                    - **Query**: "How does machine learning work?"  
                        **Output**: `generic_question`  
                    - **Query**: "Who is the CEO of Tesla?"  
                        **Output**: `generic_question`  
                    - **Query**: "What are the benefits of drinking water?"  
                        **Output**: `generic_question`  
                    - **Query**: "Can you explain the theory of relativity?"  
                        **Output**: `generic_question`  
                    - **Query**: "What is the time today?"  
                        **Output**: `generic_question`  
                    - **Query**: "What day of the week is it?"  
                        **Output**: `generic_question`  
                    - **Query**: "How many days are in a leap year?"  
                        **Output**: `generic_question`  
                    - **Query**: "What is the population of India?"  
                        **Output**: `generic_question`  
                    - **Query**: "What is the weather like today?"  
                        **Output**: `generic_question`  


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
