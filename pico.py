import network
import time
import requests
from microdot import Microdot

SSID = 'Mi 10T Pro'
PASSWORD = '123456789'
AI_API_KEY = 'AIzaSyCXhf0yGZX_l1VSkCLoYfL89yNaI-ARbrg'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

class GenAIRequest:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + api_key
    def generate_response(self, prompt):
        headers = {'Content-Type': 'application/json'}
        data = {
            'prompt': prompt,
            'temperature': 0.5,
            'maxOutputTokens': 100,
            'topK': 40,
            'topP': 0.95,
            'stopSequences': ['\n']
        }
        response = requests.post(self.base_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['output']
        else:
            return f"Error: {response.status_code}"

print("📶 Připojuji se k Wi-Fi...")
while not wlan.isconnected():
    time.sleep(1)

ip = wlan.ifconfig()[0]
print(f"✅ Připojeno! IP adresa: http://{ip}")

app = Microdot()

@app.route('/')
def index(request):
    return 'Ahoj ze serveru na Raspberry Pi Pico W!'

@app.route('/form')
def form(request):
    html = """
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Dotaz</title>
    </head>
    <body>
        <h1>Zadejte svůj dotaz</h1>
        <form action="/ask" method="get">
            <label for="prompt">Dotaz:</label><br>
            <input type="text" id="prompt" name="prompt" required><br><br>
            <button type="submit">Odeslat</button>
        </form>
    </body>
    </html>
    """
    return html

@app.route('/ask')
def ask(request):
    prompt = request.args.get('prompt')
    if prompt:
        ai_request = GenAIRequest(AI_API_KEY)
        response = ai_request.generate_response(prompt)
        return response
    else:
        return "Chybí parametr 'prompt'."

app.run(host=ip, port=80)
