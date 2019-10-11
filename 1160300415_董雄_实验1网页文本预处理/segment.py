# -*- coding: utf-8 -*-
"""
Created on Thu May  2 16:13:07 2019

@author: dxzmpk
"""
import os
import json
from pyltp import Segmentor


def getDictionary(filename):
    dics = []
    temp1 = {}
    with open(filename, 'r',encoding='utf-8') as f:
        distros_dict = json.load(f)    
    return distros_dict

def stopwordslistbuilder(filename):
    stopwords = [line.strip() for line in open(filename,'r').readlines()]
    return stopwords
    
def jsonFormat():
    print('文件格式化开始')
    original_file= open('test.json','r',encoding='utf-8')# r when we only wanna read file
    revised_file = open('testSeg.json','w',encoding='utf-8')# w when u wanna write sth on the file
    for aline in original_file:
        revised_file.write(aline + ',' )#for writing your new data
    original_file.close()
    revised_file.close()   


if __name__ == '__main__':
    dics = getDictionary('testSeg.json')
    stopwords = stopwordslistbuilder('hit_stop.txt')
    newDics = []
    temp = {}
    segmentor = Segmentor()  # 初始化实例
    segmentor.load('cws.model')  # 加载模型
    with open('seg.json', 'w',encoding = 'utf-8') as f:
        for dic in dics:
            temp['url'] = str(dic['url'])
            words = segmentor.segment(str(dic['title']))
            seg_sentence = list(words)
            final_seg_title = []
            for word in seg_sentence:
                if word not in stopwords:
                    final_seg_title.append(word)
            temp['title'] =  final_seg_title
            words = segmentor.segment(str(dic['paragraph']))
            seg_sentence = list(words)
            final_seg_sentence = []
            for word in seg_sentence:
                if word not in stopwords:
                    final_seg_sentence.append(word)
            temp['sentence'] =  final_seg_sentence
            temp['file_name'] = dic['file_name']
            f.write(json.dumps(temp, ensure_ascii=False) +'\n')
            f.flush()
    segmentor.release()  # 释放模型


    