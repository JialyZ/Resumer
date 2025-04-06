import os
import openai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"Debug: API Key loaded: {'Yes' if api_key else 'No'}")  # 调试信息

def ask_chatbot(resume_text, chat_history, memory_notes, user_input):
    # 检查API密钥是否配置
    if not api_key:
        print("Debug: API key not found in environment variables")  # 调试信息
        return "Error: DeepSeek API key not configured. Please check your .env file."

    try:
        # 设置API配置
        openai.api_key = api_key
        openai.api_base = "https://api.deepseek.com/v1"  # 修正API基础URL

        print(f"Debug: Resume text available: {'Yes' if resume_text else 'No'}")  # 调试信息
        print(f"Debug: Chat history length: {len(chat_history) if chat_history else 0}")  # 调试信息
        print(f"Debug: User input: {user_input}")  # 调试信息

        # 根据是否有简历内容来构建系统提示
        if resume_text:
            system_content = "You are a career advisor chatbot. Provide career suggestions based on the resume and remember user preferences."
            initial_context = f"My resume:\n{resume_text[:1200]}\n\nConversation so far:\n{memory_notes}"
        else:
            system_content = "You are a helpful career advisor chatbot. Provide general career advice and guidance. If the user hasn't uploaded a resume yet, you can suggest they do so for more personalized advice."
            initial_context = f"No resume uploaded yet.\n\nConversation so far:\n{memory_notes}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": initial_context},
        ]
        
        # 添加聊天历史
        if chat_history:
            for i in range(0, len(chat_history), 2):
                messages.append({"role": "user", "content": chat_history[i][1]})
                if i + 1 < len(chat_history):
                    messages.append({"role": "assistant", "content": chat_history[i+1][1]})

        # 添加当前用户输入
        messages.append({"role": "user", "content": user_input})

        print(f"Debug: Sending request to API with {len(messages)} messages")  # 调试信息
        print(f"Debug: Messages content: {messages}")  # 调试信息

        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            print(f"Debug: API response received: {response}")  # 调试信息
            return response.choices[0].message.content
        except Exception as api_error:
            print(f"Debug: API call error - {str(api_error)}")  # 调试信息
            raise api_error

    except Exception as e:
        error_message = str(e)
        print(f"Debug: Error occurred - {error_message}")  # 调试信息
        if "api_key" in error_message.lower():
            return "Error: Invalid or expired API key. Please check your API key configuration."
        elif "api_base" in error_message.lower():
            return "Error: Unable to connect to the API. Please check your internet connection."
        return f"Error: Unable to get response from the chatbot. {error_message}"