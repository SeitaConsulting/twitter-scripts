from twitterlib import TwitterLib
import config
import csv
import datetime
import time

if __name__ == '__main__':
    print('Started at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # init
    t = TwitterLib(config)

    data = []
    with open('{0}/responses.csv'.format(config.wd), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
            
    now = datetime.datetime.now()
    lastday = '{0:%y%m%d}'.format(now-datetime.timedelta(days=config.lastday))
    #lastday = '200520' # to specify date
    
    has_removed = []
    i = len(data)
    for row in data:
        if row[0] < lastday:
            print(row[1])
            res = t.remove(row[1])
            if not 'error' in res:
                has_removed.append(row)
            time.sleep(5)

    for row in has_removed:
        data.remove(row)
            
    with open('{0}/responses.csv'.format(config.wd), 'w') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)
            
    print('Ended at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
