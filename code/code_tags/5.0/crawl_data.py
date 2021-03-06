import requests
import pandas as pd
import numpy as np
from lxml import etree
import os
import setting
import time


class Spiders():

    def __init__(self):
        # 使用默认地址为富投网行情全表
        self.url = r"http://www.richvest.com/index.php?m=cb&a=cb_all"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

    
    def set_url(self,url):
        """ 设置自己为指定的url """
        self.url = url
    
    def get_html(self):
        ''' 模拟请求数据 '''
        try:
            res = requests.get(self.url,headers=self.headers)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            return res.text
        except :
            return "GET HTML A (出现错误)"

    def parse_html(self):
        '''  使用lxml解析HTML '''
        demo = self.get_html()
        try:
            if  "GET HTML(出现错误)" != demo:
                html =  etree.HTML(demo)
                table = html.xpath('//table[@id="cb_hq"]')
                demo_ = etree.tostring(table[0], encoding='utf-8').decode() 
                data_pool = pd.read_html(demo_, encoding='utf-8', header=0)[0]
                return  data_pool
            else :
                return  "GET HTML B (失败)"
        except :
            return "PARSE HTMl (出现错误)"

    
    
    def storage_data(self,data,path = setting.DATA_PATH):
        """
        数据预览及存储
        - 默认存储
        """
        name = str(pd.datetime.now())[:10]
        try:
            data.to_csv(path+name+".csv",index = False)
            return  True
        except :
            return False

    def crawl_storage(self):
        path = setting.DATA_PATH
        file_name = os.listdir(path)[-1][:-4]
        print(os.listdir(path))

        file_stamp = pd.to_datetime(file_name)
        stamp = pd.datetime.now()
        print(file_stamp.month,file_stamp.day,stamp.month,stamp.day)
        if file_stamp.month == stamp.month and file_stamp.day == stamp.day:
            pass
        else:
            data = self.parse_html()
            self.storage_data(data)
    
    def get_gsz(self):
        """ 基金估算值 """
        # 设置对应连链接
        url = "http://fundgz.1234567.com.cn/js/161716.js?rt=" + str(int(round(time.time() * 1000)))
        self.set_url(url)
        result = self.get_html()
        gsz = float(eval(result[8:-2])["gsz"])
        return gsz
    
    def get_zhaoshang(self):
        """ 获取招商现价 """
        self.set_url("http://www.richvest.com/index.php?m=stock_pub&c=arbitrage&a=listBondFund")
        fund_data = self.parse_html()
        zhaoshang = fund_data["现价"][fund_data["代码"]=="sz161716"].values[0]
        return zhaoshang

    def get_zs_data(self):
        zhaoshang = self.get_zhaoshang()
        gsz = self.get_gsz()
        fund_data_ = ["招商双债","sz161716",zhaoshang,gsz,round((float(zhaoshang)- float(gsz))/float(gsz) * 100,3)]
        # print(fund_data_)
        return  fund_data_

# 初始化类
# spider = Spiders()
# spider.crawl_storage()


""" 数据爬取类实例化  """
# spider = Spiders()
# spider.set_url("http://www.richvest.com/index.php?m=stock_pub&c=arbitrage&a=listBondFund")
# fund_data = spider.parse_html()
# zhaoshang = fund_data["现价"][fund_data["代码"]=="sz161716"].values[0]
# gsz = spider.get_gsz()

# print(zhaoshang,gsz,(zhaoshang-gsz)/gsz*100)

# fund_data_ = pd.DataFrame([["招商双债"],["sz161716"],[zhaoshang],[gsz],[round((zhaoshang-gsz)/gsz*100,3)]],columns=["名称","代码","现价","净估值","溢价率(%)",])
# print(fund_data_)