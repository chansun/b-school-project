import time
import os
import gzip
from bs4 import BeautifulSoup
import pickle
import multiprocessing

def post_helper(posts):
    temp = []
    temp2 = []
    for post in posts:
        temp.append(int(post.split(".")[1]))
    for i in sorted(temp):
        temp2.append(posts[0].split(".")[0] + "." + str(i) + "." + posts[0].split(".")[2] + "." + posts[0].split(".")[3])
    return temp2

def date_and_time(content):
    dates = []
    soup = BeautifulSoup(content, "html5lib")
    div_temp = soup.find_all("div", class_="smalltext")
    dates = []
    for div in div_temp:
        if "PM" in div.get_text() or "AM" in div.get_text():
            try:
                editplain = div.find("span", class_="editplain")
                temp = str(div).replace(str(editplain), "")
                temp_soup = BeautifulSoup(temp, "html5lib")
                dates.append(temp_soup.get_text())
                continue
            except:
                pass
            dates.append(div.get_text())
    return data_and_time_helper(dates)

def data_and_time_helper(dates):
    date_and_time = []
    dates = [i for i in dates if len(i) <= 40]
    for i in dates:
        temp = i.split(",")
        if len(temp) == 1 and "Today" in temp[0]:
            date_and_time.append(("Today", temp[0][9:]))
            print("temp[0][9:]: {0}".format(temp[0][9:]))
            print("temp: {0}".format(temp))
            print("len(temp): {0}".format(len(temp)))
        else:
            date_and_time.append((temp[0]+temp[1], temp[2][1:]))
    return date_and_time

def id_and_link(content):
    id_and_links = []
    avoid_me = []
    soup = BeautifulSoup(content, "html5lib")
    tb_temp = soup.findAll("td", {'class':["poster_info"]})
    for i in tb_temp:
        if "Personal Message (Offline)" in str(i):
            temp = i.find("a")
            avoid_me.append(temp.get_text())
            continue
        temp = i.find("a")
        if temp == None:
            id_and_links.append(("Guest", "None"))
        else:
            id_and_links.append((temp.get_text(), temp['href']))
    return (id_and_links, avoid_me)

def contents(content, avoid_me):
    soup = BeautifulSoup(content, "html5lib")
    table_temp = soup.findAll("table", {'border':"0", "cellpadding":"3", "cellspacing":"0", "width":"100%"})
    div_temp = [i for i in table_temp if '''class="post"''' in str(i)]
    msg_ids = []
    contents = []
    quotes = []
    merits = []
    for div in div_temp:
        temp = ""
        try:
            msg_id = div.find("div", class_="subject").find("a").attrs['href']
            div_post = div.find("div", class_="post")
            quotes_here = quotes_info2(div_post)
            merits_here = merit_info(div)
            quoteheader = div_post.find_all("div", class_="quoteheader")
            quote = div_post.find_all("div", class_="quote")
            temp = str(div_post)
            for k in quote:
                temp = temp.replace(str(k), "")
            for k in quoteheader:
                temp = temp.replace(str(k), "")
            temp_soup = BeautifulSoup(temp, "html5lib")
            if temp_soup.get_text() not in avoid_me:
                msg_ids.append(msg_id)
                contents.append(temp_soup.get_text())
                quotes.append(quotes_here)
                merits.append(merits_here)
            continue
        except:
            pass
        try:
            div_post = div.find("div", class_="post")
            if div_post.get_text() not in avoid_me:
                msg_id = div.find("div", class_="subject").find("a").attrs['href']
                msg_ids.append(msg_id)
                contents.append(div_post.get_text())
                quotes_here = quotes_info2(div_post)
                merits_here = merit_info(div)
                quotes.append(quotes_here)
                merits.append(merits_here)
        except:
            pass
    return [msg_ids, contents, quotes, merits]

def quotes_info(table):
    quote_temp = table.findAll("div", {"class":"quote"})
    quotes = []
    for quote in quote_temp:
        destroy_me = quote.findAll("div", {"class":"quoteheader"})
        for i in destroy_me:
            i.decompose()
        destroy_me2 = quote.findAll("div", {"class":"quote"})
        for i in destroy_me2:
            i.decompose()
    for i in quote_temp:
        if str(i.get_text()) != "":
            quotes.append(str(i.get_text()))
    return quotes

