import re

import numpy as np


class TFIDF:
    def __init__(self, corpus:list[str]) -> None:
        self.raw_corpus = corpus
        self.tokenized_corpus = []
        self.vocabulary = set()
        # 记录每篇文档不重复词
        self.doc_word_set = [set() for i in range(len(corpus))]
        for i, doc in enumerate(corpus):
            tokenized_doc = []
            sentence = doc.split()
            for word in sentence:
                word = re.sub('[^\w\s]','', word)
                word = word.lower()
                self.vocabulary.add(word)
                tokenized_doc.append(word)
                self.doc_word_set[i].add(word)
            self.tokenized_corpus.append(tokenized_doc)
        self.vocabulary = list(self.vocabulary)

        self.__tf_list = []
        self.__tf_list = self.__calc_tf()

        self.__df_dict = self.__count_df()
        self.__idf_dict = {}
        for word, df in self.__df_dict.items():
            self.__idf_dict[word] = np.log10(len(corpus)/df)
        self.vocabulary_2_idx = {}
        for i, w in enumerate(self.vocabulary):
            self.vocabulary_2_idx[w] = i

        self.doc_vector = self.__get_tf_idf_vector()

    def get_most_similar_doc_by_word(self, sentence:str, top_k:int = 1):
        raw_word_list = sentence.split()
        query_vec = np.zeros(shape=(len(raw_word_list),))
        for i, word in enumerate(raw_word_list):
            word = re.sub('[^\w\s]','', word)
            word = word.lower()
            query_vec[i] = self.vocabulary_2_idx.get(word, len(self.vocabulary))
           
        target_vector = self.doc_vector[:,query_vec.astype(np.int32)]
        target_vector_sum = np.sum(target_vector, axis=1)
        arg_sort = np.argsort(target_vector_sum)[::-1]
        value = target_vector_sum[arg_sort]
        return arg_sort[0:top_k], value[0:top_k]

            
    def __count_df(self):
        df_dict = {}
        for word in self.vocabulary:
            df_dict[word] = 0
        for word_set in self.doc_word_set:
            for word in word_set:
                df_dict[word] += 1
        return df_dict

    def __calc_tf(self):
        doc_idx_to_word_num = [{} for i in range(len(self.tokenized_corpus))]
        for i, doc in enumerate(self.tokenized_corpus):
            for word in doc:
                if word not in doc_idx_to_word_num[i]:
                    doc_idx_to_word_num[i][word] = 1
                else:
                    doc_idx_to_word_num[i][word] += 1
        tf_list = [{} for i in range(len(self.tokenized_corpus))]
        for i in range(len(self.tokenized_corpus)):
            for word in self.vocabulary:
                tf_list[i][word] = doc_idx_to_word_num[i].get(word, 0)/len(self.tokenized_corpus[i])
        return tf_list


    def __get_tf_idf_vector(self):
        vector = np.zeros((len(self.tokenized_corpus), len(self.vocabulary)+1))
        for doc_idx in range(len(self.tokenized_corpus)):
            for word_idx, word in enumerate(self.vocabulary):
                vector[doc_idx][word_idx] = self.__tf_list[doc_idx][word] * self.__idf_dict[word]
            vector[doc_idx][-1] = 0
        return vector

