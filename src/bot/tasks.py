import os

from bot import Bot
from bot.proxy import get_proxy


def create_task(sleep=5, print=print, factor=1):
    result = 0
    proxy = get_proxy()
    if not proxy["port"] is None:
        bot = init_Bot(proxy=proxy, sleep=sleep, print=print)
        try:
            print('Starting Bot at: %s' % proxy)
            result = bot.act(factor=factor)
        except Exception as e:
            print(e)
            try:
                bot.end()
            except Exception as e2:
                print(e2)
            return e

        bot.end()
    return result


def init_Bot(proxy, sleep, print=print):

    print("SELENIUM: %s" % os.environ.get('SELENIUM'))
    if os.environ.get('SELENIUM'):
        bot = Bot(proxy_ip=proxy["ip"], proxy_port=proxy["port"],
                  selenium_local_session=False,
                  print=print,
                  sleep_time=sleep)
        bot.set_selenium_remote_session(
            selenium_url="http://%s:%d/wd/hub" % (os.environ.get('SELENIUM', 'selenium'), 4444))
    else:
        bot = Bot(proxy_ip=proxy["ip"], proxy_port=proxy["port"],
                  selenium_local_session=True,
                  print=print,
                  sleep_time=sleep)
    return bot
