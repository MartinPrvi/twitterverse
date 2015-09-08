import json

import cPickle as pickle

def generate_json(users, reduced_dimensionality):
  data = []

  for i in xrange(len(users)):
    tmp_user = {}
    tmp_user['screenname'] = users[i]['screen_name']
    tmp_user['position'] = list(reduced_dimensionality[i])

    data.append(tmp_user)

  JSON = 'var data = ' + json.dumps(data)

  writer = open('js/data.json', 'w')
  writer.write(JSON)
  writer.close()

def main():
  new_users = pickle.load(open('Data/new_users.cPickle'))
  reduced_dimensionality = pickle.load(open('reduced_dimensionality.cPickle'))

  generate_json(new_users, reduced_dimensionality)

if __name__=='__main__':
  main()