# coding:UTF-8

import requests
from lxml import html
from use_mysql import UseMySQL
import re


class ExpertSpider():
    def __init__(self, start_url=None):
        self.start_url = start_url
        s = requests.Session()
        s.keep_alive = False
        s.adapters.DEFAULT_RETRIES = 10
        self.s = s

    def parse(self):
        start_page = self.s.get(self.start_url)
        tree = html.fromstring(start_page.text)
        keshi_url_list = tree.xpath('//ul[@class="as-jib-main-list zh-item-list public-list pl15 pt10 pb10 clearfix"]/li/a/@href')
        for url in keshi_url_list:
            url_list = str(url).split('-')
            url = url_list[0] + "zhuanjia-" + url_list[1]
            self.get_page(url)
            # print url

    def get_page(self, url=None):
        response = self.s.get(url)
        tree = html.fromstring(response.text)
        temp_url = tree.xpath('//div[@class="page mt25 fYaHei tc"]/a[last()]/@href')
        if temp_url:
            last_url = temp_url[0]
            last_url_list = str(last_url).split("=")  # 将最后一页如：‘/zhuanyezhuanjia-erke.htm?page=731’以“=”分开
            mode = re.compile(r'\d+')
            last_page = mode.findall(last_url)[0]
            for page in range(1, int(last_page) + 1):
                page_url = "http://z.xywy.com" + last_url_list[0] + "=" + str(page)
                self.get_info(page_url)
        else:
            page_url = response.url
            self.get_info(page_url)

    def get_info(self, url=None):
        expert_item = {}
        response = self.s.get(url)
        tree = html.fromstring(response.text)
        doc_url_list = tree.xpath('//a[@class="f14 fb"]/@href')
        my_sql = UseMySQL()
        for each in doc_url_list:
            doc_response = self.s.get(each)
            doc_tree = html.fromstring(doc_response.text)

            expert_item['expert_name'] = doc_tree.xpath('//strong/a/text()')[0]

            expert_item['expert_url'] = each

            expert_person_url = doc_tree.xpath('//div[@class="mt20 cca clearfix"]/span/a/text()')
            if expert_person_url:
                expert_item['expert_person_url'] = expert_person_url[0]
            else:
                expert_item['expert_person_url'] = '0'

            expert_item['expert_keshi_url'] = url

            pho_doc_url = doc_tree.xpath('//a[@class="call-btn mb30 btn-blue-anim personal-btn"]/@href')
            if pho_doc_url:
                expert_item['pho_doc_url'] = pho_doc_url[0]
            else:
                expert_item['pho_doc_url'] = '0'

            ask_que_url = doc_tree.xpath('//a[@class="call-btn btn-blue-anim personal-btn"]/@href')
            if ask_que_url:
                temp_url = requests.get(ask_que_url[0]).url
                expert_item['ask_que_url'] = str(temp_url)
            else:
                expert_item['ask_que_url'] = '0'

            my_sql.insert_mysql(record=expert_item, table='expert')
            print expert_item['expert_name'] + ' ' + expert_item['expert_url'] + ' ' + expert_item['expert_person_url'] + ' ' + expert_item['expert_keshi_url'] + ' ' + expert_item['pho_doc_url'] + ' ' + expert_item['ask_que_url']
        my_sql.close_mysql()


if __name__ == "__main__":
    url = 'http://z.xywy.com/zhuanye.htm?fromurl=xywyhomepage'
    spider = ExpertSpider(url)
    spider.parse()


