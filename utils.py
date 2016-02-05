import re
import cPickle as pickle

from gensim import corpora
from gensim.models.tfidfmodel import TfidfModel
from gensim.similarities.docsim import SparseMatrixSimilarity

import numpy as np

from sklearn.manifold import TSNE

from Data import clean_dump

hash_tags_re = re.compile(r'(?u)#\w+') # Used to find all hash tags within tweet
user_tags_re = re.compile(r'(?u)@\w+') # Used to find all users taged in tweet
tokenizer_re = re.compile(r'(?u)\w+') # Used to tokenize texts

#==================================================================================================

def reduce_dimensionality(distances, num_dimensions=3):
  distances = np.array(distances)

  tsne = TSNE(n_components=num_dimensions, random_state=0, metric='precomputed')

  reduced_dimensionality = tsne.fit_transform(distances)

  return reduced_dimensionality

#==================================================================================================

def user_communications(tweets, new_users):
  """
    From every tweet, extract the user mentioned.

    Parameters
    ----------
    tweets : list
      The tweets list
    new_users : list
      A list of users

    Returns
    -------
      user_coms : dict
        A dictionary, where the keys are user ids, and values are dictionaries of user_ids as keys
        and number of mentions of this user.
  """
  user_coms = {}
  user_screename_map = {}
  for user in new_users:
    user_coms[user['id']] = []
    user_screename_map['@' + user['screen_name']] = user['id']

  for tweet in tweets:
    user_name_list = user_tags_re.findall(tweet['text'])
    
    user_id_list = []
    for user_name in user_name_list:
      if user_name in user_screename_map:
        user_id_list.append(user_screename_map[user_name])

    if tweet['in_reply_to_user_id'] is not None:
      user_id_list.append(tweet['in_reply_to_user_id'])
    
    if tweet['user'] in user_coms:
      user_coms[tweet['user']] += set(user_id_list)

  for user_id in user_coms:
    com_list = user_coms[user_id]

    com_counts = {}
    for com_user_id in com_list:
      com_counts[com_user_id] = com_counts.get(com_user_id, 0) + 1

    user_coms[user_id] = com_counts

  return user_coms

#==================================================================================================

def distance_user_communications(new_users, user_coms):
  """
  """
  distance_matrix = np.zeros((len(new_users), len(new_users)))

  for i in xrange(len(new_users)):
    user_i = new_users[i]['id']
    for j in xrange(i+1, len(new_users)):
      user_j = new_users[j]['id']

      if user_j not in user_coms[user_i] and user_i not in user_coms[user_j]:
        distance_matrix[i, j] = 0.0
        distance_matrix[j, i] = 0.0
      else:
        user_i_count = user_coms[user_i].get(user_j, 0.0)
        user_j_count = user_coms[user_j].get(user_i, 0.0)

        distance = weighted_mean_distance([user_i_count, user_j_count], [1.0, 1.0])
        distance_matrix[i, j] = distance
        distance_matrix[j, i] = distance

  distance_matrix = np.max(distance_matrix) - distance_matrix
  np.fill_diagonal(distance_matrix, 0.0)

  return distance_matrix

#==================================================================================================

def weighted_mean_distance(x, w):
  """
  """
  if len(x) != len(w):
    raise ValueError('Size of w={0} is not the same as size of x={1}'.format(len(w), len(x)))

  num = sum([x[i] * w[i] for i in xrange(len(x))])
  den = sum(w)

  return float(num) / float(den)

#==================================================================================================

def calculate_distance(tfidf_scores, vocab_size):
  """
    Calculates the distance between each of the texts in tfidf_scores, and returns a matrix
    of distances

    Parameters
    ----------
    tfidf_scores : list
      The tfidf scores of every word in every text
    vocab_size : int
      The size of the vocab

    Returns
    -------
    distance : list
      The distance between each of the texts
  """
  cosine_sim = SparseMatrixSimilarity(tfidf_scores, num_features=vocab_size)

  distance = []
  i=0
  for row in tfidf_scores:
    print i
    i += 1
    distance.append(1 - cosine_sim[row])

  return distance

#==================================================================================================

def calculate_tfidf(user_tweets):
  """
    Calculates tfidf scores for every word in every text

    Parameters
    ----------
    user_tweets : list
      The tweets of every user

    Returns
    -------
    tfidf_scores : list
      Tfidf values for every word in every text
    dictionary_size : int
      Size of the dictionary
  """
  tokenized_texts = []

  # First tokenize all texts
  for user_tweet in user_tweets:
    tokenized_texts.append(tokenize_text(user_tweet))

  # Then make a dictionary
  dictionary = corpora.Dictionary(tokenized_texts)

  # Then calculate BOW
  corpus = [dictionary.doc2bow(tokenized_tweet) for tokenized_tweet in tokenized_texts]

  # Calculate tfidf score
  tfidf = TfidfModel(corpus)

  tfidf_score = [tfidf[corpus_item] for corpus_item in corpus]

  return tfidf_score, len(dictionary.keys())

#==================================================================================================

