import requests
from bs4 import BeautifulSoup
import time
import os
import gzip
import json

class Downloader:
    def __init__(self, url, link_name, directory_name, start_page, last_page):
        self.url = url
        self.link_name = link_name
        self.directory_name = directory_name
        self.start_page = start_page
        self.last_page = last_page
        
    def get_links(self, num):
        while True:
            url = "{0}{1}".format(self.url[:-1], num)
            #e.g., url = "https://bitcointalk.org/index.php?board=57.{0}".format(num)
            time.sleep(0.7) # sleep for 0.7 sec
            r = requests.get(url)
            if (r.status_code == 200):
                soup = BeautifulSoup(r.content, "html5lib")
                id_container = []
                temp = soup.find_all('span')
                for i in temp:
                    try: 
                        id_container.append(i.attrs['id'])
                    except:
                        pass # do nothing
                link_container = set()   
                for id_v in id_container:
                    temp2 = soup.find("span", attrs={"id": id_v})
                    link_container.add(temp2.select("a")[0]['href'])
                return list(link_container)
            else:
                time.sleep(1.0) # sleep for 1 sec
                continue

    def get_links_pages(self):
        temp = {}
        for i in range(self.start_page-1, self.last_page):
            p = "page" + str(i+1)
            temp[p] = self.get_links(i*40)
            print("Page{0} is complete".format(i+1))
        return temp
    
    def helper(self):
        pages = self.get_links_pages()
        with open(self.link_name + ".json", 'w', encoding='utf-8') as fp:
            json.dump(pages, fp)
        with open(self.link_name + ".json", "rb") as fp:
            with gzip.open(self.link_name + ".json.gz", "wb") as fp2:
                fp2.writelines(fp)
        os.remove(self.link_name + ".json")
    
    def make_directory(self, dir_path, dir_name):
        os.mkdir(dir_path + "/" + dir_name + "/")
    
    def get_html(self, address):
        while True:
            url = address
            time.sleep(0.7) # sleep for 0.7 sec
            r = requests.get(url)
            if (r.status_code == 200):
                soup = BeautifulSoup(r.content, "html5lib")
                return str(soup)
            else:
                print(r.status_code)
                time.sleep(1.0) # sleep for 1 sec
                continue

    def get_topic_pages(self, topic_url):
        topic_pages = 0
        while True:
            time.sleep(0.7) # sleep for 0.7 sec
            r = requests.get(topic_url)
            if (r.status_code == 200):
                soup = BeautifulSoup(r.content, "html5lib")
                temp = soup.find_all("a", class_= "navPages")
                if (len(temp) == 0): # The topic has a single page
                    topic_pages = 1
                    return str(soup)
                else: # The topic has multiple pages
                    number_container = []
                    for i in temp:
                        if (i.text != "»"):
                            number_container.append(int(i.text))
                    number_container.sort(reverse=True)
                    topic_pages = number_container[0]
                    return int(topic_pages)
                return -1 # Shouldn't be reached here
            else:
                time.sleep(1.0) # sleep for 1 sec
                continue
        return -1 # Shouldn't be reached here
    
    def collect(self):
        start = time.time()
        pages_links = json.load(gzip.open(self.link_name + ".json.gz", 'rt', encoding='utf-8'))
        try:
            self.make_directory("/Users/chansun/Desktop/b_school_project", self.directory_name)
        except:
            pass
        dir_path = "/Users/chansun/Desktop/b_school_project/" + self.directory_name

        for page in range(self.start_page, self.last_page+1):
            dir_name = "page{0}".format(page)
            print("================ {0} has begun ================".format(dir_name))

            self.make_directory(dir_path, dir_name)
            dir_path_topic = "/Users/chansun/Desktop/b_school_project/" + self.directory_name + "/" + dir_name
            page_html = dir_path_topic + "/" + dir_name + ".html.gz"
            page_url = "{0}{1}".format(self.url[:-1], (page-1)*40)
            content = self.get_html(page_url).encode('utf-8')

            with gzip.open(page_html, 'wb') as f:
                f.write(content)

            for topic in pages_links[dir_name]:
                dir_name_topic = topic.split("?")[1]
                self.make_directory(dir_path_topic, dir_name_topic)         
                temp = self.get_topic_pages(topic)
                if (type(temp) == str):
                    content2 = temp.encode('utf-8')
                    topic_html = dir_path_topic + "/" + dir_name_topic + "/" + dir_name_topic + ".html.gz"
                    with gzip.open(topic_html, 'wb') as f:
                        f.write(content2)
                else:
                    for i in range(1, temp+1):
                        dir_name_page = "{0}{1}".format(topic[:-1], str((i-1)*20))
                        content3 = self.get_html(dir_name_page).encode('utf-8')
                        each_page_html = dir_path_topic + "/" + dir_name_topic + "/" + dir_name_page.split("?")[1] + ".html.gz"
                        with gzip.open(each_page_html, 'wb') as f:
                            f.write(content3)
                print("{0} is complete".format(topic))
            print("time :", time.time() - start, "(sec)")
            print("================ {0} is complete ================".format(dir_name))     

bitcoin_url = "https://bitcointalk.org/index.php?board=57.0"
bitcoin = Downloader(bitcoin_url, "page_links_bitcoin", "bitcoin_speculation", 1, 491)
#bitcoin.helper()
#bitcoin.collect()

altcoin_url = "https://bitcointalk.org/index.php?board=224.0"
altcoin = Downloader(altcoin_url, "page_links_altcoin", "altcoin_speculation", 1, 318)
#altcoin.helper()
#altcoin.collect()

