# coding: utf-8

# # Assignment 3:  Recommendation systems
#
# Here we'll implement a content-based recommendation algorithm.
# It will use the list of genres for a movie as the content.
# The data come from the MovieLens project: http://grouplens.org/datasets/movielens/
# Note that I have not provided many doctests for this one. I strongly
# recommend that you write your own for each function to ensure your
# implementation is correct.

# Please only use these imports.
from collections import Counter, defaultdict
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
import urllib.request
import zipfile

def download_data():
    """ DONE. Download and unzip data.
    """
    url = 'https://www.dropbox.com/s/p9wmkvbqt1xr6lc/ml-latest-small.zip?dl=1'
    urllib.request.urlretrieve(url, 'ml-latest-small.zip')
    zfile = zipfile.ZipFile('ml-latest-small.zip')
    zfile.extractall()
    zfile.close()


def tokenize_string(my_string):
    """ DONE. You should use this in your tokenize function.
    """
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(movies):
    """
    Append a new column to the movies DataFrame with header 'tokens'.
    This will contain a list of strings, one per token, extracted
    from the 'genre' field of each movie. Use the tokenize_string method above.

    Note: you may modify the movies parameter directly; no need to make
    a new copy.
    Params:
      movies...The movies DataFrame
    Returns:
      The movies DataFrame, augmented to include a new column called 'tokens'.

    >>> movies = pd.DataFrame([[123, 'Horror|Romance'], [456, 'Sci-Fi']], columns=['movieId', 'genres'])
    >>> movies = tokenize(movies)
    >>> movies['tokens'].tolist()
    [['horror', 'romance'], ['sci-fi']]
    """
    ###TODO
    movies["tokens"] = movies["genres"].apply(tokenize_string)
    return movies

def featurize(movies):
    """
    Append a new column to the movies DataFrame with header 'features'.
    Each row will contain a csr_matrix of shape (1, num_features). Each
    entry in this matrix will contain the tf-idf value of the term, as
    defined in class:
    tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    where:
    i is a term
    d is a document (movie)
    tf(i, d) is the frequency of term i in document d
    max_k tf(k, d) is the maximum frequency of any term in document d
    N is the number of documents (movies)
    df(i) is the number of unique documents containing term i

    Params:
      movies...The movies DataFrame
    Returns:
      A tuple containing:
      - The movies DataFrame, which has been modified to include a column named 'features'.
      - The vocab, a dict from term to int. Make sure the vocab is sorted alphabetically as in a2 (e.g., {'aardvark': 0, 'boy': 1, ...})
    """
    ###TODO
    frequencyOfTermInDocument = {}
    numOfUniqueDoc = Counter()
    tf_idf_value = 0
    vocab = defaultdict(lambda: 0)
    tokenList = set()

    for index, row in movies.iterrows():
        tokenList.update(row['tokens'])
    
    for term_index, term in enumerate(sorted(tokenList)):
        vocab[term] = term_index

    for index, row in movies.iterrows():
        frequencyOfTermInDocument[row['movieId']] = dict(Counter(row['tokens']))
    
    for movie in frequencyOfTermInDocument:
        numOfUniqueDoc.update(frequencyOfTermInDocument[movie].keys())

    N = len(frequencyOfTermInDocument)

    def form_csrmatrix(movies_df_row):
        movie = movies_df_row['movieId']
        max_k = max(frequencyOfTermInDocument[movie].values())
        row = []
        col = []
        data = []
        for term in frequencyOfTermInDocument[movie]:
            row.append(0)
            col.append(vocab[term])
            tf_idf_value = frequencyOfTermInDocument[movie][term] / max_k * math.log10(N / numOfUniqueDoc[term])
            data.append(tf_idf_value)

        return csr_matrix((data, (row, col)), shape=(1, len(vocab)))

    movies['features'] = movies.apply(form_csrmatrix, axis=1)
    return tuple((movies, vocab))


def train_test_split(ratings):
    """DONE.
    Returns a random split of the ratings matrix into a training and testing set.
    """
    test = set(range(len(ratings))[::1000])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]


def cosine_sim(a, b):
    """
    Compute the cosine similarity between two 1-d csr_matrices.
    Each matrix represents the tf-idf feature vector of a movie.
    Params:
      a...A csr_matrix with shape (1, number_features)
      b...A csr_matrix with shape (1, number_features)
    Returns:
      A float. The cosine similarity, defined as: dot(a, b) / ||a|| * ||b||
      where ||a|| indicates the Euclidean norm (aka L2 norm) of vector a.
    """
    ###TODO
    return (a.dot(b.T).toarray()[0][0]) / (np.linalg.norm(a.toarray()) * np.linalg.norm(b.toarray()))    


def make_predictions(movies, ratings_train, ratings_test):
    """
    Using the ratings in ratings_train, predict the ratings for each
    row in ratings_test.

    To predict the rating of user u for movie i: Compute the weighted average
    rating for every other movie that u has rated.  Restrict this weighted
    average to movies that have a positive cosine similarity with movie
    i. The weight for movie m corresponds to the cosine similarity between m
    and i.

    If there are no other movies with positive cosine similarity to use in the
    prediction, use the mean rating of the target user in ratings_train as the
    prediction.

    Params:
      movies..........The movies DataFrame.
      ratings_train...The subset of ratings used for making predictions. These are the "historical" data.
      ratings_test....The subset of ratings that need to predicted. These are the "future" data.
    Returns:
      A numpy array containing one predicted rating for each element of ratings_test.
    """
    ###TODO
    userTrainingDictionary = defaultdict(list)
    resultDictionary = {} # returned finally
    weightedAverageRating = []
    for index, row in ratings_train.iterrows():
        userTrainingDictionary.setdefault(row["userId"], []).append((row['movieId'], row['rating']))

    for index, test_movie in ratings_test.iterrows():
        moviesRatedByUser = userTrainingDictionary[test_movie['userId']]
        a_csr = movies.loc[movies['movieId'] == test_movie['movieId'], 'features'].iloc[0]

        for movieRated in moviesRatedByUser:
            b_csr = movies.loc[movies['movieId'] == movieRated[0], 'features'].iloc[0]
            aCosb = cosine_sim(a_csr, b_csr)
            if aCosb > 0:
                resultDictionary.setdefault(index,[]).append((aCosb, movieRated[1]))
        #when user has not rated any similar movie
        if index in resultDictionary:
            weightedAverageRating.append(sum(s*r for s,r in resultDictionary[index])/sum(s for s,r in resultDictionary[index]))
        else:
            weightedAverageRating.append(sum(movieRated[1] for movieRated in moviesRatedByUser) \
                                                  / len(moviesRatedByUser))
    return np.array(weightedAverageRating)



def mean_absolute_error(predictions, ratings_test):
    """DONE.
    Return the mean absolute error of the predictions.
    """
    return np.abs(predictions - np.array(ratings_test.rating)).mean()
   
def main():
	download_data()
	path = 'ml-latest-small'
	ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
	movies = pd.read_csv(path + os.path.sep + 'movies.csv')
	movies = tokenize(movies)
	movies, vocab = featurize(movies)
	print('vocab:')
	print(sorted(vocab.items())[:10])
	ratings_train, ratings_test = train_test_split(ratings)
	print('%d training ratings; %d testing ratings' % (len(ratings_train), len(ratings_test)))
	predictions = make_predictions(movies, ratings_train, ratings_test)
	print('error=%f' % mean_absolute_error(predictions, ratings_test))
	print(predictions[:10])

if __name__ == '__main__':
    main()
