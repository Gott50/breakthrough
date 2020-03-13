from bot.tasks import create_task
from bot.time_util import sleep, get_time


def is_time():
    hour = int(get_time('this_hour'))
    return 10 < hour < 22


for i in range(10):
    sleep(50 * 60)
    print("result %s: %s " % (i, create_task(sleep=50)))

    while not is_time():
        sleep(50 * 60)
