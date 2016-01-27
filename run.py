import json

import cPickle as pickle

def generate_json(users, reduced_dimensionality):
  data = []

  for i in xrange(len(users)):
    tmp_user = {}
    tmp_user['screenname'] = users[i]['screen_name']
    tmp_user['name'] = users[i]['name']
    tmp_user['description'] = users[i]['description']
    tmp_user['followers_count'] = users[i]['followers_count']
    tmp_user['profile_image_url'] = users[i]['profile_image_url']
    tmp_user['url'] = users[i]['url']
    tmp_user['position'] = list(reduced_dimensionality[i])

    data.append(tmp_user)

  JSON = 'var data = ' + json.dumps(data)

  writer = open('js/data.json', 'w')
  writer.write(JSON)
  writer.close()

def main():
  new_users = pickle.load(open('Data/new_users.cPickle'))
  reduced_dimensionality = pickle.load(open('Data/reduced_dimensionality.cPickle'))

  generate_json(new_users, reduced_dimensionality)

if __name__=='__main__':
  main()