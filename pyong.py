from pymongo import MongoClient
import requests
from bs4 import  BeautifulSoup
import time
from selenium import webdriver
from flask import Flask,render_template,jsonify,request

# 셀레니움으로 크롤링 할 경우 하나하나 검색하는 브라우저가 뜬다. 브라우저를 안뜨게 하기 위해 Option추가
#options = webdriver.ChromeOptions()
#options.add_argument('headless')
#options.add_argument('window-size=1920x1080')
#options.add_argument("disable-gpu")



# 타겟 URL을 읽어서 HTML를 받아오고,
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
naver = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.nhn?sel=pnt&date=20190909',headers=headers)

#mongoDB 생성
client = MongoClient('localhost',27017)
db = client.pyongshik

# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
# 각 사이트 별 parser 생성
soup = BeautifulSoup(naver.text, 'html.parser')
# select를 이용해서, tr들을 불러오기
Navermovies = soup.select('#old_content > table > tbody > tr')
# movies (tr들) 의 반복문을 돌리기
for movie in Navermovies:
    # movie 안에 a 가 있으면,
    a_tag = movie.select_one('td.title > div > a')
    if a_tag is not None:
        title = a_tag.text
        star = movie.select_one('td.point').text
        #다음에서 영화 검색
        driver = webdriver.Chrome(executable_path=r'\Users\kkkwl\chromdriver\chromedriver_win32\chromedriver')
        driver.implicitly_wait(3)
        driver.get("https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&q="+title)
        findingTag_names = driver.find_elements_by_id('moviePoint')
        for tag in findingTag_names:
            print(tag.text)

        driver.quit()

        if 'href' in a_tag.attrs:
            Link=a_tag.attrs['href']
            imgLink = requests.get('https://movie.naver.com/'+Link,headers=headers)
            soup4 = BeautifulSoup(imgLink.text,'html.parser')
            img = soup4.select_one('meta[property="og:image"]')
            imgs = img['content']
            #print(imgs)
            doc = {
                'title' : title,
                'star' : star,
                'img' : imgs

            }
            db.Navermovies.insert_one(doc)


