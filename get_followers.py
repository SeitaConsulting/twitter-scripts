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
    
    users = []
    cursor = 1671984091574487771 #default: -1
    loop = 0
    while not cursor == 0:
        res = None
        success = False
        while not success:
            try:
                endpoint = 'https://api.twitter.com/1.1/friends/list.json'
                params = {
                    'count': 200,
                    'cursor': cursor
                }
                print('cursor:', cursor)
                res = t.get(endpoint, params)
                for user in res['users']:
                    data = []
                    with open('{0}/responses.csv'.format(config.wd), newline='') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            data.append(row)

                    found = False
                    for row in data:
                        if row[1] == user['id_str']:
                            found = True
                            print('skipped: already exists')
                    if not found:
                        with open(config.wd + '/responses.csv', 'a') as f:
                            now = datetime.datetime.now()
                            date = '{0:%y%m%d}'.format(now)
                            print(date + ',' + user['id_str'], file=f)
                        print('added:', user['id_str'])
                success = True
            except:
                time.sleep(30)

        users += res['users']
        cursor = res['next_cursor']
        print('waiting for 10s.')
        time.sleep(10)
        
        loop += 1
        if loop % 15 == 0:
            print('waiting for 925s.')
            time.sleep(925)
            
    print('Ended at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
