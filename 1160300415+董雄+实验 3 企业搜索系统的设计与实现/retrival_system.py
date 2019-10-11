from tkinter import *
import jieba
import json
import string
import MySQLdb as mdb
from gensim import corpora
from gensim.summarization import bm25

index_dict = None
seg_dict = None
pic_name = 'data/pic/mode.png'

def pre_process():
    file_dicts = parse_json_data('data/file_data.json')
    out_dicts = []
    ite = 0
    for file_dict in file_dicts:
        if ite<250:
            file_dict['rate'] = 1
        if ite<500 and ite >= 250:
            file_dict['rate'] = 2
        if ite>=500 and ite<750:
            file_dict['rate'] = 3
        if ite>=750 and ite<1115:
            file_dict['rate'] = 4
        ite += 1
        out_dicts.append(file_dict)
    save_json_data(out_dicts,'data/file_data_identity.json')


def parse_json_data(filename):
    dicts = []
    with open(filename,'r',encoding = 'utf-8') as f:
        for line in f:
            dicts.append(json.loads(line))
    return dicts

def save_json_data(dics,filename):
    with open(filename,'w',encoding = 'utf-8') as f:
        for dic in dics:
            f.write(json.dumps(dic,ensure_ascii = False) + '\n')
            f.flush()

'''
建立索引
使用字典套字典的方式建立
'''
def create_file_index(filename):
    file_index = {}
    dics = parse_json_data(filename)
    pid = 0
    for dic in dics:
        title = dic['title']
        content = dic['sentence']
        content = content + title
        for word in content:
            if word not in file_index:
                file_index[word] = {pid:1}
            else:
                if pid not in file_index[word]:
                    file_index[word][pid] = 1
                else:
                    file_index[word][pid] += 1
        pid = pid + 1
    return file_index

def search_by_words(entry,rate):
    global index_dict
    if index_dict is None:
        print("加载索引文件中...")
        index_dict = parse_json_data('index/index.json')[0]
    keywords = jieba.lcut(entry)
    one_stop_words = ['机密','资金','涉密']
    if rate == 1:
        keywords = [key for key in keywords if key not in one_stop_words]
    ans_dict = {}
    print(keywords)
    for keyword in keywords:
        if keyword not in index_dict: continue
        for pid in index_dict[keyword].keys():
            if pid not in ans_dict:
                ans_dict[pid] = index_dict[keyword][pid]
            else:
                ans_dict[pid] += index_dict[keyword][pid]
    answer = sorted(ans_dict.items(),reverse=True, key=lambda x : x[1])
    # print("打印answer测试：",answer)
    return [answer[i][0] for i in range(min(len(answer),3))]

def gui(rate):
    global seg_dict
    global pic_name
    root = Tk()
    root.title("今日哈工大信息检索系统")
    root.minsize(500,400)
    # Thinker总共提供了三种布局组件的方法：pack(),grid()和place()
    # grid()方法允许你用表格的形式来管理组件的位置
    # row选项代表行，column选项代表列  
    # 例如row=1，column=2表示第二行第三列(0表示第一行)
    Label(root, text="请输入查询的内容:").grid(row=0)
    Label(root, text="文本查询结果:").grid(row=5)
    Label(root, text="附件查询结果:").grid(row=8)
    Label(root, text="当前用户等级: " + str(rate)).grid(row=9)
    e1 = Entry(root,borderwidth = 3,width = 48)
    e2 = Text(root)
    e3 = Text(root)
    e1.grid(row=0, column=1, padx=10, pady=5)
    e2.grid(row=5, column=1, padx=10, pady=5)
    e3.grid(row=8, column=1, padx=10, pady=3)
    e3['height'] = 8
    def search():
        global seg_dict
        global pic_name
        e2.delete('1.0','end')
        e3.delete('1.0','end')
        search_line = e1.get()
        results = get_message(search_line,rate)
        if seg_dict is None:
            print('装载分词字典中...')
            seg_dict = parse_json_data('data/file_data_identity.json')
        num = 1
        photo_files = []
        for result in results:
            result_int = int(result)
            photo_files += seg_dict[result_int]['file_name']
            if rate >= seg_dict[result_int]['rate']:
                e2.insert("insert",'%d' %(num)+'.' + 'title:' + seg_dict[result_int]['title'] +'\n' +'paragraph:' + seg_dict[result_int]['paragraph']+'\n'+'\n')
                num = num+1
        print(photo_files)
        '''
        if len(photo_files) != 0:
            new_img = photo = PhotoImage(format="png",file='data/pic/'+photo_files[0])
            imgLabel = Label(root, image=new_img)
            imgLabel.grid(row=10, column=1, padx=10, pady=3)
        '''
        for photo_file in photo_files:
            e3.insert("insert",photo_file+"\n")
        results = []
        e1.delete(0, END)

    #定义按钮
    Button(root, text="获取信息", width=10, command=search).grid(row=0, column=5, sticky=W, padx=10, pady=5)
    mainloop()

