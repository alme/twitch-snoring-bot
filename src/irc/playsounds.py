import lxml.html as LH
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