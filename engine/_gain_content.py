import pickle
from bs4 import BeautifulSoup
import os
import time
import sys
import logging as log
from .engine import SpiderEngine

class GainContent(SpiderEngine):
    def __init__(self, config):
        self.config = config
        # all in args
        self.pklfile = config['pklfile']
        self.trytimes = config['trytimes']

        super(GainContent, self).__init__(config)


    def start_spider(self):

        ip_gene = self.get_ip()
        flag = 0
        results=[]
        with open(self.pklfile, 'rb') as f:
            results = pickle.load(f)
            idx = 0
            while idx < len(results):
                result = results[idx]
                company = result['company']
                if result['page_size'] == 0:
                    try:
                        ip = next(ip_gene)
                        # print(ip)
                        log.info(f"{idx+1}-{flag+1}: 提取IP成功")
                    except:
                        log.error(f"{idx+1}-{flag+1}: 提取IP失败")                        
                        ip_gene = self.get_ip()
                        continue
                    try:
                        html = self.get_html(ip)
                    except:
                        log.error(f"{idx+1}-{flag+1}: 网络连接超时")
                        continue

                    html.encoding = 'utf-8'
                    soup = BeautifulSoup(html.text, 'lxml')
                    # print(soup)
                    try:
                        main_tb = soup.find("div", class_="next")
                        posion = main_tb.find('input')['onkeypress']
                        start = posion.find('zl_tz')+6
                        page_size = int(posion[start:-1])
                        result['page_size'] = page_size
                    except:
                        if soup.find("h1", class_="head_title") == None:
                            log.error(f"{idx+1}-{flag+1}: 没有您要查询的结果")
                            flag+=1
                            if flag >= self.trytimes:
                                spider_all+=1
                                log.info(f'{idx+1}-{flag}: {company} failed\n')
                                idx += 1
                                flag = 0
                            continue
                        else:
                            log.error(f"{idx+1}-{flag+1}: 被认为是机器人")  
                            continue
                    log.info(f'{idx+1}-{flag+1}: {company} success\n')
                    idx += 1
                    flag = 0
                    self.spider_success+=1
                    spider_all+=1
                    with open(self.pklfile, 'wb') as f:
                        pickle.dump(results, f)
                        log.info("保存到文件\n")
                else:
                    log.info(f'{idx+1}-{flag+1}: {company} has successed\n')
                    idx += 1
                    flag = 0

