from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv
from db.database import init_db, db_path
import sqlite3
import uvicorn
import os

load_dotenv()
init_db()

mcp = FastMCP("Prompt review system")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

@mcp.tool()
def review_prompt(prompt: str, member_name: str) -> str:
    """Reviews a prompt and returns a score with feedback.
    IMPORTANT: Follow these steps in exact order:
    1. Ask the user their name and department if not already provided
    2. YOU MUST call get_department_prompts tool with the department FIRST
    3. Display the results from get_department_prompts to the user as reference prompts
    4. Then proceed with the review
    5. Then call improve_prompt
    6. Finally ask if they want to log it
    NEVER skip step 2 even if the department is new or unknown."""

    response = client.chat.completions.create(
        model="meta/llama-4-maverick-17b-128e-instruct",
        messages=[
            {
                "role": "system",
                "content": """
                You are a expert prompt reviewer.
                Review the given prompt and provide feedback in this exact format:
                Score: <number from 0 to 10>
                Clarity: <Good or Bad> - <one line reason>
                Specificity: <Good or Bad> - <one line reason>
                Context: <Good or Bad> - <one line reason>
                Output format: <Good or Bad> - <one line reason>
                Summary: <one line overall feedback>
                """
            },
            {
                "role": "user",
                "content": f"Review this prompt: {prompt}"
            }
        ]
    )

    return response.choices[0].message.content

@mcp.tool()
def improve_prompt(prompt: str) -> str:
    response = client.chat.completions.create(
        model="meta/llama-4-maverick-17b-128e-instruct",
        messages=[
            {
                "role": "system",
                "content": """
                You are a expert prompt engineer
                Your job is to rewrite the given prompt to make it clearer,
                more specific, and more effective.
                Return only the improved prompt - no explanation, no preamble
                """
            },
            {
                "role": "user",
                "content": f"Improve this prompt: {prompt}"
            }
        ]
    )

    return response.choices[0].message.content

@mcp.tool()
def log_prompt(member_name: str, department: str, original_prompt: str, score: int, improved_prompt: str) -> str:
    """Logs the prompt, score, improved version and department to the database.
    IMPORTANT: Never assume or default the member_name or department.
    You MUST ask the user 'What is your name?' if member_name is not provided.
    You MUST ask the user 'Which department are you from?' if department is not provided."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO prompts (member_name, department, original_prompt, score, improved_prompt)
        VALUES (?, ?, ?, ?, ?)
    ''', (member_name, department, original_prompt, score, improved_prompt))
    conn.commit()
    conn.close()

    return f"Prompt logged successfully for {member_name} with a score of {score}/10"

@mcp.tool()
def get_department_prompts(department: str, min_score: int = 7) -> str:
    """Fetches high scoring prompts from the database for a given department.
    IMPORTANT: 
    - ALWAYS display the full results returned by this tool to the user
    - Show each prompt clearly with its score
    - If no prompts found tell the user there are no high scoring prompts for that department
    - NEVER summarize or skip showing the prompts"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT original_prompt, improved_prompt, score FROM prompts
        WHERE department = ? AND score >= ?
        ORDER BY score DESC
        LIMIT 3
    ''', (department, min_score))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No high scoring prompts found for {department} department. Proceeding with review normally."

    result = f"📚 High scoring prompts from {department} department:\n\n"
    for i, row in enumerate(rows, 1):
        result+=f"{i}. Prompt: {row[0]}\n"
        result+=f"   Improved: {row[1]}\n"
        result+=f"   Score: {row[2]}/10\n\n"

    return result
                   
                   
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        mcp.sse_app(), 
        host="0.0.0.0", 
        port=port,
        forwarded_allow_ips="*"
    )