# coding:UTF-8

import requests
from lxml import html
from use_mysql import UseMySQL


class Match():
    def __init__(self, record=None):
        """
        在寻医问药——电话医生界面搜索，匹配家庭医生(姓名)
        :param record:(dict) 搜素条件
        """
        if record is not None:
            self.record = record
            s = requests.Session()
            s.keep_alive = False
            s.adapters.DEFAULT_RETRIES = 10
            self.s = s
        else:
            print "No record!"
            pass

    def get_family(self):
        """
        查询家庭医生的姓名、职称、医院、科室
        :return:
        """
        record = {}
        fam_doc_url = self.record['fam_doc_url']
        response = self.s.get(url=fam_doc_url)
        tree = html.fromstring(response.text)
        name = tree.xpath('//li[1]/span[@class="fl dib mt20 graydeep"]/text()')
        if name:
            record['name'] = name[0]
        else:
            record['name'] = "0"
        title = tree.xpath('//li[2]/span[@class="fl dib mt20 graydeep"]/text()')
        if title:
            record['title'] = title[0]
        else:
            record['title'] = '0'
        hospital = tree.xpath('//div[@class="dbjb f12 mt10"]/text()[last()]')
        if hospital:
            record['hospital'] = hospital[0]
        else:
            record['hospital'] = '0'
        keshi = tree.xpath('//li[3]/span[@class="fl dib mt20 graydeep"]/text()')
        if keshi:
            record['keshi'] = keshi[0]
        else:
            record['keshi'] = '0'

        return record

    def search_phone(self):
        """
        在电话咨询界面搜索
        :return:
        """
        list = []
        name = self.record['fam_doc_name'].encode("gbk")  ##gbk：1-2，utf-8：1-3  看网页
        #依据网页配置查询条件
        data = {
            'speciality1': '',
            'speciality2': '',
            'search_keyword': name,
            'province': '',
            'city': '',
            'price': '',
            'time': '',
            'search': 1
        }
        response = self.s.get(url="http://z.xywy.com/dhyslist.htm", params=data)  ##传递参数
        tree = html.fromstring(response.text)
        temp_hos = tree.xpath('//span[@class="ml20 f14 graydeep"][1]/text()')
        temp_keshi = tree.xpath('//span[@class="ml20 f14 graydeep"][2]/text()')
        temp_title = tree.xpath('//span[@class="ml10 gray"]/text()')
        if temp_hos:
            for i in range(len(temp_hos)):
                record = {}
                record['name'] = self.record['fam_doc_name']
                record['title'] = temp_title[i].encode('utf-8').split()[0]
                record['hospital'] = temp_hos[i]
                record['keshi'] = temp_keshi[i]
                list.append(record)
            return list
        else:
            return list

    def match(self):
        fam_doc = self.get_family()
        search_pho_list = self.search_phone()
        if search_pho_list:
            for each in search_pho_list:
                fam_name = fam_doc['name']
                phone_name = each['name']
                fam_title = fam_doc['title']
                phone_title = each['title']
                fam_hospital = fam_doc['hospital']
                phone_hospital = each['hospital']
                fam_keshi = fam_doc['keshi']
                phone_keshi = each['keshi']

                if fam_name == phone_name and fam_title == phone_title and fam_hospital == phone_hospital and fam_keshi == phone_keshi:
                    return '1'
                else:
                    return '0'
        else:
            return '0'

if __name__ == "__main__":
    my_sql = UseMySQL()
    query_result = my_sql.select_mysql(table="family_doctor")
    record = {}
    for dic in query_result:
        my_match = Match(record=dic)
        record['doc_name'] = dic['fam_doc_name']
        record['isphone'] = my_match.match()
        my_sql.insert_mysql(record=record, table='matching_copy')
        print repr(record['doc_name']) + ' ' + repr(record['isphone'])
    my_sql.close_mysql()
