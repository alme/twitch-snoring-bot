import config
import datetime
import lxml.html as LH
import os.path
import requests

def get_playsounds(url):
    response = requests.get(url)

    root = LH.fromstring(response.content)
    table = root.xpath('//table[@class="ui collapsing single line compact table"]')[0]
    if len(table) == 0:
        raise Exception("Couldn't find <table> element. Page structure may have changed.")

    playsounds = set()
    sounds = table.xpath('//tr/td[1]')
    if len(sounds) == 0:
        raise Exception("Couldn't find playsound text. Page structure may have changed.")

    for sound in sounds:
        playsounds.add(sound.text)

    return playsounds


def get_last_playsound_time():
    try:
        with open(config.TIMESTAMP_FILE, 'r') as f:
            timestamp_str = f.read()
            timestamp = datetime.datetime.fromisoformat(timestamp_str).replace(tzinfo=datetime.timezone.utc)

            return timestamp

    except FileNotFoundError:
        return None