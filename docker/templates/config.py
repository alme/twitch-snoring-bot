SERVER = "irc.chat.twitch.tv"
PORT = 6667
NICKNAME = "playsoundsnoring"

CLIENT_ID = "$CLIENT_ID"
CLIENT_SECRET = "$CLIENT_SECRET"
REFRESH_TOKEN = "$REFRESH_TOKEN"

CHANNEL = "lacari"

PLAYSOUND_COOLDOWN = 180
BOT_COOLDOWN = 210
PLAYSOUND_INTERVAL = 7200

# Wait for stream to be live for at least 30 minutes before sending commands
STREAM_LIVE_MINIMUM = 1800

PLAYSOUND_URL = "https://lacari.live/playsounds"

LOGGING_FORMAT = "%(asctime)s %(message)s"

API_URL = "https://api.twitch.tv/helix/{method}"

TOKEN_URL = "https://id.twitch.tv/oauth2/token"
REDIRECT_URI = "http://localhost"

TIMESTAMP_FILE = "/store/last_playsound"