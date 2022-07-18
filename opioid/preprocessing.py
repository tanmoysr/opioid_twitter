"""
Opioid Project

python3 preprocess cluster0 extract_features update_features 10000
"""
import os
import json
import nltk
from nltk.cluster import KMeansClusterer
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.externals import joblib
import pickle
from gensim.models import Word2Vec
import numpy as np
import pandas as pd
import sys
import argparse


class Opioid:
    def __init__(self):
        self.uniqueWords = set([])
        self.data_dir = 'data'
        self.key_file_name_m = 'data/terms/key_terms.txt'
        self.corpus = []
        self.result = []
        self.sentences = []

    def preprocessing(self):
        count = 0
        after_cleaned_count = 0

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".txt"):
                print(os.path.join(self.data_dir, filename))
                term = filename.split('_')[0]
                with open(os.path.join(self.data_dir, filename), 'r') as t_file:
                    for l in t_file.readlines():
                        line = l.strip()
                        score = 0
                        if len(line) > 0:
                            line = json.loads(line)
                            txt = line.get('text')

                            if "place" in line and \
                                    not line.get('place') is None and \
                                    not txt.lower().startswith('rt ') and \
                                    term.lower() in txt.lower():
                                txt = txt.replace('\n', '')
                                txt = re.sub(r'https?:\/\/.*', '', txt, flags=re.MULTILINE)
                                txt = re.sub(r'@[\w]+', '', txt, flags=re.MULTILINE)
                                txt = txt.strip()
                                self.sentences.append(txt.split())
                                self.uniqueWords.union(txt.split())
                                place = line.get('place')
                                self.corpus.append(txt)
                                self.result.append({'text': txt.lower(), 'place': place, 'score': 0})
                                # print(self.result)

                                # bow = txt.split()
                                # uniqueWords = set(uniqueWords).union(set(bow))

                                # print(count, txt)
                                line.update({'score': score, 'text': txt})
                                after_cleaned_count += 1
                            count += 1

        print('total: ', count)
        print('total after cleaned: ', after_cleaned_count)

    def clustering0(self, is_train=True):
        print('*** Clustering 0 In Progress ...')

        if is_train:
            print('Training Model...')
            model = Word2Vec(self.sentences, min_count=1)
            model.save("model/word2vec.model")
        else:
            print('Loading Model...')
            model = Word2Vec.load("model/word2vec.model")

        NUM_CLUSTERS = 2
        X = model[model.wv.vocab]
        print('Clustering...')
        # kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance, repeats=25)
        # assigned_clusters = kclusterer.cluster(X, assign_clusters=True)
        # print(assigned_clusters)

        words = list(model.wv.vocab)
        kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance, repeats=25)
        assigned_clusters = kclusterer.cluster(X, assign_clusters=True)
        for i, word in enumerate(words):
            print(word + ":" + str(assigned_clusters[i]))

        keywords = []
        return keywords

    def clustering1(self, is_train=True):
        print('*** Clustering 1 In Progress ...')

        keywords = []
        return keywords

    def get_manual_keywords(self):
        keywords = []
        with open(self.key_file_name_m, 'r') as f:
            for w in f.readlines():
                keywords.append(w.strip().lower())
        return keywords

    def tweet_ranking(self, k, km):
        self.load_features()
        print('*** Tweet Ranking In Progress ...')

        outfile = 'out_' + str(k) + '.txt'

        with open(outfile, 'w+') as f:
            found = False
            for l in self.result:
                line = json.dumps(l).lower()
                for key in km:
                    if key in line:
                        f.write(line + '\n')
                        found = True
                        break

                if found:
                    k -= 1
                    if k < 0:
                        break

    def feature_extraction(self):
        print('*** Feature Extraction In Progress ...')
        # tf-idf based vectors
        tf = TfidfVectorizer(analyzer='word',
                             ngram_range=(1, 2),
                             stop_words="english",
                             lowercase=True,
                             max_features=5000000)

        # Fit the model
        tf_transformer = tf.fit(self.corpus)

        # save your model in disk
        joblib.dump(tf_transformer, 'model/tfidf.pkl')

    def load_features(self):
        print('*** Load Features In Progress...')
        # Testing phase
        tfidf = joblib.load('model/tfidf.pkl')
        # feature_names = np.array(tfidf.get_feature_names())
        # new_doc = 'This document is the second document.'

        doc = 0
        # tfidf_ = tfidf.transform(self.corpus)
        # features = tfidf.get_feature_names()
        #
        # self.top_feats_in_doc(tfidf_, features, 0, 10)

        # responses = tfidf.transform(new_doc)

    def update_features(self, k):
        return None

    def top_tfidf_feats(self, row, features, top_n=100):
        ''' Get top n tfidf values in row and return them with their corresponding feature names.'''
        topn_ids = np.argsort(row)[::-1][:top_n]
        top_feats = [(features[i], row[i]) for i in topn_ids]
        df = pd.DataFrame(top_feats)
        df.columns = ['feature', 'tfidf']
        df.to_csv('top_features.csv')
        return df

    def top_feats_in_doc(self, Xtr, features, row_id, top_n=100):
        ''' Top tfidf features in specific document (matrix row) '''

        row = np.squeeze(Xtr[row_id].toarray())
        return self.top_tfidf_feats(row, features, top_n)

    def get_ifidf_for_words(self, feature_names, tfidf, text):
        tfidf_matrix = tfidf.transform([text]).todense()
        feature_index = tfidf_matrix[0, :].nonzero()[1]
        tfidf_scores = zip([feature_names[i] for i in feature_index], [tfidf_matrix[0, x] for x in feature_index])
        print(dict(tfidf_scores))
        return dict(tfidf_scores)


if __name__ == '__main__':
    is_preprocessing = False
    is_clustering0 = False
    is_clustering1 = False
    is_extract_features = True
    is_update_features = False
    is_tweet_ranking = False

    print(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("-P", type=bool, help="is_preprocessing", default=True)
    parser.add_argument("-W", type=bool, help="is_word2vec", default=False)
    parser.add_argument("-C0", type=bool, help="is_clustering0", default=False)
    parser.add_argument("-C1", type=bool, help="is_clustering1", default=False)
    parser.add_argument("-F", type=bool, help="is_extract_features", default=False)
    parser.add_argument("-U", type=bool, help="is_update_features", default=True)
    parser.add_argument("-R", type=bool, help="is_tweet_ranking", default=True)
    parser.add_argument("-k", type=int, help="top K tweets", default=1000)
    args = parser.parse_args()
    print(args.k)

    opioid = Opioid()
    if args.P:
        opioid.preprocessing()  # It will stored the data temporarily in Opioid class

    k0, k1 = [], []
    if args.C0:
        k0 = opioid.clustering0(args.W) # K-mean culstering (K=2) # W2Vec then clustering with it

    if args.C1:
        k1 = opioid.clustering1(args.W)  # K-mean culstering (K=2)

    if args.F:
        opioid.feature_extraction() #TFIDF. Giving score for each word.

    if args.U:
        km = opioid.get_manual_keywords()
        km = set(km).union(set(k0)).union(set(k1))
        opioid.update_features(km)  # updating the score of the keyword

    if args.R:
        print(list(km))
        opioid.tweet_ranking(args.k, list(km))  # Summing the tfidf of each word in a sentence
