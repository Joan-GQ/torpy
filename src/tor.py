import typing
import timeit
import requests
import re
import os
from typing_extensions import TypeAlias
from subprocess import Popen, PIPE, STDOUT, call
from stem.control import Controller
from stem import Signal
from dotenv import load_dotenv, dotenv_values
from __future__ import annotations

load_dotenv('.env')

TOR_SERVICE_CHECK_CMD =  'pgrep -l "tor\\b"'
TOR_SERVICE_START_CMD = 'sudo service tor start'
TOR_SERVICE_STOP_CMD  = 'sudo service tor stop'
REGEX_SERVICE = re.compile('([0-9]+).([A-Za-z]+)')
REGEX_IP = re.compile('([0-9\.]+)')

class NotSudo(Exception):
    pass

class NoSuchService(Exception):
    pass

def check_sudo() -> None:
    if os.getuid() != 0:
        raise NotSudo('Script is not running with elevated privileges. Run again using sudo.')

def execute_command(command):
    process = Popen(command, shell=True,
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                    close_fds=True)
    output = process.stdout.read().decode('utf-8')
    return output

def is_tor_active() -> bool:
    output = execute_command(TOR_SERVICE_CHECK_CMD)
    search = re.search(pattern=REGEX_SERVICE, string=output)
    if search == None:
        return False
    else:
        return True

def get_ip(service:str|int='httpbin', session:requests.Session=None) -> str:
    if session == None:
        session = requests.session()
    
    valid_services = ['ipify', 'httpbin', 'ipecho']
    if type(service) == int and service not in range(len(valid_services)):
        raise NoSuchService(f'Service index {service} not in range {len(valid_services)}.')
    
    if type(service) == str and service not in valid_services:
        raise NoSuchService(f'Invalid service {service}. It should be one of this ones: {valid_services}')

    ip  = ''
    if service == 0 or service == 'ipify':
        ip = session.get('https://api.ipify.org').text
    
    if service == 1 or service == 'httpbin':
        ip = session.get('https://httpbin.org/ip').text

    if service == 2 or service == 'ipecho':
        ip = session.get('https://ipecho.net/plain').text

    ip = re.search(string=ip, pattern=REGEX_IP).group()
    return ip


class Onion(object):
    def __init__(self, port:int=9050):
        self.port = port
        self.init_session()
        self.get_ip()
        self.real_ip = get_ip(session = None)
        pass

    def init_session(self):
        self.session = requests.session()
        self.session.proxies = {
            'http': f'socks5://127.0.0.1:{self.port}',
            'https':f'socks5://127.0.0.1:{self.port}'
        }

    def renew_identity(self, password:str|None=None, port:int=9051):
        if password == None:
            try:
                password = dotenv_values()['PASSWORD']
            except KeyError:
                print('Key not found in dotenv.')
            except Exception:
                print('An unexpected error has ocurred whilst loading tor password. Is dotenv loaded?')

        with Controller.from_port(port=port) as controller:
            controller.authenticate(password)
            controller.signal(Signal.NEWNYM)
        self.init_session()

    def request(self, method, url, **kwargs):
        self.last_delay = timeit.default_timer()
        output = self.session.request(method=method, url=url, **kwargs)
        self.last_delay = timeit.default_timer() - self.last_delay
        return output

    def get(self, url, params=None, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('get', url, params=params, **kwargs)

    def options(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('options', url, **kwargs)

    def head(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return self.request('head', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request('post', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request('put', url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        return self.request('patch', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)

    def get_ip(self):
        self.last_delay = timeit.default_timer()
        self.ip = get_ip(session = self.session)
        self.last_delay = timeit.default_timer() - self.last_delay
        return self.ip

    def get_delay(self):
        return round(self.last_delay, 2)

    
