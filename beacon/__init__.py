
import datetime
import xml.etree.ElementTree as ET
from requests_toolbelt.threaded import pool

URL = "https://beacon.nist.gov/rest/record/{:0.0f}"
MIN_TIME = 1378395540


class Beacon(dict):
    ## XML parsing stuff
    def __init__(self, xml_string):
        try:
            tree = ET.fromstring(xml_string)
            for elem in tree.iter():
                tag = elem.tag.split("}", 1)[1] 
                self[tag] = elem.text
        except ET.ParseError as e:
            raise RuntimeError("Cannot parse '{}' as XML: {}".format(
                xml_string, e))

def _urls(date_from, date_to):
    date_from = date_from.replace(second=0, microsecond=0)
    while date_from <= date_to.replace(second=0, microsecond=0):
        yield URL.format(date_from.timestamp())
        date_from = date_from + datetime.timedelta(minutes=1)

def _fetch(urls):
    p = pool.Pool.from_urls(
      urls, dict(timeout=5.0), num_processes=1)
    p.join_all()
    for response in p.responses():
        yield response


def request(date_from, date_to):
    urls = list(_urls(date_from, date_to))
    for response in _fetch(urls):
        yield Beacon(response.text)