def quotes_info2(table2):
    table = table2
    quote_temp = table.findAll("div", {"class":"quote"})
    for quote in quote_temp:
        destroy_me = quote.findAll("div", {"class":"quoteheader"})
        for i in destroy_me:
            i.decompose()
        destroy_me2 = quote.findAll("div", {"class":"quote"})
        for i in destroy_me2:
            i.decompose()
    quote_temp = table.findAll("div", {"class":"quoteheader"})
    quotes = []
    for i in quote_temp:
        if i.find("a"):
            quotes.append(i.find("a").attrs['href'])
    return quotes

def merit_info(table):
    merit_info = []
    span_temp = table.findAll("div", {'class':"smalltext"})
    span_temp = [j for j in span_temp if '''<span style="color:green">Merited</span>''' in str(j)]
    for i in span_temp:
        temp = str(i.get_text())
        temp = temp[11:]
        temp2 = temp.split(",")
        temp2 = [i.strip() for i in temp2]
        for j in temp2:
            merit_info.append(user_merit_helper(j))
    return merit_info


def user_merit_helper(user_merit):
    user = ""
    merit = -1
    index = -1
    for i in range(len(user_merit)-1, -1, -1):
        if user_merit[i] == "(":
            index = i
            break
    user = user_merit[:i-1]
    merit = int(user_merit[i+1:-1])
    return [user, merit]

def put_pages(input_arr):
    start = input_arr[0]
    end = input_arr[1]
    for i in range(start, end):
        rows = []
        print("\nPage{0} started\n".format(i))
        start_time = time.time()
        path = "./altcoin_speculation/page{0}/".format(i)
        topic_folders = os.listdir(path)
        topic_folders = [folder for folder in topic_folders if folder[:6] == "topic="]
        try:
            topic_folders.remove("topic=178336.0") # for page 1
        except:
            pass
        for topic in topic_folders:
            second_path = path + topic + "/"
            posts = os.listdir(second_path)
            posts = [post for post in posts if post[-8:] == ".html.gz"] # .DS_store may exist
            posts = post_helper(posts)
            topic_temp = []
            for post in posts:
                print("post: {0}".format(post))
                with gzip.open(second_path + post, "rb") as fp:
                    content = fp.read().decode("utf-8")
                    date_time = date_and_time(content)
                    id_link_temp = id_and_link(content)
                    id_link = id_link_temp[0]
                    comments = contents(content, id_link_temp[1])
                    for index in range(0, len(date_time)):             
                        temp = [topic, post]
                        temp.append(comments[0][index])
                        temp.append(comments[1][index])
                        temp.append(comments[2][index])
                        temp.append(comments[3][index])
                        temp.append(date_time[index][0])
                        temp.append(date_time[index][1])
                        temp.append(id_link[index][0])
                        temp.append(id_link[index][1])
                        topic_temp.append(temp)
            rows += topic_temp    
        print("time :", time.time() - start_time, "(sec)")
        print("========================page{0} is complete!==========================".format(i))
        with open('./altcoin_posts/page{0}'.format(i), 'wb') as f:
            pickle.dump(rows, f)

if __name__ == "__main__":
    print("Start page(inclusive): ")
    start = int(input())
    print("End page(exclusive): ")
    end = int(input())

    measure = time.time()

    if (end-start) >= 2:
        mid = int((end+start)/2)
        rangers = [[start,mid], [mid,end]]
        # Use 2 processes
        pool = multiprocessing.Pool(processes=2)
        pool.map(put_pages, rangers)
        pool.close()
        pool.join()
    else:
        put_pages([start, end])

    print("\n\n***** Total Time: {0} *****\n\n".format(time.time() - measure))

# Pickle Write Example
#import pickle
#list = ['a', 'b', 'c']
#with open('page_', 'wb') as f:
#    pickle.dump(list, f)

# Pickle Read Example
#with open('page_', 'rb') as f:
#    data = pickle.load(f) # read every line
#    print(data)

# Exceptional cases:
# For the date, "Today" may exist
# For the content, "del" may exist
# For the topic, "del" may exist
# For the user, "Guest" may exist