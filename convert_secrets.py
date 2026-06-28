import json

# Apna serviceAccountKey.json ka naam yahan likho
with open("serviceAccountKey.json", "r") as f:
    data = json.load(f)

print("=" * 60)
print("YEH EXACT TEXT COPY KARKE STREAMLIT CLOUD SECRETS ME PASTE KARO")
print("=" * 60)
print()

print(f'''GROQ_API_KEY = "gsk_your_groq_key_here"
FIREBASE_API_KEY = "AIzaSyBJMI1T3cEePtoSPVP2N7n5WmsmUN6A4gU"

[fbase]
type = "{data['type']}"
project_id = "{data['project_id']}"
private_key_id = "{data['private_key_id']}"
client_email = "{data['client_email']}"
client_id = "{data['client_id']}"
auth_uri = "{data['auth_uri']}"
token_uri = "{data['token_uri']}"
auth_provider_x509_cert_url = "{data['auth_provider_x509_cert_url']}"
client_x509_cert_url = "{data['client_x509_cert_url']}"
''')

# private_key ko triple quotes mein print karo taake newlines sahi rahein
print('''private_key = """''', end="")
print(data['private_key'].replace('-----END PRIVATE KEY-----\n', '-----END PRIVATE KEY-----'), end="")
print('''"""''')

print()
print("=" * 60)
print("COPY KARO AUR STREAMLIT CLOUD → SETTINGS → SECRETS ME PASTE KARO")
print("=" * 60)

