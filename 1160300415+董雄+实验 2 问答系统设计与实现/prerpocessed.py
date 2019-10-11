#!coding=utf8
from whoosh.qparser import QueryParser  
from whoosh.index import create_in  
from whoosh.index import open_dir  
from whoosh.fields import *  
from whoosh.sorting import FieldFacet  
import json
import jieba
from pyltp import Segmentor
from jieba.analyse import ChineseAnalyzer

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


def jsonFormat():
    print('文件格式化开始')
    original_file= open('data/train.json','r',encoding='utf-8')# r when we only wanna read file
    revised_file = open('data/train_new.json','w',encoding='utf-8')# w when u wanna write sth on the file
    for aline in original_file:
        revised_file.write(aline + ',' )#for writing your new data
    original_file.close()
    revised_file.close()  


if __name__ == '__main__':
    analyzer = ChineseAnalyzer()
    schema = Schema(pid=NUMERIC(stored=True),document=TEXT(stored=True, analyzer=analyzer))
    ix = create_in("/index",schema=schema,indexname='ducument_index')
    writer = ix.writer()
    with open('data/passages_multi_sentences_new.json', 'r',encoding='utf-8') as f:
        distros_dict = json.load(f)
        print('共有',len(distros_dict),'条记录')
    for dic in distros_dict:
        writer.add_document(
            pid=dic['pid'],
            document=dic['document']
        )
    writer.commit()    
    print('索引建立完成')
    print('index built')
    with ix.searcher() as searcher:
        query = QueryParser("document", ix.schema).parse("出生")
        results = searcher.search(query)
        print(results[0]['pid'])
        
    with open('train_new.json','r',encoding='utf-8') as rf:
        train_dicts = json.load(rf)
        print('共有',len(train_dicts),'条记录')
    correct = 0
    total = 0
    for train_dict in train_dicts:
        rate = {}
        with ix.searcher() as searcher:
            total = total + 1
            question_word_list = jieba.lcut(train_dict['question'])
            for question_word in question_word_list:
                word_query = QueryParser("document", ix.schema).parse(question_word)
                results = searcher.search(query)
                for result in results:
                    if result['pid'] == train_dict['pid'] :
                        rate[result['pid']] = rate[result['pid']] + 1
                        
    F1 = correct/total
    print('')
    
    