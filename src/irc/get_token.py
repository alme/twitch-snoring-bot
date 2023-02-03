import sys
import requests

# pylint: disable=import-error
import config # type: ignore

if len(sys.argv) < 2:
    print("usage: get_token.py <code>")
    sys.exit(1)

response = requests.post(
    config.TOKEN_URL,
    params={
        'client_id': config.CLIENT_ID,
        'client_secret': config.CLIENT_SECRET,
        'code': sys.argv[1],
        'grant_type': 'authorization_code',
        'redirect_uri': config.REDIRECT_URI
    },
    timeout=30
)

print(response.content)
