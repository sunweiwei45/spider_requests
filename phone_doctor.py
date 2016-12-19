# coding:UTF-8

import requests
from lxml import html
from use_mysql import UseMySQL
import re


class PhoneDocSpider():

    """
    爬取所有电话咨询医生的姓名和其电话咨询页，存入mysql数据库expert中
    不成熟的程序
    """
    def __init__(self, start_url=None):
        """
        实例化一个爬虫的对象，设置
        :param start_url: (string),初始网址
        """
        self.start_url = start_url
        s = requests.Session()
        s.keep_alive = False
        s.adapters.DEFAULT_RETRIES = 5
        self.s = s

    def get_all_page(self):
        start_page = self.s.get(url=self.start_url)
        start_tree = html.fromstring(start_page.text)
        last_page_url = start_tree.xpath('//div[@class="mt30 tc clearfix record-page"]/a[last()]/@href')
        if last_page_url:  # /dhyslist.htm?page=1755\
            all_page = []
            mode = re.compile(r'\d+')
            last_page = mode.findall(last_page_url[0])[0]
            for each in range(1, int(last_page) + 1):
                page_url = 'http://z.xywy.com/dhyslist.htm?page=' + str(each)
                # print page_url
                all_page.append(page_url)
            return all_page
        else:
            pass

    def get_info(self):
        all_page = self.get_all_page()
        my_sql = UseMySQL()
        for page in all_page:
            print page
            response = self.s.get(url=page)
            tree = html.fromstring(response.text)
            doc_name_list = tree.xpath('//strong[@class="f14 fb z-link gre"]/text()')
            doc_url_list = tree.xpath('//div[@class="z-sub-item new-sub-ite pr oh pt20 pb20 pl15 pr15 clearfix"]/a/@href')
            for each in range(len(doc_name_list)):
                pho_doc_item = {}
                pho_doc_item['pho_doc_name'] = doc_name_list[each]
                pho_doc_item['pho_doc_url'] = doc_url_list[each]
                mode = re.compile(r"\d+")
                pho_doc_item['page'] = mode.findall(page)[0]
                my_sql.insert_mysql(pho_doc_item, table='phone_doctor_2')
                print pho_doc_item['pho_doc_name'] + ' ' + pho_doc_item['pho_doc_url'] + ' ' + pho_doc_item['page']
        my_sql.close_mysql()

if __name__ == "__main__":
    url = 'http://z.xywy.com/dhyslist.htm'
    spider = PhoneDocSpider(url)
    spider.get_info()





















