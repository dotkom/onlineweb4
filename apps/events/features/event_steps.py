from lettuce import *
from lxml import html
from django.test.client import Client


@before.all
def set_browser():
    world.browser = Client()


@step(r'I access the url "(.*)"')
def access_url(step, url):
    response = world.browser.get(url)
    world.dom = html.fromstring(response.content)


@step(r'I see the header "(.*)"')
def see_header(step, text):
    header = world.dom.cssselect('h1')[0]
    assert header.text == text
