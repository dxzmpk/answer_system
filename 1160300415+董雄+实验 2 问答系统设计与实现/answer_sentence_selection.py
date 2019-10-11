# -*- coding: utf-8 -*-
"""
Created on Tue May 28 10:07:20 2019

@author: dxzmpk
"""

import jieba 
import json
import codecs
#from gensim import corpora
#from gensim.summarization import bm25
import os
import math
import jieba #导入结巴分词
import re



def create_new_index(filename):
    file_index = {}
    dic_list = read_json_data(filename)
    for dic in dic_list:
        pid = dic['pid']
        for sentence in dic['document']:
            for word in sentence:
                if word not in file_index:
                    file_index[word] = {pid: 1}
                else:
                    if pid not in file_index[word]:
                        file_index[word][pid] = 1
                    else:
                        file_index[word][pid] += 1 
    return file_index

def search(entry, topK=3):
    global index_dic
    if index_dic is None:
        try:
            print('Loading index file...')
            index_dic = read_json_data('index.json')[0]
            print('Done.')
        except Exception:
            print('Create index dictionary failed.')
            exit(1)
    keywords = list(jieba.analyse.extract_tags(entry, topK=5))
    ans_dict = {}
    for keyword in keywords:
        if keyword not in index_dic: continue
        for pid in index_dic[keyword].keys():
            if pid not in ans_dict:
                ans_dict[pid] = 1
            else:
                ans_dict[pid] += 1
    answer = sorted(ans_dict.items(), reverse=True, key=lambda x: x[1])
    return [answer[i][0] for i in range(min(len(answer), topK))]

def evaluation(topK=3):
    global TEST_DATA
    if TEST_DATA is None:
        TEST_DATA = read_json_data('train.json')
    find = 0
    for dic in TEST_DATA:
        if str(dic['pid']) in search(dic['question'], topK):
            find += 1
    print('mrr: ', str(topK)+':', find/len(TEST_DATA))  

def read_json_data(filename):
    dic_list = []
    with open(filename, 'r',encoding = 'utf-8') as f:
        for line in f:
            dic_list.append(json.loads(line))
    return dic_list

def save_json_data(dic_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for dic in dic_list:
            f.write(json.dumps(dic, ensure_ascii=False) + '\n')
            f.flush()

def main():
    correct = 0
    train_dicts = read_json_data('data/train.json')
    answer_dicts = read_json_data('data/passages_multi_sentences.json')
    #开始进行评价
    for train_dict in train_dicts:
        corpus = []
        question = train_dict['question']
        pid = train_dict['pid']
        answer_sentence = train_dict['answer_sentence']
        question_seg = jieba.lcut(question)
        answer_dic = answer_dicts[pid]
        answer_list = answer_dic['document']
        for sentence in answer_list:
            words_in_sentence = jieba.lcut(sentence)
            corpus.append(words_in_sentence)
        dictionary = corpora.Dictionary(corpus)
 #           print (len(dictionary))
        bm25Model = bm25.BM25(corpus)
#            average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
        scores = bm25Model.get_scores(question_seg)
 #           print('max index')
        iterate = 0
        while len(scores):
            iterate = iterate+1
            max_index = scores.index(max(scores))
            if answer_list[max_index]==answer_sentence[0]:
                correct=correct+(1/iterate)
                break
            else:
                scores.remove(scores[max_index])
 #           print('预测答案句：'+answer_list[idx])
 #           print('标准答案句：'+answer_sentence[0])
    totalitem = len(train_dicts)
    print('MRR为：') 
    print(correct/totalitem)

def inition(docs):
    D = len(docs)
    avgdl = sum([len(doc)+ 0.0 for doc in docs]) / D
    for doc in docs:
        tmp = {}
        for word in doc:
            tmp[word] = tmp.get(word, 0) + 1  # 存储每个文档中每个词的出现次数
        f.append(tmp)
        for k in tmp.keys():
            tf[k] = tf.get(k, 0) + 1
    for k, v in tf.items():
        idf[k] = math.log(D - v + 0.5) - math.log(v + 0.5)
    return D, avgdl

def sim(query, index):
    score = 0.0
    for word in doc:
        if word not in f[index]:
            continue
        d = len(document[index])
        score += (idf[word] * f[index][word] * (k1 + 1) / (f[index][word] + k1 * (1 - b + b * d / avgdl)))
    return score
SS
    scores = []
    for index in range(D):
            score = sim(query, index)
            scores.append(score)
    return scores




def filter_stop(words):
    return list(filter(lambda x: x not in stop, words))

def get_sentences(doc):
    line_break = re.compile('[\r\n]')
    delimiter = re.compile('[，。？！；]')
    sentences = []
    for line in line_break.split(doc):
        line = line.strip()
        if not line:
            continue
        for sent in delimiter.split(line):
            sent = sent.strip()
            if not sent:
                continue
            sentences.append(sent)
    return sentences

def cal_bm25(query):
    f = [] # 列表的每一个元素是一个dict，dict存储着一个文档中每个词的出现次数
    tf = {} # 储存每个词以及该词出现的文本数量
    idf = {} # 储存每个词的idf值
    k1 = 1.5
    b = 0.75
    stop = set()
    fr = codecs.open('data/stopwords.txt', 'r', 'utf-8')
    for word in fr:
        stop.add(word.strip())
    fr.close()
    re_zh = re.compile('([\u4E00-\u9FA5]+)')
    sents = get_sentences(text)
    doc = []
    for sent in sents:
        words = list(jieba.cut(sent))
        words = filter_stop(words)
        doc.append(words)
    print(doc)
    document = doc

    D, avgdl = inition(doc)
    print(tf)
    print(f)
    print(idf)
    return simall(jieba.lcut(query))

    
if __name__ == '__main__': main()
