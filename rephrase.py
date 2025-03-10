import os
import openai
import json
import re
from dotenv import load_dotenv
import streamlit as st


AZURE_OPENAI_API_KEY = st.secrets["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
DEPLOYMENT_NAME = st.secrets["DEPLOYMENT_NAME"]
API_VERSION = st.secrets["API_VERSION"]
# Load environment variables
# load_dotenv()




# Get Azure OpenAI Credentials from .env
# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
# API_VERSION = os.getenv("API_VERSION")

# Initialize Azure OpenAI client
client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def clean_json_response(response_text):
    """
    Cleans the response text by removing Markdown code blocks
    and ensuring it contains valid JSON.
    """
    try:
        # Remove Markdown code block markers (```json ... ```)
        clean_text = re.sub(r"```json\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL).strip()
        
        # Parse JSON
        return json.loads(clean_text)
    
    except json.JSONDecodeError:
        print("Error: LLM did not return structured JSON. Returning raw text.")
        return {
            "original_query": response_text,
            "rephrased_query": "Error: Unable to parse response as JSON.",
            "reason": "The LLM output was not properly formatted as JSON."
        }

def rephrase_prompt_with_context(current_prompt, past_interactions):
    """
    Rephrases a user's query while maintaining full conversational context.
    Ensures troubleshooting details and past responses are preserved.
    """

    if not past_interactions:
        return {"original_query": current_prompt, "rephrased_query": current_prompt, "reason": "No past interactions available."}

    # ✅ Keep only the last 10 messages (if available) to maintain recent context
    recent_interactions = past_interactions[-10:]

    # ✅ Construct structured conversation history including Assistant's responses
    conversation_history = []
    for entry in recent_interactions:
        role = entry['role'].capitalize()
        message = entry['message']
        conversation_history.append(f"{role}: {message}")

    full_context = "\n".join(conversation_history)


    # ✅ Construct system prompt to instruct the model
    system_prompt = f"""
        A. You are an AI assistant that ensures 100% accuracy in rephrasing queries while maintaining troubleshooting details.
        - Your task is to reformulate the user's latest query while preserving context, previous troubleshooting steps, and assistant responses.

        B. You will analyze the **entire past conversation** (up to 10 messages) to ensure that the rephrased query:
            1. **Retains full context** from previous assistant responses.
            2. **Does not drop any crucial troubleshooting details.**
            3. **Summarizes the query in a clear, structured manner.**
        
        C. **Conversation History**:
        ```
        {full_context}
        ```

        D. **Rephrase the following user query while ensuring full troubleshooting context is preserved**:
        ```
        {current_prompt}
        ```

        E. **Output your response in JSON format only** (DO NOT include Markdown code blocks):
        {{
            "original_query": "{current_prompt}",
            "rephrased_query": "<Rephrased version of the query with full context>",
            "reason": "<Explain why the query was rephrased this way>"
        }}
    """

    try:
        
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": current_prompt}
            ],
            temperature=0.0
        )
        
        json_response = response.choices[0].message.content.strip()

        # ✅ Clean and parse JSON response
        return clean_json_response(json_response)

    except Exception as e:
        print("Error calling Azure OpenAI:", e)
        return {
            "original_query": current_prompt,
            "rephrased_query": "Error: Unable to get response from LLM.",
            "reason": str(e)
        }
