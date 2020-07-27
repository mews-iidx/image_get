import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
import requests
import datetime

def get_image_url(args):
    sleep_between_interactions = 2
    download_num = args.count
    output_dir = args.output_dir
    query = args.k
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    
    
    opt = Options()
    opt.add_argument('--headless')
    wd = webdriver.Chrome(executable_path='./chromedriver', chrome_options=opt)
    wd.get(search_url.format(q=query))
    thumbnail_results = wd.find_elements_by_css_selector("img.rg_i")
    if len(thumbnail_results) < download_num:
        raise ValueError("image results: {}, download_count {}".format(len(thumbnail_results), download_num))
    
    image_urls = set()
    for i, img in enumerate(thumbnail_results[:download_num]):
        try:
            img.click()
            time.sleep(sleep_between_interactions)
        except Exception:
            continue
        url_candidates = wd.find_elements_by_class_name('n3VNCb')
        for candidate in url_candidates:
            url = candidate.get_attribute('src')
            if url and 'https' in url:
                image_urls.add(url)
        print('get : ' + str(i))
    time.sleep(sleep_between_interactions+3)
    wd.quit()

    return image_urls

def url2image(url):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print("ERROR - Could not download {url} - {e}")
    
    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        return image

    except Exception as e:
        print("ERROR - Could not save {url} - {e}".format(url=url, e=e))
    
    


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='検索して保存するやつ')
    parser.add_argument('k', help='検索キーワード')
    parser.add_argument('-c', '--count', help='上位N個の画像', default=3, type=int)
    parser.add_argument('-o', '--output_dir', help='出力先ディレクトリ名', default='data')
    parser.add_argument('-l', '--log', help='ログ', default='logs.txt')

    args = parser.parse_args()

    log = open(args.log, 'a')

    image_urls = get_image_url(args)
    print('finish get_image_url')

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    for i, url in enumerate(image_urls):
        img = url2image(url)
        output_name = os.path.join(args.output_dir, str(i) + '.jpg')
        now = str(datetime.datetime.now())
        with open(output_name, 'wb') as f:
            try:
                img.save(f, "JPEG", quality=90)
            except AttributeError:
                print("file corrupt: " + output_name)
                log.write(now + ',' + output_name + ',' + url + ',FAILED\n')
                continue

            print('saved ' + output_name)
            log.write(now + ',' + output_name + ',' + url + ',SUCCESS\n')
    print('save log ' + args.log)
