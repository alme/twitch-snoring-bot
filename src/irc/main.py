import irc.bot

import argparse
import config
import datetime
import logging
import threading
import time
import twitch_token

from api import TwitchAPI
from playsounds import get_playsounds


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, playsounds, time=None):
        irc.bot.SingleServerIRCBot.__init__(self, [
            (config.SERVER, config.PORT, f'oauth:{twitch_token.twitch_token.access_token}')], config.NICKNAME, config.NICKNAME)

        self.api = TwitchAPI()

        self.channel = f'#{config.CHANNEL}'
        self.playsounds = playsounds

        if time:
            self.last_playsound_time = time
        else:
            self.last_playsound_time = datetime.datetime.now()

        self.last_sent_playsound_time = datetime.datetime.min
        self.timer = None

        self.start_playsound_timer()

    def on_welcome(self, connection, event):
        connection.join(self.channel)
        logging.info(f"Joined channel: {self.channel}")

        connection.cap("REQ", "twitch.tv/commands")
    
    def on_pubmsg(self, connection, event):
        text = event.arguments[0]

        if text.startswith('!playsound'):
            self.handle_playsound(text)            

    def on_privmsg(self, connection, event):
        logging.info(event)

    def on_whisper(self, connection, event):
        logging.info("whisper: " + event.arguments[0])

        if "Successfully" in event.arguments[0]:
            self.last_sent_playsound_time = self.last_playsound_time = datetime.datetime.now()

            self.start_playsound_timer()

        elif "Another user played a sample too recently." in event.arguments[0]:
            last_playsound_time = get_latest_playsound_time(config.PLAYSOUND_COOLDOWN)
            if last_playsound_time:
                logging.info(f"Playsound used too recently. Found latest playsound at: {self.last_playsound_time}")
                self.last_playsound_time = last_playsound_time

                self.start_playsound_timer()
            else:
                self.last_playsound_time = datetime.datetime.now()

                self.start_playsound_timer()

    def on_playsound_played(self, playsound_time):
        if self.last_playsound_time == playsound_time:
            return

        logging.info(f"Found latest playsound at: {playsound_time}. Updating timer.")
        self.last_playsound_time = playsound_time

        self.start_playsound_timer()

    def handle_playsound(self, text):
        tokens = text.split(' ')
        if len(tokens) < 2:
            return

        if tokens[1] not in self.playsounds:
            return

        if (datetime.datetime.now() - self.last_playsound_time).seconds < config.PLAYSOUND_COOLDOWN:
            return

        self.last_playsound_time = datetime.datetime.now()
        self.start_playsound_timer()

        logging.info(f'Played sound detected: {text}.')

    def start_playsound_timer(self):
        if self.timer is not None:
            self.timer.cancel()

        playsound_time = max(
            self.last_playsound_time + datetime.timedelta(seconds=config.BOT_COOLDOWN),
            self.last_sent_playsound_time + datetime.timedelta(seconds=config.PLAYSOUND_INTERVAL) + datetime.timedelta(seconds=config.BOT_COOLDOWN))
        if playsound_time <= datetime.datetime.now():
            seconds_left = 0
        else:
            seconds_left = (playsound_time - datetime.datetime.now()).seconds

        logging.info(f'Playing sound in {seconds_left} seconds.')

        self.timer = threading.Timer(seconds_left, self.send_playsound)
        self.timer.start()

        logging.info(f'Timer set to play sound at {playsound_time.strftime("%Y-%m-%d %H:%M:%S")}')

    def send_playsound(self):
        if self.api.is_channel_live(config.CHANNEL):
            logging.info('Sending: !playsound snoring')
            self.connection.privmsg(self.channel, '!playsound snoring')
        else:
            logging.info('Channel is not live, not sending message.')

            self.last_playsound_time = datetime.datetime.now()
            self.start_playsound_timer()


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--playsounds', action='store_true', default=False)
    parser.add_argument('-t', '--time', type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S'))
    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    logging.basicConfig(level=logging.INFO, format=config.LOGGING_FORMAT)

    playsounds = []
    if args.playsounds:
        playsounds = get_playsounds(config.PLAYSOUND_URL)

    bot = TestBot(playsounds, args.time)
    bot.start()
    

if __name__ == '__main__':
    main()