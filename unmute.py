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
    
    cursor = -1 #default: -1
    loop = 0
    while not cursor == 0:
        res = None
        success = False
        while not success:
            try:
                endpoint = 'https://api.twitter.com/1.1/mutes/users/ids.json'
                params = {
                    'stringify_ids': True,
                    'cursor': cursor
                }
                print('cursor:', cursor)
                res = t.get(endpoint, params)
                cursor = res['next_cursor']
                for id_strs in res['ids']:
                    t.unmute(id_strs)
                    print('muted')
                    time.sleep(2)
                success = True
            except:
                time.sleep(30)

        print('waiting for 10s.')
        time.sleep(10)
        
        loop += 1
        if loop % 15 == 0:
            print('waiting for 925s.')
            time.sleep(925)
            
    print('Ended at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
