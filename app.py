import streamlit as st
from client import chat_with_nemotron

st.set_page_config(page_title="Prompt Review", page_icon="🕵️‍♂️", layout="centered")

st.title("🕵️‍♂️ Prompt Review Tool")
st.caption("Prompt Review Tool — Powered by Nemotron")

SYSTEM_PROMPT = """You are an internal prompt review assistant.
Your job is to help team members review and improve their AI prompts.

When a user asks to review a prompt follow these steps in order:
1. Ask for their name and department if not provided
2. Call get_department_prompts with their department
3. Show the reference prompts if any are found
4. Call review_prompt to review their prompt
5. Call improve_prompt to improve their prompt
6. Ask if they want to log it
7. If yes call log_prompt to save it

Always be friendly and conversational."""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

# Display chat history
for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your message here..."):
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.display_messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            message, tool_results = chat_with_nemotron(st.session_state.messages)

            while tool_results:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                })

                for tr in tool_results:
                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_call_id": tr["tool_call_id"],
                        "content": tr["result"]
                    })

                message, tool_results = chat_with_nemotron(st.session_state.messages)
            
            response_text = message.content or ""

        st.markdown(response_text)

    st.session_state.display_messages.append({"role": "assistant", "content": response_text})
    st.session_state.messages.append({"role": "assistant", "content": response_text})