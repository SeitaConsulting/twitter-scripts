from twitterlib import TwitterLib
import config
import csv
import datetime
import json
import random
import time

if __name__ == '__main__':
    print('Started at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # init
    t = TwitterLib(config)

    page = 1
    while True:
        users = t.search_users('大学 ビジネス', page)
        for user in users:
            if 'id' in user:
                t.add_to_list(1305767898028236800, user['id'])
            page += 1
            time.sleep(1)
            
    print('Ended at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
