
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # 自动加载 .env 文件中的 API KEY

def generate_career_explanation(resume_text, job_title):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    endpoint = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = f"Given the resume: {resume_text[:1200]}...\n\nExplain why this person is suitable for the job title: '{job_title}'.\nRespond in 2-3 sentences in professional English."

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful AI career coach."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=15)
        result = response.json()

        if 'error' in result:
            return f"(DeepSeek API Error: {result['error'].get('message', 'unknown error')})"

        return result['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"(Exception during explanation generation: {str(e)})"
