from requests_oauthlib import OAuth1Session
import csv
import datetime
import json
import time
import urllib.request

class TwitterLib:

    def __init__(self, config):
        self.config = config
        self.twitter = OAuth1Session(
            config.CONSUMER_KEY,
            config.CONSUMER_SECRET,
            config.ACCESS_TOKEN,
            config.ACCESS_TOKEN_SECRET
        )
        # removable check; 1. unfollow list, 2. responses.csv
        users = self.get_list_members(1236913985535893504)['users'] #unfollow
        users += self.get_list_members(1164816424260403200)['users'] #CEO
        #users += self.get_list_members(1164857266475917312)['users'] #startup
        self.users = users

    def get(self, endpoint, params):
        res = self.twitter.get(endpoint, params=params)
        return json.loads(res.text)
    
    def post(self, endpoint, params):
        res = self.twitter.post(endpoint, params=params)
        return json.loads(res.text)

    def follow(self, user_id):
        # followable check; has_removed.csv
        with open(self.config.wd + '/has_removed.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[1] == user_id:
                    return { 'error': 'has_removed' }

        # follow by user_id
        endpoint = 'https://api.twitter.com/1.1/friendships/create.json'
        params = {
            'user_id': user_id
        }

        count = 0
        res = None
        success = False
        while not success:
            try:
                res = self.post(endpoint, params)
                success = True
            except:
                count += 1
                if count > self.config.retry:
                    return { 'error': 'over retry' }
                time.sleep(30)

        date = '{0:%y%m%d}'.format(datetime.datetime.now())
        self.set_to_responses(date, [user_id])

        return res
                
    def remove(self, user_id):
        user_ids = []
        for user in self.users:
            user_ids.append(str(user['id']))

        now = datetime.datetime.now()
        lastday = '{0:%y%m%d}'.format(now-datetime.timedelta(days=self.config.lastday))
        with open(self.config.wd + '/responses.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] > lastday:
                    user_ids.append(row[1])

        if user_id in user_ids:
            return { 'error': 'still responded or in unfollow-list' }
        
        # remove by user_id
        endpoint = 'https://api.twitter.com/1.1/friendships/destroy.json'
        params = {
            'user_id': user_id
        }

        res = None
        success = False
        while not success:
            try:
                res = self.post(endpoint, params=params)
                success = True
            except:
                time.sleep(30)
        print('removed', user_id)

        date = '{0:%y%m%d}'.format(now)
        self.set_to_has_removed(date, [user_id])
        
        return res

    def mute(self, user_id):
        endpoint = 'https://api.twitter.com/1.1/mutes/users/create.json'
        params = {
            'user_id': user_id
        }
        
        res = None
        success = False
        while not success:
            try:
                res = self.post(endpoint, params=params)
                success = True
            except:
                time.sleep(30)

        return res

    def unmute(self, user_id):
        endpoint = 'https://api.twitter.com/1.1/mutes/users/destroy.json'
        params = {
            'user_id': user_id
        }
        
        res = None
        success = False
        res = self.post(endpoint, params=params)

        return res
    
    def get_followers(self, user_id, count, cursor):
        endpoint = 'https://api.twitter.com/1.1/followers/list.json'
        params = {
            'user_id': user_id,
            'count': count, #maximum 200
            'cursor': cursor
        }

        res = self.get(endpoint, params=params)
        return res
    
    def get_list_members(self, list_id):
        endpoint = 'https://api.twitter.com/1.1/lists/members.json'
        params = {
            'list_id': list_id,
            'count': 5000
        }

        res = self.get(endpoint, params=params)
        return res

    def get_relationships(self, user_ids):
        endpoint = 'https://api.twitter.com/1.1/friendships/lookup.json'
        params = {
            'user_id': user_ids,
        }

        res = self.get(endpoint, params=params)
        return res

    def followed(self, user_id):
        endpoint = 'https://api.twitter.com/1.1/users/lookup.json'
        params = {
            'user_id': user_id
        }

        res = self.get(endpoint, params=params)
        print(res)
        return True
    
    def get_rate_limit_status(self):
        endpoint = 'https://api.twitter.com/1.1/application/rate_limit_status.json'
        params = {}
        res = self.get(endpoint, params)
        return res

    def search_users(self, query, page):
        endpoint = 'https://api.twitter.com/1.1/users/search.json'
        params = {
            'q': query,
            'count': 20,
            'page': page
        }
        res = self.get(endpoint, params)
        return res

    def add_to_list(self, list_id, user_id):
        endpoint = 'https://api.twitter.com/1.1/lists/members/create.json'
        params = {
            'list_id': list_id,
            'user_id': user_id
        }
        res = self.post(endpoint, params)
        return res
    
    def screen_names_to_user_ids(self, screen_names):
        print('=== screen_names to user_ids START ===')

        screen_names_sliced = []
        size = 100
        for i in range(0, len(screen_names), size):
            screen_names_sliced.append(screen_names[i:i+size])
        
        print('Splited?:')
        users = []
        for array in screen_names_sliced:
            print(array)
            print(len(array))
            
            endpoint = 'https://api.twitter.com/1.1/users/lookup.json'
            params = {
                'screen_name': ','.join(array)
            }

            res = None
            success = False
            while not success:
                try:
                    res = self.post(endpoint, params)
                    success = True
                except Exception as e:
                    print('Error:')
                    print(e)
                    print('sleeping for 30s.')
                    time.sleep(30)
            users += res


        user_ids = []
        for user in users:
            user_ids.append(user['id_str'])

        print('=== screen_names to user_ids END ===')
        return user_ids

    def set_to_has_removed(self, date, user_ids):
        data = []

        # read has_removed
        with open('{0}/has_removed.csv'.format(self.config.wd), newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row)
                
        # append or update
        for user_id in user_ids:
            found = False
            for row in data:
                if row[1] == user_id:
                    row[0] = date
                    found = True
            if not found:
                # write has_removed
                with open('{0}/has_removed.csv'.format(self.config.wd), 'a') as f:
                    tmp = date + ',' + user_id + '\n'
                    f.write(tmp)
    
    def set_to_responses(self, date, user_ids):
        data = []

        # read responses
        with open('{0}/responses.csv'.format(self.config.wd), newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row)

        # append or update
        for user_id in user_ids:
            found = False
            for row in data:
                if row[1] == user_id:
                    if row[0] < date:
                        row[0] = date
                    found = True
            if not found:
                data.append([date, user_id])

        # sort
        data = sorted(data, key=lambda x: x[0])
                
        # write responses
        with open('{0}/responses.csv'.format(self.config.wd), 'w') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)        
