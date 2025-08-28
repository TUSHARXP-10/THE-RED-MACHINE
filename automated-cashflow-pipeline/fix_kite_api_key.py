import os
import re

def read_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        print("Error: .env file not found")
        return None
    
    with open(env_path, 'r') as f:
        return f.read()

def write_env_file(content):
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    with open(env_path, 'w') as f:
        f.write(content)

def fix_api_keys():
    content = read_env_file()
    if content is None:
        return
    
    # Fix KITE_API_KEY format
    content = re.sub(r"KITE_API_KEY=\s*'([^']*)'\s*", r'KITE_API_KEY=\1', content)
    content = re.sub(r'KITE_API_KEY=\s*"([^"]*)"\s*', r'KITE_API_KEY=\1', content)
    
    # Fix KITE_API_SECRET format
    content = re.sub(r"KITE_API_SECRET=\s*'([^']*)'\s*", r'KITE_API_SECRET=\1', content)
    content = re.sub(r'KITE_API_SECRET=\s*"([^"]*)"\s*', r'KITE_API_SECRET=\1', content)
    
    # Fix KITE_REDIRECT_URL format
    content = re.sub(r"KITE_REDIRECT_URL=\s*'([^']*)'\s*", r'KITE_REDIRECT_URL=\1', content)
    content = re.sub(r'KITE_REDIRECT_URL=\s*"([^"]*)"\s*', r'KITE_REDIRECT_URL=\1', content)
    
    write_env_file(content)
    print("API key formats have been fixed in .env file")
    print("Please try running the Kite session fix script again")

if __name__ == '__main__':
    fix_api_keys()