import config
import json
import requests
import twitch_token

class TwitchAPI:

    def send_api_request(self, url, params):
        headers = {
            'Authorization': f'Bearer {twitch_token.twitch_token.access_token}',
            'Client-Id': config.CLIENT_ID
        }

        response = requests.get(url, params, headers=headers)
        if response.status_code == 401:
            self.access_token = twitch_token.twitch_token.get_access_token()

            headers['Authorization'] = f'Bearer {twitch_token.twitch_token.access_token}'
            response = requests.get(url, params, headers=headers)

        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Received invalid response ({response.status_code}) when sending "
                            f"API request to {url}.")

    def is_channel_live(self, channel):
        response = self.send_api_request(config.API_URL.format(method="streams"), {'user_login': channel})        

        data = json.loads(response.content)
        if len(data["data"]) == 0:
            return False
            
        return data["data"][0]["type"] == "live"