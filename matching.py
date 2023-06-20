from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import config
from db.db import get_product
import pandas as pd


class StringMatching:
    @staticmethod
    def convert_to_tfidf(corpus):
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(corpus)
        return vectors, vectorizer

    @staticmethod
    def cal_cosine(s, corpus):
        vectors, vectorizer = StringMatching.convert_to_tfidf(corpus)
        s_vec = vectorizer.transform([s])

        return cosine_similarity(s_vec, vectors, dense_output=False)

    @staticmethod
    def cal_edit_distance(s, t, ratio_calc=True):
        """ cal_edit_distance:
            For all i and j, distance[i,j] will contain the
            distance between the first i characters of s and the
            first j characters of t
        """
        rows = len(s) + 1
        cols = len(t) + 1
        distance = np.zeros((rows, cols), dtype=int)

        for i in range(1, rows):
            for k in range(1, cols):
                distance[i][0] = i
                distance[0][k] = k

        for col in range(1, cols):
            for row in range(1, rows):
                if s[row - 1] == t[col - 1]:
                    cost = 0
                else:
                    cost = 1

                distance[row][col] = min(distance[row - 1][col] + 1,  # Cost of deletions
                                         distance[row][col - 1] + 1,  # Cost of insertions
                                         distance[row - 1][col - 1] + cost)  # Cost of substitutions
        if ratio_calc:
            ratio = 1 - distance[row][col] / max(len(s), len(t))
            return ratio
        else:
            return distance[row][col]

    @staticmethod
    def find(s, shop=config.main_shop["cps"]):
        product_list = get_product(shop=shop)
        corpus = [str.lower(i[1]) for i in product_list]
        #
        cosine_vectors = StringMatching.cal_cosine(str.lower(s), corpus)

        non_zeros = cosine_vectors.nonzero()

        sparse_cols = non_zeros[1]
        nr_matches = sparse_cols.size
        right_side = np.empty([nr_matches], dtype=object)
        similarity = np.zeros(nr_matches)
        val = [() for _ in range(nr_matches)]

        for index in range(0, nr_matches):
            right_side[index] = corpus[sparse_cols[index]]
            similarity[index] = cosine_vectors.data[index]
            val[index] = product_list[sparse_cols[index]]
        df = pd.DataFrame({'product': right_side,
                           'similarity': similarity,
                           'val': val})

        df.sort_values(by="similarity", inplace=True, ascending=False)
        # print(df.loc[df['similarity'].idxmax()])
        return df['similarity'].idxmax(), df

    @staticmethod
    def find_by_edit_distance(s, shop=config.main_shop["cps"]):
        product_list = get_product(shop)
        corpus = [str.lower(i[1]) for i in product_list]
        similarity = []
        for p in corpus:
            similarity.append(StringMatching.cal_edit_distance(str.lower(s), p))
        df = pd.DataFrame({'product': corpus,
                           'similarity': similarity,
                           'val': product_list})
        df.sort_values(by="similarity", inplace=True, ascending=False)
        return df['similarity'].idxmax(), df


if __name__ == '__main__':
    r = StringMatching.find("iphone 12", config.main_shop["cps"])
    print(r[1].loc[r[0]])
    # print(df.iloc[df['similarity'].argmax()])
    # print(StringMatching.cal_edit_distance(corpus[0], corpus[1]))
