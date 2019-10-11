#!/usr/bin/python
# coding:utf-8

"""
@author: Mingxiang Tuo
@contact: tuomx@qq.com
@file: demo.py
@time: 2019/4/28 11:01
实验一的整个程序逻辑框架的简单示例（也可以按自己的逻辑写），同学们只需要指定urls集合以及完成爬虫工具提取网页内容及附件的逻辑即可
"""
import json
import requests, threading
import re
from bs4 import BeautifulSoup

def craw(url):
    pattern = re.compile('>(.*?)<') 
    print('Start Crawing '+ url)
    result = {}
    html = requests.get(url)
    html.encoding = 'utf-8'
    html_txt = html.text
    soup = BeautifulSoup(html_txt,'html.parser')
	#解析标题和url
    for each_text in soup.find('title'):
        title = each_text
        result['url'] =  url
        result['title'] = title
	#解析正文
    if not soup.find(attrs = {'class':'block-region-left'}):
        return 
    texts = soup.find(attrs={'class':'block-region-left'})
    contents = texts.sekect('p')
    content = ''
    for para in contents:
        content += str(para)
    result['paragraph'] = ''.join(pattern.findall(content))
    #解析文件# Search
    for link in texts.find_all('img'):
        image = link.get('src')
        name = str(image).split('/')[-1]
        result['img'] = name
    return result;

def save_file(url, filename):
    r = requests.get(url)
    open(filename, 'wb').write(r.content)

#多线程
def usingthread(urls):
    for i in range(1, len(urls)): 
        #创建线程
        thread = threading.Thread(target = craw, args=(urls[i], False)) 
        thread.start()




def getUrl(url):
    hrefs = []
    html_txt = requests.get(url).text
    soup = BeautifulSoup(html_txt,'html.parser')
    for i in soup.find_all('a',href = re.compile(r"/article/2019/.*")):
        if 'http' in i.get('href'):
            tmp = i.get('href')
        else:
            tmp = "http://today.hit.edu.cn" + i.get('href')
        hrefs.append(tmp)
    print('crawing',len(hrefs),'urls')
    return hrefs
    


if __name__ == '__main__':
    url1 = 'http://today.hit.edu.cn/article/2019/04/29/66551'
    urls = getUrl(url1)
    # url集合示例
    results = []
    if (len(urls) > 100):
        usingthread(urls)
    else:
        for url in urls:
            craw(url)
    for url in urls:
        result = craw(url)
        if not result:
            continue
        # 这个是用爬虫爬取并处理后得到的一个字典对象
        results.append(result)

    # 保存成json文件的示例
    with open('data.json', 'w', encoding='utf-8') as fout:
        for sample in results:
            # 注意一定要加上换行符
            fout.write(json.dumps(sample, ensure_ascii=False)+'\n')

    # 从json文件中读取数据的示例
    read_results = []
    with open('data.json', encoding='utf-8') as fin:
        read_results = [json.loads(line.strip()) for line in fin.readlines()]
