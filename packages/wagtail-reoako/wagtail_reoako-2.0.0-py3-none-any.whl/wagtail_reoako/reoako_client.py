import urllib
import requests

default_api_domain = 'https://api.reoako.nz'
default_api_base_path = 'api/v1'


def get_base_url(url):
    parts = urllib.parse.urlparse(url)
    return f'{parts.scheme}://{parts.netloc}'


class ReoakoApiClient:
    def __init__(self, api_token='', api_domain=default_api_domain, referer=''):
        self.token = api_token
        self.domain = api_domain.strip('/')
        self.base_path = default_api_base_path
        self.origin = get_base_url(referer)

    def build_path(self, path):
        return f'{self.domain}/{self.base_path}/{path}'

    def get(self, endpoint, params={}):
        resp = requests.get(endpoint, headers={
            'Accept': 'application/json',
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json',
            'Origin': self.origin
        }, params=params)

        return resp

    def search(self, term):
        path = self.build_path('entries')

        try:
            resp = self.get(path, {'search': term})
            json = resp.json()
            return json

        except requests.exceptions.ConnectionError as e:
            return {'message': f'[{type(e).__name__}] Reoako domain "{self.domain}" could not be reached'}

        except Exception as e:
            return {'message': f'Unknown Error: [{type(e).__name__}] {str(e)}'}
