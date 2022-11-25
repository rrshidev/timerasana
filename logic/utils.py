import json
from pytz import timezone
import datetime
from random import randint


class Dict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__getitem__


def callback(data):
    d = json.dumps(data, ensure_ascii=False)
    #print("SIZE", len(d.encode("utf-8")))
    return d


def get_callback(callback_data):
    return json.loads(callback_data)

    
def get_moscow_datetime():
    spb_timezone = timezone("Europe/Moscow")
    local_time = datetime.datetime.now().replace(microsecond=0)
    current_time = local_time.astimezone(spb_timezone)
    return current_time
