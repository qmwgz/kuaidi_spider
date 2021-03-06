import requests
from time import sleep

URL_POST = 'https://www.kuaidi100.com/autonumber/autoComNum?resultv2=1&text='
URL_GET_1 = 'https://www.kuaidi100.com/query?type='
URL_GET_2 = '&postid='

Headers_POST = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "0",
    "Host": "www.kuaidi100.com",
    "Origin": "https://www.kuaidi100.com",
    "Referer": "https://www.kuaidi100.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
Headers_GET = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Host": "www.kuaidi100.com",
    "Referer": "https://www.kuaidi100.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def get_kuaidi(Result_FileName, SleepTime):
    # 打开PostID.txt，获取物流单号
    with open('PostID.txt', 'r') as g:
        postid_list = g.readlines()
        g.close()
    # 打开Result_FileName.txt（如果没有则新建，如果有则清空原有数据重新写入）
    with open('%s.txt' % Result_FileName, 'w', encoding='utf-8') as f:
        # 写入标题，可用于Excel导入数据
        f.write('postid,com,message,time,ftime,context' + '\n')
        postid_num = 0
        for x in postid_list:
            postid = x.strip('\n')
            postid_num += 1
            print('正在获取第 %s 个物流信息: %s' % (postid_num, postid))
            # 获取快递100的推荐的快递公司Code，用于下面的物流信息获取
            r_comCode = requests.post(URL_POST + postid, headers=Headers_POST)
            autodata = r_comCode.json()['auto']
            comCode = [i['comCode'] for i in autodata]
            # 开始爬取物流信息
            r_data = requests.get(URL_GET_1 + comCode[0] + URL_GET_2 + postid, headers=Headers_GET)
            wuliu_json = r_data.json()['data']
            Num = 1
            # 首先尝试使用首个推荐的Code获取，如果结果为空则使用while循环获取后面推荐的Code，直至尝试完所有的推荐后用break退出循环
            while wuliu_json == []:
                if Num == len(comCode): break
                r_data = requests.get(URL_GET_1 + comCode[Num] + URL_GET_2 + postid)
                wuliu_json = r_data.json()['data']
                Num += 1
            if wuliu_json == []:
                # 如果查询失败，则写入空值，并保留错误提示（message）
                f.write('%s,%s,%s,%s,%s,%s' % (postid, r_data.json()['com'], r_data.json()['message'], '', '', '' + '\n'))
            else:
                for wuliu in wuliu_json:
                    # 写入爬取的物流流转信息，使用replace把英文的“,”转换为中文的“，”，避免导入Excel时引起错误分行
                    f.write('%s,%s,%s,%s,%s,%s' % (
                    postid, r_data.json()['com'], r_data.json()['message'], wuliu['time'], wuliu['ftime'], wuliu['context'].replace(',','，') + '\n'))
            sleep(SleepTime)
        f.close()

if __name__ == '__main__':
    '''
    文件说明：
        postid.txt: 待爬取物流信息的物流单号，一行一个物流单号
        main.py: 爬虫的主程序，可直接执行
    参数说明：get_kuaidi(Result_FileName, SleepTime)
        Result_FileName: 储存文件的名字，可自行修改，默认为“Result.txt”
        sleep_time: 每次爬取的停止间隔，越大越不容易被封，默认为“2”
    '''
    get_kuaidi("Result", 3)
