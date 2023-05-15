import os
import json
import uuid
import flask
import hashlib
import requests

from bs4 import BeautifulSoup

from werkzeug.middleware.proxy_fix import ProxyFix

HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", 
        "Accept-Encoding": "gzip, deflate", 
        "Accept-Language": "en-US;q=0.9,en;q=0.8", 
        "Host": "iknowwhatyoudownload.com", 
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",         
}

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if not os.path.exists('data/_ip-countries.json'):
    with open('data/_ip-countries.json', 'w') as f:
        json.dump({}, f, indent=4)

def get_torrents(ip: str) -> list:
    url = 'https://iknowwhatyoudownload.com/en/peer/'

    html = requests.get(url, params={'ip': ip}, headers=HEADERS).text
    soup = BeautifulSoup(html, 'html.parser')

    gdp = soup.find_all('tr', attrs={'class': ''})[1:]

    downloads = []

    for table in gdp:
        currentTable = table
        body = currentTable.find_all('td')
        download = []

        for td in body:
            download.append(td.text.strip())

        downloads.append(download)

    return downloads

def get_ip_country(ip: str) -> str:
    """Get the country of an IP address."""
    with open(f'data/_ip-countries.json', 'r') as f:
        ip_countries = json.load(f)

    if ip in ip_countries:
        return ip_countries[ip]
    
    r = requests.get(f'https://ipinfo.io/{ip}/country', timeout=5)
    ip_countries[ip] = r.text.strip().lower()

    with open(f'data/_ip-countries.json', 'w') as f:
        json.dump(ip_countries, f, indent=4)

    return ip_countries[ip]

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/api/channel/<channel_name>', methods=['GET', 'POST'])
def channel(channel_name):
    if not os.path.exists(f'data/{channel_name}.json'):
        with open(f'data/{channel_name}.json', 'w') as f:
            json.dump([], f, indent=4)

    with open(f'data/{channel_name}.json', 'r') as f:
        messages = json.load(f)

    if flask.request.method == 'POST':
        message_content = flask.request.json.get('message')    
        ip_addr = flask.request.remote_addr
        message_id = str(uuid.uuid4())

        messages.append({
            'id': message_id,
            'author': ip_addr,
            'country': get_ip_country(ip_addr),
            'content': message_content,
            'last_torrent': get_torrents(ip_addr)[0][3]
        })

        with open(f'data/{channel_name}.json', 'w') as f:
            json.dump(messages, f, indent=4)

    return {
        'messages': messages[-100:],
        'hash': hashlib.sha256(json.dumps(messages).encode('utf-8')).hexdigest()
    }



app.run(host='0.0.0.0', port=5777, debug=True, use_evalex=False)
