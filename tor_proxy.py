import requests
from stem import Signal
from stem.control import Controller
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


#USE for test https://api.ipify.org/
# signal TOR for a new connection
def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password=None)
        controller.signal(Signal.NEWNYM)
        time.sleep(10)
        controller.close()

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def get_page(url, headers):
    for i in range(5):
        gate_proxy = get_tor_session()
        request_page = gate_proxy.get(url, headers=headers)
        if request_page.status_code == 200:
            return request_page
        else:
            renew_connection()
            url_repeat(url)


def url_repeat(url):
    with open('erros_tage_page.txt', 'a') as file:
            file.write(url + '\n')
