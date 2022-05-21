import requests

host = 'slumbot.com'


class Session:
    def __init__(self):
        self.token = None

    def parse_response(self, response):
        try:
            r_json = response.json()
        except Exception:
            raise ValueError('BadJSON', response.status_code, response.text)

        if response.status_code != 200:
            raise ValueError(f'Error response {response.status_code}: {r_json!r}')

        if 'error_msg' in r_json:
            raise ValueError(r_json['error_msg'])

        if new_token := r_json.get('token'):
            self.token = new_token

        return r_json

    def new_hand(self):
        data = {}
        if self.token:
            data['token'] = self.token

        # Use verify=false to avoid SSL Error
        response = requests.post(f'https://{host}/api/new_hand', headers={}, json=data)
        return self.parse_response(response)

    def act(self, action):
        data = {'token': self.token, 'incr': action}

        # Use verify=false to avoid SSL Error
        response = requests.post(f'https://{host}/api/act', headers={}, json=data)
        return self.parse_response(response)
