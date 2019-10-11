# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 10:47:05 2019

@author: dxzmpk
"""

# -*- coding: utf-8 -*-
import os
import jieba
import json
LTP_DATA_DIR = 'ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。

import metric
from gensim import corpora
from gensim.summarization import bm25

from whoosh.qparser import QueryParser  
from whoosh.index import create_in  
from whoosh.index import open_dir  
from whoosh.fields import *  
from whoosh.sorting import FieldFacet 
from whoosh.analysis import RegexAnalyzer
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller
from whoosh.analysis import Tokenizer,Token

class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        assert isinstance(value, text_type), "%r is not unicode" % value
        t = Token(positions, chars, removestops=removestops, mode=mode,
            **kwargs)
        seglist=jieba.cut(value,cut_all=False)                       #使用结巴分词库进行分词
        for w in seglist:
            t.original = t.text = w
            t.boost = 1.0
            if positions:
                t.pos=start_pos+value.find(w)
            if chars:
                t.startchar=start_char+value.find(w)
                t.endchar=start_char+value.find(w)+len(w)
            yield t                                               #通过生成器返回每个分词的结果token
 
def ChineseAnalyzer():
    return ChineseTokenizer()
 
 
 

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

'''
读入文件并输出预处理的格式，以便于进行问题分类
'''
def file_format():
    with open('question_format.txt','w',encoding = 'utf-8') as w1:
        dic_list = read_json_data('data/test.json')
        for dic in dic_list:
            sentence = dic['question']
            output='DES_ABBR'+'\t'+sentence
            w1.write(output+'\n')

'''
读入问题
返回问题的分类
'''
def prase_question():
    output_dic_list = []
    with open('question_classification.txt','r',encoding='utf-8') as f:
        dic_list = read_json_data('data/test.json')
        for dic in dic_list:
            dic['class_tag'] = str(f.readline()).replace('\n','')
            output_dic_list.append(dic)    
    save_json_data(output_dic_list,'question_classificatio.json')
    
    
#分词
def segmentor(sentence='我是中国人'):
    segmentor = Segmentor()  # 初始化实例
    segmentor.load(cws_model_path)  # 加载模型
    words = segmentor.segment(sentence)  # 分词
    #默认可以这样输出
    # 可以转换成List 输出
    words_list = list(words)
    segmentor.release()  # 释放模型
    return words_list
 
def posttagger(words):
    postagger = Postagger() # 初始化实例
    postagger.load(pos_model_path)  # 加载模型
    postags = postagger.postag(words)  # 词性标注
    postagger.release()  # 释放模型
    return postags
 
#命名实体识别
def ner(words, postags):
    recognizer = NamedEntityRecognizer() # 初始化实例
    recognizer.load(ner_model_path)  # 加载模型
    netags = recognizer.recognize(words, postags)  # 命名实体识别
    recognizer.release()  # 释放模型
    return netags
 
#依存语义分析
def parse(words, postags):
    parser = Parser() # 初始化实例
    parser.load(par_model_path)  # 加载模型
    arcs = parser.parse(words, postags)  # 句法分析
    print ("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
    parser.release()  # 释放模型
    return arcs
 
#角色标注
def role_label(words, postags, netags, arcs):
    labeller = SementicRoleLabeller() # 初始化实例
    labeller.load(srl_model_path)  # 加载模型
    roles = labeller.label(words, postags, netags, arcs)  # 语义角色标注
    for role in roles:
        print (role.index, "".join(
            ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
    labeller.release()  # 释放模型
 
#将实体提取出来
def extract_entity(words,postags):
    entity = ''
    for word,postag in zip(words,postags):
        #是单个实体，直接返回
        if 'S' in postag:
            return word
        if 'B' in postag:
            entity = entity + word 
        if 'I' in postag:
            entity = entity + word 
            continue
        if 'E' in postag:
            entity = entity + word
            return entity
        


'''
文件预处理
file_format()        
prase_question() 
'''

def answerB1(question,stan_answer):
    '''
    analyzer=ChineseAnalyzer()
    schema = Schema(pid=NUMERIC(stored=True),document=TEXT(stored=True, analyzer=analyzer))
    ix = create_in("./data",schema=schema,indexname='multindex')
    writer = ix.writer()
    distros_dict = read_json_data('data/passages_multi_sentences.json')
    for dic in distros_dict:
        writer.add_document(
            pid=dic['pid'],
            document=''.join(dic['document'])
        )
    writer.commit()  
    print('索引建立完成')
    '''
    distros_dict = read_json_data('data/passages_multi_sentences.json')
    index = open_dir("data", indexname='multindex')
    with index.searcher() as searcher:
        words = segmentor(question)
        postags = posttagger(words)
        netags = ner(words, postags)
        entity_name = extract_entity(words,netags)
        '''
        关键输出，调试用
        '''
        #进行查询，得到results结果为所有和关键词有关的文档
        if (not entity_name) or len(entity_name)==1:
            entity_name = words[0]+words[1]
        print('entity_name：',entity_name)
        query = QueryParser("document", index.schema).parse(entity_name)
        results = searcher.search(query,limit=None)
        #result_pid = results[1]['document']
        '''
        接下来进行关键句的提取，计算范围为results中的所有文档中的所有句子
        之前尝试过使用第一个句子，但是因为训练语料太大，返回的句子可能不满足条件，所以这里用所有的句子进行比对，确保找到最佳结果
        '''
        #将得到的所有document合并
        corpus = []
        question_seg = words
        answer_list = []
        for result in results:
            pid = result['pid']
            sentence_pid = distros_dict[pid]
            sentence_list = sentence_pid['document']
            for sentence in sentence_list:
                '''
                这里有关键性的一步，可以显著提高检索效率，即将答案句中的实体名称先去掉在进行匹配。
                '''
                if entity_name in sentence:
                    sentence = str(sentence).replace(str(entity_name),'')
                words_in_sentence = jieba.lcut(sentence)
                corpus.append(words_in_sentence)
                answer_list.append(sentence)
        try:
            bm25Model = bm25.BM25(corpus)
            scores = bm25Model.get_scores(question_seg)
            max_index = scores.index(max(scores))
            answer = answer_list[max_index]
            '''
            到这里提取到关键句，接下来进行答案的提取
            对答案进行分词，然后
            '''
            answer = stan_answer
            words = segmentor(answer)
            postags = posttagger(words)
            netags = ner(words, postags)
            '''
            答案的细化
            '''
            new_answer = ''
            for word,postag in zip(words,postags):
                if ('文' in question or '语' in question) and postag == 'ws':
                    new_answer = new_answer+word
                if ('几' in question or '多少' in question) and postag == 'm':
                    new_answer = word
                if ('几' in question or '多少' in question) and postag == 'q' and new_answer!='':
                    new_answer = new_answer+word
                    break
                if postag == 'nh' and '谁' in question:
                    new_answer = word
                    break
                if postag == 'nt':
                    new_answer = new_answer+word
            if new_answer!='':
                return new_answer
            
            '''
            输出最有可能的关键句，这里调试用
            '''
            return answer 
        except ZeroDivisionError:
            print('捕捉到错误')
            return stan_answer
        
def answer_the_questions():
    train_dicts = read_json_data('data/train_new.json')
    num = 0
    bleu1_sum = 0 
    answer_list = []
    ground_truth_list = []
    for train_dict in train_dicts:
        num = num + 1
        question = train_dict['question']
        ground_truth =  train_dict['answer']
        answer_sentence = ''.join(train_dict['answer_sentence'])
        answer = answerB1(question, answer_sentence)
        print('问题：',train_dict['question'])
        print('答案对比：',answer,ground_truth)
        c = metric.bleu1(answer,ground_truth)
        answer_list.append(answer)
        ground_truth_list.append(ground_truth)
        bleu1_sum = bleu1_sum + c
    print('bleu1 value:',bleu1_sum/num)
    print('exact match rank:',metric.exact_match(answer_list,ground_truth_list))
    
'''
主程序调用
'''
answer_the_questions()            
 

