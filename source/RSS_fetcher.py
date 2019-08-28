import os
import pytz
import requests
import re
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET
import time


def clean_html(raw_html):
    reg1 = re.compile('<.*?>')
    reg2 = re.compile('&nbsp;')
    clean_text = re.sub(reg1, '', raw_html)
    cleaner_text = re.sub(reg2, '', clean_text)
    return cleaner_text


def lambda_handler(event, context):
    RSS_PAGE = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
    POST_HEADERS = {"Content-Type": "application/json"}
    GET_HEADERS = {"Accept": "application/xml", "Content-Type": "application/xml"}
    ADDRESS = os.environ['WEBHOOK_URL']

    xml = requests.get(RSS_PAGE, headers=GET_HEADERS)
    root = ET.fromstring(xml.text)

    for entry in root.iter('item'):

        published_datetime = datetime.strptime(entry.find(
        'pubDate').text,'%a, %d %b %Y %H:%M:%S %z')
        yesterday_datetime = datetime.now(pytz.utc) - timedelta(days=1)

        if published_datetime < yesterday_datetime:
            continue
        description = clean_html(entry.find('description').text)
        payload = "{\"Content\":\""+entry.find(
        'title').text+"\\n\\n"+entry.find(
        'pubDate').text+"\\n\\n"+description+"\\n\\n"+entry.find(
            'link').text+"\"}"
        printable = "\\n".join(payload.split("\n"))
        response = requests.post(ADDRESS, data=printable.encode('utf-8'),
                                 headers=POST_HEADERS)
        print(response.status_code)
        print()
        time.sleep(1)

    return "Done"