def tokenize_text(text):
  """
    Tokenizes the text and returns a list of words in it

    Parameters
    ----------
    text : string
      The text to be tokenized

    Returns
    -------
    words_in_text : list
      A list of the words in the text
  """
  # First find the hashtags
  found_hash_tags = hash_tags_re.findall(text)

  # Then remove the hash tags from the text and remove the user tags from the text
  text = hash_tags_re.sub(' ', text)
  text = user_tags_re.sub(' ', text)

  # Then tokenize the text
  text = text.lower()
  words_in_text = tokenizer_re.findall(text)

  # Then add all the hash tags
  words_in_text.extend(found_hash_tags)

  return words_in_text

#==================================================================================================

def filter_users_ids(users, tweets,min_tweets = 0):
  """
    Filters out users that don't have tweets and that the ALIEN tag is set to None

    Parameters
    ----------
    users : list
      The users list
    tweets : list
      The tweets

    Returns
    -------
    users_id : dict
      The ids of the users
  """
  users_id = {}
  for tweet in tweets:
    users_id[tweet['user']] = users_id.get(tweet['user'],0)+1

  for user in users:
    if users_id.get(user['id'],0) < min_tweets:
      if user['id'] in users_id:
        del users_id[user['id']]


  return users_id

#==================================================================================================

def filter_users(users, users_id):
  """
    Returns a list of users who have a user id in users_id

    Parameters
    ----------
    users : list
      The users list
    users_id : dict/list
      IDs of the users that you want to be included in the resulting dict

    Returns
    -------
    new_users : list
      A list of filtered_users
  """
  new_users = []

  for user in users:
    if user['id'] in users_id:
      new_users.append(user)

  return new_users

#==================================================================================================

def merge_user_tweets(users_id, tweets, new_users):
  """
    Returns a list of user tweets

    Parameters
    ----------
    users_id : dict
      The user dict where we will get their ids
    tweets : list
      The tweets
    new_users : list
      The users, so i can put the tweets in order

    Returns
    -------
    user_tweets : list
      A list of the tweets
  """
  user_tweets_dict = {}
  for user_id in users_id:
    user_tweets_dict[user_id] = []

  for tweet in tweets:
    if tweet['user'] in users_id:
      user_tweets_dict[tweet['user']].append(tweet['text'])

  user_tweets = []
  for user in new_users:
    user_tweets.append(' '.join(user_tweets_dict[user['id']]))

  return user_tweets

#==================================================================================================

def main():
  
  #clean_dump.run()
  print 'clean_dump finished ====================================='
  users = pickle.load(open('Data/export/users.cPickle','rb'))
  #users = clean_dump.users
  print 'loaded users'
  tweets = pickle.load(open('Data/export/tweets.cPickle','rb'))
  #tweets = clean_dump.tweets
  print 'loaded tweets'
  
  
  #================================================================================================
  '''Filter User Ids'''
  users_id = filter_users_ids(users, tweets,min_tweets = 20)
  print len(users)
  users = filter_users(users, users_id)
  print len(users)
  print 'filtered users'
  
  pickle.dump(users, open('Data/processed/users_filtered.cPickle', 'wb'), 2)
  print 'dumped users'
  
  #================================================================================================
  '''Generate User Coms'''
  # tweets = pickle.load(open('Data/mk_tweets_2015.cPickle', 'rb'))
  # new_users = pickle.load(open('Data/new_users.cPickle', 'rb'))
  print 'user_communications'
  user_coms = user_communications(tweets, users)
  print 'dumping user_communications'
  pickle.dump(user_coms, open('Data/processed/user_coms.cPickle', 'wb'), pickle.HIGHEST_PROTOCOL)
  print 'done user_communications'
  
  #================================================================================================
  '''Generate Distance Matrix'''
  # new_users = pickle.load(open('Data/new_users.cPickle', 'rb'))
  # user_coms = pickle.load(open('Data/user_coms.cPickle', 'rb'))

  print 'start distance matrix'
  distance_matrix = distance_user_communications(users, user_coms)
  print 'finish distance matrix'
  pickle.dump(distance_matrix, open('Data/processed/weighted_minus_distance_users_com_v1.cPickle', 'wb'), 2)
  
  #distance_matrix = pickle.load(open('Data/processed/weighted_minus_distance_users_com_v1.cPickle','rb'))
  print 'dumped distance matrix'
  #================================================================================================
  '''Reduce Dimensionality'''
  print 'start reduce dimensionality'
  #distance_matrix = np.array(pickle.load(open('v7_weighted_minus_distance_users_com.cPickle', 'rb')))
  distance_matrix[distance_matrix < 0.0] = 0.0
  distance_matrix = np.nan_to_num(distance_matrix)

  print 'started calculating reduce dimensionality'
  reduced_dimensionality = reduce_dimensionality(distance_matrix)
  print 'finish calculating reduce dimensionality'

  pickle.dump(reduced_dimensionality, open('Data/processed/weighted_minus_user_com_reduced_dimensionality_v1.cPickle', 'wb'))
  print 'dumped reduce dimensionality'

if __name__=='__main__':
  main()
