import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

def test_deepseek():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL")
    
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found in .env")
        return

    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        print("🚀 Sending request to DeepSeek...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello! Confirm if you are DeepSeek and tell me today's date."},
            ],
            stream=False
        )
        print("✅ Success!")
        print(f"🤖 Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_deepseek()
