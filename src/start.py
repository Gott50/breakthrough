import os

from bot.tasks import create_task
from bot.time_util import sleep, get_time

factor = int(os.environ.get('FACTOR', '1'))
start = 8
end = 22
counter = 0

print("factor: %s" % factor)
print("should do about: %s " % ((end - start) * 60 / (10 + 100 / factor)))


def is_time():
    hour = int(get_time('this_hour'))
    return start <= hour <= end


while True:
    while not is_time():
        print("hour: %s" % get_time('this_hour'))
        sleep(50 * 60 / factor)

    result = create_task(sleep=50, factor=factor)
    counter += result
    print("result %s: %s " % (counter, result))

    sleep(50 * 60 / factor)
