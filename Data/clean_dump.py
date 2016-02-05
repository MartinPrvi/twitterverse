import bson
import pprint
import cPickle


users   = []
set_user_ids  = set([])

tweets  = []

#==================================================================================================

def clean_users():
  global users
  global set_user_ids
  
  clean_users = []

  remove_fields = [ '_id',
                    'created_at',
                    'favourites_count',
                    'friends_count',
                    'location',
                    'statuses_count',
                    'updated_FL_FR',
                    'updated_info']
  
  
  for user in users:
    if user['ALIEN'] == False:
      

      for f in remove_fields:
        try: del user[f]
        except: pass
      
      clean_users.append(user)
      set_user_ids.add(user['id'])

  users = clean_users
  
  print 'cleaned users'
  
#==================================================================================================

def clean_tweets():
  global tweets
  global set_user_ids
  
  remove_fields  = ['_id',
              			'RT',
                  	'created_at',
                    'in_reply_to_status_id',
                    'retweeted_status',
                    'source',
                    'updated_info',
                    'retweet_count'
                    'favorite_count',
                  ]
  clean_tweets = []
  for i, tweet in enumerate(tweets):
    
    if tweet['user'] in set_user_ids:
      for f in remove_fields:
        try:
          del tweet[f]
        except:
          pass
      clean_tweets.append(tweet)
  
  tweets = clean_tweets
  
  print 'cleaned tweets'

#==================================================================================================

def decode_bson(collection):
  with open('Data/'+collection+'.bson','rb') as f:
    data = bson.decode_all(f.read())
  print 'decoded',collection,'bson'
  return data
  
#==================================================================================================


def run():
  global users
  global tweets
  users   = decode_bson('users')
  tweets  = decode_bson('tweets')
  
  
  clean_users()
  cPickle.dump(users,open('Data/export/users.cPickle','wb'),2)

  print 'dump users'

  clean_tweets()
  cPickle.dump(tweets,open('Data/export/tweets.cPickle','wb'),2)
  print 'dump tweets'
  
  
  
#==================================================================================================
if __name__ == "__main__":
  run()