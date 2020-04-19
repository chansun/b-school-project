import pickle
import os
import gzip
from bs4 import BeautifulSoup
import csv

def strip_data():
    data = []
    for i in range(0, 25665):
        try:
            with open('./bitcoin_posts/page1_topic=178336.0/page1_topic=178336.{0}'.format(i*20), 'rb') as f:
                temp = pickle.load(f)
                for j in temp:
                    data.append(j)
        except:
            pass
    for i in range(1, 492):
        try:
            with open('./bitcoin_posts/page{0}'.format(i), 'rb') as f:
                data += pickle.load(f)
        except:
            pass
    return data

titles = {}
for j in range(1, 492):
    name = "./bitcoin_speculation/page{0}/page{1}.html.gz".format(j, j)
    with gzip.open(name, "rb") as fp:
        content = fp.read().decode("utf-8")
        soup = BeautifulSoup(content, "html5lib")
        id_container = []
        temp = soup.find_all('span')
        for i in temp:
            try: 
                id_container.append(i.attrs['id'])
            except:
                pass # do nothing
        link_container = set()
        for id_v in id_container:            
            topic_link = soup.find("span", attrs={"id": id_v}).find('a').attrs['href']
            titles[topic_link] = soup.find("span", attrs={"id": id_v}).get_text()

#print(len(titles.keys()))

data = strip_data()

temp1 = []
for key in titles.keys():
    temp1.append(key[key.find("topic="):])
temp2 = set(temp1)

no_titles = set()
for i in range(0, len(data)):
    if data[i][0] not in temp2:
        no_titles.add(data2[i][0])
#print(len(no_titles))

# Manually add topic titles for the missing ones, using no_titles.
titles["https://bitcointalk.org/index.php?topic=5210374.0"] = "Bitcoin Price Prediction 2019, 2020, 2025, 2030, 2040"
titles["https://bitcointalk.org/index.php?topic=5165037.0"] = "Bitcoin Dominance rising again. What is happening?"
titles["https://bitcointalk.org/index.php?topic=5209110.0"] = "Extrapolating 2014 Correction: Could $6,500 Be The Low For Bitcoin?"
titles["https://bitcointalk.org/index.php?topic=5205218.0"] = "Can bitcoin readh 10000usd this year again?"
titles["https://bitcointalk.org/index.php?topic=5210774.0"] = "December’s Significance for Bitcoin: All-Time Highs and Bearish Bottoms"
titles["https://bitcointalk.org/index.php?topic=5210259.0"] = "Plustoken owners may be driving down the price of bitcoin - Chainanalysis blog"
titles["https://bitcointalk.org/index.php?topic=5188537.0"] = "Bitcoin Still Repeating History? 10 Part TA Series (September-October 2019)"
titles["https://bitcointalk.org/index.php?topic=5196072.0"] = "Yet another analyst"
titles["https://bitcointalk.org/index.php?topic=5205105.0"] = "That Crypto Guy Takes Profit From BTC Long"
titles["https://bitcointalk.org/index.php?topic=5158368.0"] = "Bitcoin dominance hits 71.2%, alts lagging behind"

for i in range(0, len(data)):
    try:
        data[i].insert(0, titles["https://bitcointalk.org/index.php?" + data[i][0]])
    except:
        print(data[i])

# Write
f = open('bitcoin_posts.csv', 'w', encoding='utf-8')
wr = csv.writer(f)
for i in data:
    wr.writerow(i)
f.close()

# Read
f = open('bitcoin_posts.csv', 'r', encoding='utf-8')
rdr = csv.reader(f)
temp3 = list(rdr)

# Check
print(len(temp3))
print(temp3[1])
print(temp3[int(len(temp3)/2)])
print(temp3[-1])
