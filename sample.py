from selenium import webdriver
import requests
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server
import traceback
import pathlib
import time
import json
import sys
import time
import brotli
import base64

class BaseFramework(object):

    def __init__(self):
        self.server = Server('./browsermob-proxy-2.1.4/bin/browsermob-proxy')
        self.server.start()
        self.proxy = self.server.create_proxy(params={'trustAllServers': 'true'})
        #print(dir(self.proxy))

        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))

        self.browser = webdriver.Chrome(options=chrome_options)

    def process_request(self, request, response):
        pass

    def process_response(self, response, request):
        pass

    def run(self, func, *args):
        self.proxy.new_har(options={
            'captureContent': True,
            'captureHeaders': True,
            "captureCookies": True,
            "captureBinaryContent": True
        })
        func(*args)
        #self.proxy.wait_for_traffic_to_stop(1, 60)
        result = self.proxy.har
        for entry in result['log']['entries']:
            request = entry['request']
            response = entry['response']
            self.process_request(request, response)
            self.process_response(response, request)

        self.scroll_down_for_new_body()

    def scroll_down_for_new_body(self, times=10, sleep_time=2):
        scroll_js = "var height = document.body.scrollHeight; window.scrollTo(0, height);"
        for _ in range(times):
            self.browser.execute_script(scroll_js)
            time.sleep(sleep_time)

    def __del__(self):
        self.server.stop()
        self.proxy.close
        self.browser.close()


class MovieFramework(BaseFramework):



    def process_request(self, request, response):
        pass
        #print(request["url"])

    def process_response(self, response, request):
        if "web/search/item" in request['url']:
            #print(request, type(request))
            #print(response, type(response))
            text = response['content']['text']
            if text:
                decoded_text = brotli.decompress(base64.b64decode(text)).decode()
                results = json.loads(decoded_text)['data']
                for item in results:
                    try:
                        uri = item.get('aweme_info').get("video").get("play_addr_lowbr").get("url_list")
                        video_desc = item.get('aweme_info').get("desc")
                        #print(uri)
                        #create dir
                        pathlib.Path(keyword).mkdir(parents=True, exist_ok=True)
                        file_name = keyword + "/" + video_desc.strip() + ".mp4"
                        response = requests.get(uri[2])
                        data = response.content
                        with open(file_name, "wb") as fp:
                            fp.write(data)
                            fp.close()
                    except:
                        traceback.print_exc()




    def load(self, url):
        self.browser.get(url)
        time.sleep(3)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        url = "https://www.douyin.com/search/{}?publish_time=0&sort_type=0&source=switch_tab&type=video".format(keyword)
        f = MovieFramework()
        f.run(f.load, url)
    else:
        print(sys.argv)
