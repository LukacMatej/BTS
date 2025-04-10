import network
import time
import urequests as requests
import json
from microdot import Microdot, Response

# Wi-Fi credentials
SSID = 'Mi 10T Pro'
PASSWORD = '123456789'
AI_API_KEY = 'AIzaSyCXhf0yGZX_l1VSkCLoYfL89yNaI-ARbrg'

# Connect to Wi-Fi
try:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("📶 Připojuji se k Wi-Fi...")
except Exception as e:
    print(f"❌ Chyba při inicializaci Wi-Fi: {e}")

class GenAIRequest:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}'
        
    def generate_response(self, prompt):
        headers = {'Content-Type': 'application/json'}
        
        # Opravený formát JSON dat podle Gemini API dokumentace
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024
            }
        }
        print(data)
        
        try:
            print(f"Odesílám požadavek: {json.dumps(data)[:100]}...")
            response = requests.post(self.base_url, headers=headers, json=data)
            print(f"API Status kód: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("API odpověď úspěšně parsována")
                    
                    # Správné mapování odpovědi podle aktuální dokumentace Gemini API
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        return text
                    else:
                        print(f"API vrátila neočekávanou strukturu: {result}")
                        return "Nebyla vygenerována žádná odpověď"
                except Exception as parse_error:
                    print(f"❌ Chyba při parsování odpovědi: {parse_error}")
                    return f"Chyba při zpracování odpovědi: {str(parse_error)}"
            else:
                try:
                    error_detail = response.json()
                    print(f"❌ API chyba: {error_detail}")
                except:
                    print(f"❌ API chyba: Status kód {response.status_code}")
                return f"Chyba: {response.status_code}"
        except Exception as e:
            print(f"❌ Výjimka při volání API: {e}")
            return f"Výjimka: {str(e)}"

# Connect to WiFi
try:
    max_wait = 10
    while max_wait > 0 and not wlan.isconnected():
        max_wait -= 1
        time.sleep(1)
        print(f"Čekání na připojení... {max_wait} pokusů zbývá")

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"✅ Připojeno! IP adresa: http://{ip}")
    else:
        print("❌ Připojení k Wi-Fi selhalo po 10 pokusech")
        ip = "0.0.0.0"
except Exception as e:
    print(f"❌ Chyba při připojování k Wi-Fi: {e}")
    ip = "0.0.0.0"

# Create the web application
app = Microdot()
Response.default_content_type = 'text/html'

@app.route('/')
def index(request):
    try:
        return '''
        <!DOCTYPE html>
        <html lang="cs">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Dotaz</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                h1 { color: #333; }
                form { margin: 20px 0; }
                input[type="text"] { width: 80%; padding: 8px; }
                button { padding: 8px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
                button:hover { background: #45a049; }
            </style>
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
        '''
    except Exception as e:
        print(f"❌ Chyba při zpracování indexové stránky: {e}")
        return f"Chyba: {str(e)}"

@app.route('/ask')
def ask(request):
    try:
        prompt = request.args.get('prompt')
        print(f"Přijat dotaz: {prompt}")
        
        if prompt:
            try:
                ai_request = GenAIRequest(AI_API_KEY)
                response = ai_request.generate_response(prompt)
                print(f"AI odpověď: {response[:50]}...")  # Vypiš prvních 50 znaků odpovědi
                
                return '''
                <!DOCTYPE html>
                <html lang="cs">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>AI Odpověď</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                        h1 { color: #333; }
                        .response { background: #f9f9f9; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
                        .back-btn { display: inline-block; margin-top: 20px; padding: 8px 15px; 
                                    background: #2196F3; color: white; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <h1>Odpověď AI</h1>
                    <div class="response">''' + response + '''</div>
                    <a href="/" class="back-btn">Zpět</a>
                </body>
                </html>
                '''
            except Exception as ai_error:
                print(f"❌ Chyba při generování AI odpovědi: {ai_error}")
                return f"Chyba při generování odpovědi: {str(ai_error)}"
        else:
            print("❌ Chybí parametr 'prompt'")
            return "Chybí parametr 'prompt'."
    except Exception as e:
        print(f"❌ Chyba při zpracování požadavku /ask: {e}")
        return f"Chyba: {str(e)}"

# Start the web server
try:
    print(f"⚡ Spouštím webový server na http://{ip}:80")
    app.run(host=ip, port=80)
except Exception as e:
    print(f"❌ Kritická chyba při spuštění serveru: {e}")
