import config
import json
import requests

from urllib.parse import quote_plus

class TwitchToken:

    def __init__(self):
        self.access_token = self.get_access_token()

    def get_access_token(self):
        response = requests.post(
            config.TOKEN_URL,
            params={
                'client_id': config.CLIENT_ID,
                'client_secret': config.CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': quote_plus(config.REFRESH_TOKEN)
            }
        )

        if response.status_code == 200:
            data = json.loads(response.content)
            self.access_token = data['access_token']

            return self.access_token
        else:
            raise Exception("Received invalid response when getting access token redirect.")

twitch_token = TwitchToken()