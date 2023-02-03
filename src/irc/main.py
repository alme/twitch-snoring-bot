"""
main.py

@brief Main bot entrypoint.
"""

import argparse
import datetime
import logging
import threading

# pylint: disable=import-error
import config # type: ignore
import twitch_token
from api import TwitchAPI
from playsounds import get_playsounds, get_last_playsound_time

import irc.bot


class TestBot(irc.bot.SingleServerIRCBot):
    """
    IRC bot class.
    """

    def __init__(self, playsounds, time=None):
        irc.bot.SingleServerIRCBot.__init__(self, [
            (config.SERVER, config.PORT, f'oauth:{twitch_token.twitch_token.access_token}')], config.NICKNAME, config.NICKNAME)

        self.api = TwitchAPI()

        self.channel = f'#{config.CHANNEL}'
        self.playsounds = playsounds

        if time:
            self.last_playsound_time = time
        else:
            self.last_playsound_time = datetime.datetime.now(datetime.timezone.utc)

        self.last_sent_playsound_time = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

        self.start_playsound_timer()

    def on_welcome(self, connection, event):
        connection.join(self.channel)
        logging.info(f"Joined channel: {self.channel}")

        connection.cap("REQ", "twitch.tv/commands")       

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

    def start_playsound_timer(self):
        playsound_time = max(
            datetime.datetime.now(datetime.timezone.utc),
            self.last_playsound_time + datetime.timedelta(seconds=config.BOT_COOLDOWN),
            self.last_sent_playsound_time + datetime.timedelta(seconds=config.PLAYSOUND_INTERVAL) + datetime.timedelta(seconds=config.BOT_COOLDOWN))
        if playsound_time <= datetime.datetime.now(datetime.timezone.utc):
            seconds_left = 0
        else:
            seconds_left = (playsound_time - datetime.datetime.now(datetime.timezone.utc)).seconds

        logging.info(f'Playing sound in {seconds_left} seconds.')

        self.reactor.scheduler.execute_at(playsound_time, self.send_playsound)
        logging.info(f'Timer set to play sound at {playsound_time.strftime("%Y-%m-%d %H:%M:%S")}')

    def send_playsound(self):
        stream_data = self.api.get_channel_data(config.CHANNEL)

        if stream_data.is_channel_live():
            stream_live_time = stream_data.get_started_at()
            minimum_stream_live_time = stream_live_time + datetime.timedelta(seconds=config.STREAM_LIVE_MINIMUM)
            
            if datetime.datetime.now(datetime.timezone.utc) > minimum_stream_live_time:
                last_playsound_time = get_last_playsound_time()
                last_cooldown_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=config.PLAYSOUND_COOLDOWN)
                if last_playsound_time is not None and last_playsound_time >= last_cooldown_time:
                    logging.info(f'Playsound was sent in the last {config.PLAYSOUND_COOLDOWN} seconds '
                                f'(at: {last_playsound_time}), resetting timer.')

                    self.last_playsound_time = last_playsound_time
                    self.start_playsound_timer()
                else:
                    logging.info('Sending: !playsound snoring')
                    self.connection.privmsg(self.channel, '!playsound snoring')

            else:
                logging.info(f'Stream not live for long enough (minimum: {minimum_stream_live_time}), not sending message.')

                self.last_playsound_time = datetime.datetime.now(datetime.timezone.utc)
                self.start_playsound_timer()

        else:
            logging.info('Channel is not live, not sending message.')

            self.last_playsound_time = datetime.datetime.now(datetime.timezone.utc)
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