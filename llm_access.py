import os
import json
import time
from http.client import HTTPSConnection
from urllib.parse import urlparse

# 读取.env文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    env_vars[key] = value
    else:
        print("Error: .env file not found. Please copy env.example to .env and fill in your values.")
        exit(1)
    
    return env_vars

# 访问LLM API
def call_llm(base_url, model, token, prompt, temperature=0.7, max_tokens=1000):
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": float(temperature),
        "max_tokens": int(max_tokens)
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 开始计时
    start_time = time.time()
    
    try:
        # 创建连接
        conn = HTTPSConnection(host)
        
        # 发送请求
        conn.request(
            "POST",
            f"{path}/chat/completions",
            body=json.dumps(data),
            headers=headers
        )
        
        # 获取响应
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        conn.close()
        
        # 结束计时
        end_time = time.time()
        
        # 解析响应
        response_json = json.loads(response_data)
        
        if 'error' in response_json:
            print(f"Error: {response_json['error']['message']}")
            return None, 0, 0, 0
        
        # 提取token使用情况
        usage = response_json.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        # 计算耗时和速度
        elapsed_time = end_time - start_time
        tokens_per_second = total_tokens / elapsed_time if elapsed_time > 0 else 0
        
        # 提取响应内容
        content = response_json['choices'][0]['message']['content']
        
        return content, total_tokens, elapsed_time, tokens_per_second
        
    except Exception as e:
        print(f"Error: {str(e)}")
        end_time = time.time()
        elapsed_time = end_time - start_time
        return None, 0, elapsed_time, 0

# 主函数
def main():
    print("=== LLM Access Script ===")
    
    # 加载环境变量
    env_vars = load_env()
    base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
    model = env_vars.get('MODEL', 'gpt-3.5-turbo')
    token = env_vars.get('TOKEN', '')
    temperature = env_vars.get('TEMPERATURE', '0.7')
    max_tokens = env_vars.get('MAX_TOKENS', '1000')
    
    print(f"Using model: {model}")
    print(f"Base URL: {base_url}")
    
    # 示例 prompt
    prompt = "Hello, please tell me a short story about AI."
    
    # 调用LLM
    print("\nCalling LLM...")
    content, total_tokens, elapsed_time, tokens_per_second = call_llm(
        base_url, model, token, prompt, temperature, max_tokens
    )
    
    # 输出结果
    print("\n=== Results ===")
    if content:
        print("Response:")
        print(content)
    print(f"Total tokens: {total_tokens}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Tokens per second: {tokens_per_second:.2f}")

if __name__ == "__main__":
    main()