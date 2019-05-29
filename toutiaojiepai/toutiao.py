import requests
from urllib.parse import quote, urlencode
import time
import os
from hashlib import md5
from multiprocessing import Pool


def get_page(offset : int) -> dict:
    #原始时间数据
    timestamp_origin = time.time()
    #秒级时间戳
    timestamp = int(timestamp_origin)
    params = {
        # 'keyword': '街拍',
        'aid': '24',
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab':'1',
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': timestamp
    }
    #url地址中，keyword必须放在第一个参数并且和后面的aid不能有’&‘相连，why????????????
    # 大概和requests有关系？因为在浏览器输入获取到的url，里面包含数据
    url = 'https://www.toutiao.com/api/search/content/?keyword=%E8%A1%97%E6%8B%8D'+urlencode(params)
    try:
        s = requests.Session()
        response = s.get(url)
        #或者??response = requests.get('https://www.toutiao.com/api/search/content/', params=data)
        if response.status_code ==200:
            return response.json()
    except requests.ConnectionError:
        return None


def get_images(json:dict) -> dict:
    if json.get('data'):
        for item in json.get('data'):
            # title = item.get('title')
            images = item.get('image_list')
            if images:
                for image in images:
                    yield{
                        'image_url': image.get('url'),
                        'title': item.get('title')
                    }


def save_image(item:dict):
#存储图片，以title和图片的md5值命名，md5去重,写入二进制数据
    title = item.get('title')
    image_url = item.get('image_url')
#将title内的某些字符替换，否则无法新建文件夹
    chr_change = r'/\<>|*:?"'
    for i in chr_change:
        if i in title:
            title = title.replace(i, ' ')
    if not os.path.exists(title):
        os.mkdir(title)
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            file_name = f'{title}\{md5(response.content).hexdigest()}.jpg'
            if not os.path.exists(file_name):
                with open(file_name, 'wb') as f:
                    f.write(response.content)
            else:
                print("Already download", file_name)
    except requests.ConnectionError:
        print('Failed to get image.')


def main(offset:int):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


GROUP_START = 1
GROUP_END = 10


if __name__ == '__main__':
    pool = Pool()
    groups = ([x*20 for x in range(GROUP_START, GROUP_END+1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
