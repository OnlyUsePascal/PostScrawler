# check time correctness
from datetime import datetime, timedelta


def correctTimeOffset(inputDate, dateFormat, targetNumWeek):
    publishedTime = datetime.strptime(inputDate, dateFormat)
    timeDiff = datetime.now() - publishedTime
    # print(timeDiff.days)
    return timeDiff <= timedelta(weeks=targetNumWeek)
