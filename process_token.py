from kiteconnect import KiteConnect

request_token = '0PenaTPGDoJC3SehPNB82mPkEDcoQDBp'
api_key = 'q23715gf6tzjmyf5'
api_secret = '87ivk3royi2z30lhzprgovhrocp8yq1g'

print("Processing request token...")
kite = KiteConnect(api_key=api_key)
data = kite.generate_session(request_token, api_secret=api_secret)
new_token = data['access_token']

# Update .env
with open('.env', 'r') as f:
    lines = f.readlines()

with open('.env', 'w') as f:
    for line in lines:
        if line.startswith('KITE_ACCESS_TOKEN='):
            f.write(f'KITE_ACCESS_TOKEN="{new_token}"\n')
        else:
            f.write(line)

print(f"Token updated: {new_token}")
kite.set_access_token(new_token)
profile = kite.profile()
print(f"Connected as: {profile['user_name']}")