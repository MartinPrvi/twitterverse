'''
  Run Forest, Run
'''
import json

import cPickle as pickle

#==================================================================================================

def generate_json(users, reduced_dimensionality, distances, count, file_name, data_name):
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
    
    nearest = list(distances[i].argsort()[:count])
    if i in nearest:
      del nearest[nearest.index(i)]
    tmp_user['nearest'] = nearest

    data.append(tmp_user)

  JSON = 'var {0} = '.format(data_name) + json.dumps(data)

  writer = open('js/{0}'.format(file_name), 'w')
  writer.write(JSON)
  writer.close()

#==================================================================================================

def main():
  new_users = pickle.load(open('Data/processed/users_filtered.cPickle'))
  reduced_dimensionality = pickle.load(open('Data/processed/tfidf_distance_reduced_dimensionality_v1.cPickle'))
  distances = pickle.load(open('Data/processed/tfidf_distance.cPickle.cPickle'))

  generate_json(new_users, reduced_dimensionality, distances, 25, 'tfidf_distance_data.json', 'tfidf_distance_data')

if __name__=='__main__':
  main()