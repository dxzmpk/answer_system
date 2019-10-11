# -*- coding: utf-8 -*-
"""
Created on Mon May 20 16:20:53 2019

@author: dxzmpk
"""
from pyltp import Segmentor
import re
import jieba
import json

word_dic = {}
wordlist = []
with open('dictionary.txt', 'r',encoding='utf-8') as f:
    word = f.readline()
    i = 0
    while word:
        wordlist.append(word)
        word = f.readline()
        word_str = str(word)
        word_dic[word_str.strip()] = i
        i=i+1
print(len(wordlist))
print(word_dic)

n = 0
label_dic = {}
with open('libsvm-3.23/windows/features.txt','w',encoding='utf-8') as wf:
    with open('libsvm-3.23/windows/trian_questions.txt', 'r',encoding='utf-8') as f:
        line = f.readline()
        while line:
            document = re.split('\t',line)
            cutword_result = jieba.lcut(document[1])
            label = document[0]
            feature_str = {}
            for word in cutword_result:
                if word!='\n':
                    if word_dic.get(word.strip()):
                        feature_str[word_dic[word.strip()]] = word.strip()
            L = sorted(feature_str.items(),key=lambda item:item[0])
            feature = ''
            for l in L:
                feature +=  str(l[0]) + ":" + str(1)+" "
            label_value = 0
           
            '''
            if label == "DES_OTHER":
                wf.write("+1" + " " +feature+"\n")    
            else:
                wf.write("-1" + " " +feature+"\n")  
             '''
            if label_dic.get(label):
                label_value = label_dic[label]
                wf.write(str(label_value) + " " +feature+"\n")    
            else:
                n = n+1
                label_value = n
                label_dic[label] = n
                wf.write(str(label_value) + " " +feature+"\n")    
            line = f.readline()


with open('question_format_features.txt','w',encoding='utf-8') as wf:
    with open('question_format.txt', 'r',encoding='utf-8') as f:
        line = f.readline()
        while line:
            document = re.split('\t',line)
            cutword_result = jieba.lcut(document[1])
            label = document[0]
            feature_str = {}
            for word in cutword_result:
                if word!='\n':
                    if word_dic.get(word.strip()):
                        feature_str[word_dic[word.strip()]] = word.strip()
            L = sorted(feature_str.items(),key=lambda item:item[0])
            feature = ''
            for l in L:
                feature +=  str(l[0]) + ":" + str(1)+" "
            
            if label_dic.get(label):
                label_value = label_dic[label]
            wf.write(str(label_value) + " " +feature+"\n")   
            '''
            if label == "DES_OTHER":
                wf.write("+1" + " " +feature+"\n")    
            else:
                wf.write("-1" + " " +feature+"\n")  
            '''
            line = f.readline()
print(label_dic)