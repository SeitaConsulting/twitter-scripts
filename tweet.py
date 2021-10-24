from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np
import pandas as pd
import json, config
from requests_oauthlib import OAuth1Session
import time
from datetime import datetime
import random
import csv

CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET 
twitter = OAuth1Session(CK, CS, AT, ATS)

history = []

def get_user(user_id):
  endpoint = 'https://api.twitter.com/1.1/users/show.json'
  
  params = {
    'user_id': user_id,
    'include_entities': True
  }
  
  res = twitter.get(endpoint, params=params)
  return json.loads(res.text)

def get_cursor():
  # 1629307286000260199
  cursor = open('./cursor.txt', 'r').read()
  return cursor

def set_cursor(cursor):
  f = open('./cursor_ra.txt', 'w')
  f.write(str(cursor))
  f.close()  

# 15 times per 15 mins
def get_followers(user_id, next_cursor):
  endpoint = 'https://api.twitter.com/1.1/followers/list.json'
  
  params = {
    'user_id': user_id,
    'count': 200,
    'cursor': next_cursor
  }
  
  res = twitter.get(endpoint, params=params)
  return json.loads(res.text)

def get_followers_all(user_id):
  followers = {
    'users': []
  }

  next_cursor = get_cursor()
  res = get_followers(user_id, next_cursor)
  followers['users'].extend(res['users'])
  next_cursor = res['next_cursor']
  set_cursor(next_cursor)

  return followers

# 1000 per a day
def dm(user_id, text):
  endpoint = 'https://api.twitter.com/1.1/direct_messages/events/new.json'

  params = {
    'type': 'message_create',
    'message_create': {
      'target': {
        'recipient_id': user_id
      },
      'message_data': {
        'text': text
      }
    }
  }

  res = twitter.post(endpoint, json={'event':params})
  print(res)
#  return json.loads(res.text)

def get_list_members(list_id):
  endpoint = 'https://api.twitter.com/1.1/lists/members.json'

  params = {
      'list_id': list_id
  }

  res = twitter.get(endpoint, params=params)
  return json.loads(res.text)

def search(q, i):
  endpoint = 'https://api.twitter.com/1.1/users/search.json'

  params = {
    'q': q,
    'page': i,
    'count': 20
  }

  res = twitter.get(endpoint, params=params)
  return json.loads(res.text)

def add_to_list(list_id, user_id):
  endpoint = 'https://api.twitter.com/1.1/lists/members/create.json'

  params = {
    'list_id': list_id,
    'user_id': user_id
  }

  twitter.post(endpoint, params=params)
  
def block(user_id):
  endpoint = 'https://api.twitter.com/1.1/blocks/create.json'

  params = {
    'user_id': user_id
  }

  res = twitter.post(endpoint, params=params)
  return json.loads(res.text)

def tweet(status, media_id):
  endpoint = 'https://api.twitter.com/1.1/statuses/update.json'

  params = {
    'status': status,
#    'media_ids': media_id
  }

  res = twitter.post(endpoint, params=params)
  return json.loads(res.text)

def upload(filename):
  endpoint = 'https://upload.twitter.com/1.1/media/upload.json'

  params = {
    'media': open(filename, 'rb')
  }

  res = twitter.post(endpoint, params=params)
  return json.loads(res.text)

def generate_text_img(text, fontsize=32):
  fontname = '/home/ubuntu/scripts/twitter/kokoro.otf'
  font = ImageFont.truetype(fontname, fontsize)
  img_size = np.ceil(np.array(font.getsize(text))*1.1).astype(int)
  img_size2 = (img_size[0], img_size[1]*10)
  img=Image.new('RGB', img_size2, (0, 174, 160))
  draw = ImageDraw.Draw(img)
  text_offset = (img_size - font.getsize(text))/2
  text_offset[0] = text_offset[0] + 60
  text_offset[1] = text_offset[1] - 8
  draw.text(text_offset, text, font=font, fill='#fff')
  return img

if __name__ == '__main__':
  print('Started at', datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

  with open('/home/ubuntu/scripts/twitter/business.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
  i = random.randrange(1,565,1)

  lines = None
  with open('/home/ubuntu/scripts/twitter/thinkbetter.txt') as f:
    lines = f.readlines()

  lines2 = None
  with open('/home/ubuntu/scripts/twitter/kakugen.csv') as f:
    lines2 = f.readlines()
    
  res = None
  if random.randrange(0, 2, 1) == 0:
#  if False:
    #text = l[i][3].rstrip('。')
    res = random.sample(lines2, 3)
  else:
    res = random.sample(lines, 3)
    
  status = '' + """



起業成功の心得
  """ + '・' + res[0].strip() + '' #←ここに句読点。

  #txt_img = generate_text_img(status, fontsize=32)
  #txt_img.save('/home/ubuntu/scripts/twitter/textimage.png', 'png')

  #res = upload('/home/ubuntu/scripts/twitter/textimage.png')
  
  tweet(status.replace(' ' ,''), None)
  #tweet('ビジネスの心得', res['media_id'])
  
  exit()
