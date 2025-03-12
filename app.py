import streamlit as st
from intent_llm import categorize_query
from llm_response import llm_response
from rephrase import rephrase_prompt_with_context

# Initialize session state for conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

st.title("Aays IT Support AI Bot")

# Display chat history
for entry in st.session_state.conversation_history:
    role = entry["role"]
    message = entry.get("original_message", entry["message"])  # Always show original query if available
    with st.chat_message(role):
        st.write(message)

query = st.chat_input("Ask me anything about Aays IT systems")

if query:
    # ✅ Immediately display user message in UI
    with st.chat_message("user"):
        st.write(query)
    
    # ✅ Show loading animation while processing
    with st.spinner("Thinking..."):
        # ✅ Get both original and rephrased query
        rephrase_result = rephrase_prompt_with_context(query, st.session_state.conversation_history)
        original_query = rephrase_result.get("original_query", query)
        rephrased_query = rephrase_result.get("rephrased_query", query)

        # ✅ Send the rephrased query to categorize function
        query_category = categorize_query(rephrased_query)

        # Format previous conversation history
        previous_conversation = "\n".join([f"{e['role']}: {e.get('original_message', e['message'])}" for e in st.session_state.conversation_history])
        full_query = f"{previous_conversation}\nUser: {rephrased_query}"

        # ✅ Store both original & rephrased query in conversation history
        st.session_state.conversation_history.append({
            "role": "user",
            "original_message": original_query,
            "message": rephrased_query
        })

        # ✅ Generate response
        if query_category == "alert_tool_query":
            response = llm_response(full_query, 1)
        elif query_category == "greeting":
            response = "Hello! I'm here to help with any questions on Aays IT systems."
        elif query_category == "generic_question":
            response = "Hello! I'm here to help with any questions on Aays IT systems. Thank you!"
        else:
            response = "Cannot classify this query. Please provide more details."

        # ✅ Save assistant response
        st.session_state.conversation_history.append({"role": "assistant", "message": response})

    # ✅ Display assistant response after processing
    with st.chat_message("assistant"):
        st.write(response)
