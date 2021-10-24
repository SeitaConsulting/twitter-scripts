from twitterlib import TwitterLib
import config
import csv
import datetime
import random
import time

if __name__ == '__main__':
    print('Started at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # init
    t = TwitterLib(config)

    list_id = 1164816424260403200 #CEO
    list_members = t.get_list_members(list_id)['users']
    influencer = random.choice(list_members)
    
    finish = False
    cursor = -1
    follow_limit = 25
    count = 0
    loop = 0
    while not finish:
        res = t.get_followers(
            user_id=influencer['id'],
            count=100,
            cursor=cursor
        ) # the reason 100 is for the limit of relationship
        followers = res['users']
        cursor = res['next_cursor']

        user_ids = []
        for follower in followers:
            user_ids.append(str(follower['id']))
        user_ids2 = ','.join(user_ids)
            
        relationships = t.get_relationships(user_ids2)
        for relationship in relationships:
            if 'following' not in relationship['connections'] and 'blocking' not in relationship['connections'] and 'followed_by' not in relationship['connections']:
                res = t.follow(relationship['id'])
                print(res)
                if not 'erros' in res:
                    count += 1
                #t.mute(relationship['id'])
                time.sleep(5)

            if count == follow_limit:
                finish = True
                break

        loop += 1
        if loop % 15 == 0:
            time.sleep(925)
            
    print('Ended at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