def build_index():
    dic = create_file_index('data/seg.json')
    save_json_data([dic], 'index/index.json')

def sign_up(user,password,user_rate):
    # 连接数据库
    conn = mdb.connect('localhost', 'root', 'root')

    # 也可以使用关键字参数
    conn = mdb.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='ir_passwords', charset='utf8')

    # 也可以使用字典进行连接参数的管理
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'passwd': 'root',
        'db': 'ir_passwords',
        'charset': 'utf8'
    }
    conn = mdb.connect(**config)
    try:
        sql = 'INSERT INTO passwords values("%s","%s","%s")' %(user,password,user_rate)
        cursor.execute(sql)
    except:
        import traceback
        traceback.print_exc()
        # 发生错误时会滚
        conn.rollback()
    finally:
        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        conn.close()

def fuzzy_search(search_line,rate):
	doc_dicts = parse_json_data('data/seg.json')
	corpus = []
	answers = []
	for doc_dict in doc_dicts:
		words = doc_dict['document']
		corpus.append(words)
	try:
		bm25Model = bm25.BM25(corpus)
        scores = bm25Model.get_scores(question_seg)
        max_index = scores.index(max(scores))
        answer = doc_dicts[max_index]['document']
        answers.append(answer)
        return answers
    except ZeroDivisionError:
	    print('捕捉到错误')
def get_message(search_line,rate):
    global seg_dict
    results = search_by_words(search_line,rate)
    if len(results) == 0:
    	results = fuzzy_search(search_line,rate)
    print(results)
    return results
    if seg_dict is None:
        print('装载分词字典中...')
        seg_dict = parse_json_data('data/file_data.json')
    answer_sentence = []
    num = 1
    for result in results:
        result_int = int(result)
        answer_sentence.append('%d' %(num)+'.' + 'title:' + seg_dict[result_int]['title'] +'\n' +'paragraph:' + seg_dict[result_int]['paragraph'])
        num = num+1
    return answer_sentence
def login():
    rate = 0
    root = Tk()
    root.title("在工大检索系统登录")
    root.minsize(100,150)
    Label(root, text="请输入用户名:").grid(row=0)
    Label(root, text="请输入密码:").grid(row=1)
    e1 = Entry(root,borderwidth = 3,width = 15)
    e1.grid(row=0, column=1, padx=10, pady=5)
    e2 = Entry(root,borderwidth = 3,width = 15,show = '*')
    e2.grid(row=1, column=1, padx=10, pady=5)
    conn = mdb.connect('localhost', 'root', 'root')
    # 也可以使用关键字参数
    conn = mdb.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='ir_passwords', charset='utf8')

    # 也可以使用字典进行连接参数的管理
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'passwd': 'root',
        'db': 'ir_passwords',
        'charset': 'utf8'
    }
    conn = mdb.connect(**config)
    try:
        sql = 'SELECT FROM passwords WHERE user = '+ str(e1.get())
        cursor.execute(sql)
    except:
        import traceback
        traceback.print_exc()
        # 发生错误时会滚
        conn.rollback()
    finally:
        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        conn.close()
    def get_user_rate():
        user_name = e1.get()
        user_rate = {'grandad':4,'dad' :3,'son':2,'grandson':1}
        rate = user_rate[user_name]
        root.destroy()        
        gui(rate)

    Button(root, text="登录", width=10, command=get_user_rate).grid(row=3, column=0, sticky=W, padx=10, pady=5)
    Button(root, text="注册", width=10, command=sign_up).grid(row=3, column=1, sticky=W, padx=10, pady=5)
    mainloop()



#pre_process()
# build_index()
login()

