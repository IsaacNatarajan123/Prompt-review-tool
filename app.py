import streamlit as st
from client import chat_with_nemotron, call_tool
import re

st.set_page_config(page_title="Prompt Review", page_icon="🔍", layout="centered")

st.title("🔍 Prompt Review Tool")
st.caption("Productsquads Internal Tool — Powered by Nemotron")

SYSTEM_PROMPT = """You are an internal prompt review assistant.
Your job is to help team members review and improve their prompts.

When a user asks to review a prompt:
1. Ask for their name and department if not provided
2. Once you have name and department, tell the user you are reviewing their prompt
3. Present the review results clearly showing Score, Clarity, Specificity, Context, Output Format and Summary
4. Present the improved version
5. Ask if they want to see reference prompts from their department
6. Ask if they want to log it

NEVER skip showing the full score and feedback.
NEVER ask for name and department again if already provided in the conversation."""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

if "reviewed" not in st.session_state:
    st.session_state.reviewed = False

if "name" not in st.session_state:
    st.session_state.name = None

if "department" not in st.session_state:
    st.session_state.department = None

if "original_prompt" not in st.session_state:
    st.session_state.original_prompt = None

def extract_name_department(messages):
    for msg in reversed(messages):
        if msg["role"] == "user":
            content = msg["content"].lower()
            match = re.search(r"i am (\w+) from (.+?)(?:department)?$", content)
            if match:
                return match.group(1).strip(), match.group(2).strip()
    return None, None

def extract_prompt(messages):
    for msg in messages:
        if msg["role"] == "user":
            content = msg["content"]
            if "review this prompt" in content.lower() or "—" in content:
                parts = content.split("—")
                if len(parts) > 1:
                    return parts[-1].strip()
                return content.replace("review this prompt", "").replace("Can you review this prompt", "").strip()
    return None

for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.display_messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            name, department = extract_name_department(st.session_state.messages)
            original_prompt = extract_prompt(st.session_state.messages)

            if name and department and original_prompt and not st.session_state.reviewed:
                st.session_state.name = name
                st.session_state.department = department
                st.session_state.original_prompt = original_prompt

                with st.spinner("Reviewing your prompt..."):
                    review_result = call_tool("review_prompt", {
                        "prompt": original_prompt,
                        "member_name": name,
                        "department": department
                    })

                with st.spinner("Improving your prompt..."):
                    improve_result = call_tool("improve_prompt", {
                        "prompt": original_prompt
                    })

                # Format review result nicely
                review_lines = review_result.strip().split("\n")
                formatted_review = ""
                for line in review_lines:
                    if line.startswith("Score:"):
                        formatted_review += f"**{line}**\n\n"
                    elif any(line.startswith(x) for x in ["Clarity:", "Specificity:", "Context:", "Output"]):
                        formatted_review += f"- **{line.split(':')[0]}:** {':'.join(line.split(':')[1:])}\n"
                    elif line.startswith("Summary:"):
                        formatted_review += f"\n**{line}**"
                    else:
                        formatted_review += f"{line}\n"

                response_text = f"""Here's the full review for your prompt, {name.capitalize()}:

**📊 Review Results**
{formatted_review}

---

**✅ Improved Prompt**
{improve_result}

---

Would you like to see reference prompts from the **{department.capitalize()}** department?
Or would you like to **log this** to the database?"""

                st.session_state.reviewed = True

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })

            else:
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

                if "review" not in user_input.lower():
                    st.session_state.reviewed = False

            st.markdown(response_text)

    st.session_state.display_messages.append({"role": "assistant", "content": response_text})
    st.session_state.messages.append({"role": "assistant", "content": response_text})