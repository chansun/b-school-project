import pickle
import os
import gzip
from bs4 import BeautifulSoup
import csv

def strip_data_alt():
    data = []
    for i in range(1, 319):
        try:
            with open('./altcoin_posts/page{0}'.format(i), 'rb') as f:
                data += pickle.load(f)
        except:
            pass
    return data

titles_alt = {}
for j in range(1, 319):
    name = "./altcoin_speculation/page{0}/page{1}.html.gz".format(j, j)
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
            titles_alt[topic_link] = soup.find("span", attrs={"id": id_v}).get_text()

#print(len(titles_alt.keys()))

data_alt = strip_data_alt()

temp1 = []
for key in titles_alt.keys():
    temp1.append(key[key.find("topic="):])
temp2 = set(temp1)

no_titles = set()
for i in range(0, len(data_alt)):
    if data_alt[i][0] not in temp2:
        no_titles.add(data_alt[i][0])
#print(len(no_titles))

# Manually add topic titles for the missing ones, using no_titles.
titles_alt['https://bitcointalk.org/index.php?topic=5106915.0'] = "The next bull run and stability"
titles_alt['https://bitcointalk.org/index.php?topic=5201062.0'] = "WHAT HAPPENS IF BTC TOUCHES 100K ?"

for i in range(0, len(data_alt)):
    try:
        data_alt[i].insert(0, titles_alt["https://bitcointalk.org/index.php?" + data_alt[i][0]])
    except:
        print(data_alt[i])

# Write
f = open('altcoin_posts.csv', 'w', encoding='utf-8')
wr = csv.writer(f)
for i in data_alt:
    wr.writerow(i)
f.close()

# Read
f = open('altcoin_posts.csv', 'r', encoding='utf-8')
rdr = csv.reader(f)
temp3 = list(rdr)

# Check
print(len(temp3))
print(temp3[1])
print(temp3[int(len(temp3)/2)])
print(temp3[-1])
