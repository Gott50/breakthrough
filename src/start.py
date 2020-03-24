from bot.tasks import create_task
from bot.time_util import sleep, get_time

factor = 5
counter = 0


def is_time():
    hour = int(get_time('this_hour'))
    return 9 < hour < 23


while True:
    while not is_time():
        sleep(50 * 60 / factor)

    result = create_task(sleep=50)
    counter += result
    print("result %s: %s " % (counter, result))

    sleep(50 * 60 / factor)
