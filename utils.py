import re
import cPickle as pickle

from gensim import corpora
from gensim.models.tfidfmodel import TfidfModel
from gensim.similarities.docsim import SparseMatrixSimilarity

import numpy as np

from sklearn.manifold import TSNE

hash_tags_re = re.compile(r'(?u)#\w+') # Used to find all hash tags within tweet
user_tags_re = re.compile(r'(?u)@\w+') # Used to find all users taged in tweet
tokenizer_re = re.compile(r'(?u)\w+') # Used to tokenize texts

#==================================================================================================

def reduce_dimensionality(distances, num_dimensions=3):
  distances = np.array(distances)

  tsne = TSNE(n_components=num_dimensions, random_state=0)

  reduced_dimensionality = tsne.fit_transform(distances)

  return reduced_dimensionality

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

def filter_users_ids(users, tweets):
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
    users_id[tweet['user']] = 1

  for user in users:
    if user['id'] in users_id:
      if user['ALIEN'] == None:
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
  distances = pickle.load(open('distances.cPickle'))

  print 'Started calculating'
  reduced_dimensionality = reduce_dimensionality(distances)

  pickle.dump(reduced_dimensionality, open('reduced_dimensionality.cPickle', 'wb'))

if __name__=='__main__':
  main()