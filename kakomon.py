from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import json
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

#options = Options()
#options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=r'C:\Users\taiza\OneDrive\デスクトップ\selenium\chromedriver.exe')

driver.get('https://www.fe-siken.com/fekakomon.php')

time.sleep(3)
#画面を最大化する
driver.maximize_window()

#旧体制の試験(平成21年春期以前の試験)のチェックボックスのチェックを外す
cnt = 22
while cnt < 32:
    driver.find_element_by_xpath('//*[@id="1"]/label[position() >' + str(cnt)  + ']').click()
    cnt += 1

time.sleep(5)
#「出題開始」ボタンを押下
driver.find_element_by_xpath('//*[@id="configform"]/div[2]/button[1]').click()

#春か否か判断する
def judgeSeason(season):

    if '春' in season:
        isSpring = True
    else:
        isSpring = False

    return isSpring

#年号から西暦を求める
def judgeYear(year):
    if '元年' == year:#令和元年だけは数字ではないので指定する
        seireki = 2019
    else:
        seireki = int(year) - 12 + 2000
    
    return seireki

#ジャンルを番号に変換するための辞書
genre_num = {}
#jsonファイルとして出力する辞書型 
output = []
#選択肢ア～エを数字に変換
conversion = {'ア':1,'イ':2,'ウ':3,'エ':4}
num = 1

time.sleep(5)
while num < 100:
    mondaiInfo = dict.fromkeys(['question_id', 'question_statement', 'choise_1','choise_2','choise_3','choise_4','answer','explanation','large_genre_id','middle_genre_id','small_genre_id','year','isSpring'])

    #id
    mondaiInfo['question_id'] = num

    time.sleep(3)
    #問題文
    if num == 1:#なぜか一問目がずれるから
        mondaiInfo['question_statement'] = driver.find_element_by_xpath('/html/body/div[1]/div/main/div[2]/div[1]').text
    else:
        mondaiInfo['question_statement'] = driver.find_element_by_css_selector('#mainCol > div.main.kako.doujou > div:nth-child(4)').text
            
    #print(mondai)
    #選択肢1~4選択肢に文章がないものに関しては例外処理を行う
    try:
        mondaiInfo['choise_1'] = driver.find_element_by_xpath('//*[@id="select_a"]').text    
        mondaiInfo['choise_2'] = driver.find_element_by_xpath('//*[@id="select_i"]').text
        mondaiInfo['choise_3'] = driver.find_element_by_xpath('//*[@id="select_u"]').text
        mondaiInfo['choise_4'] = driver.find_element_by_xpath('//*[@id="select_e"]').text
    except NoSuchElementException:
        mondaiInfo['choise_1'] = driver.find_element_by_xpath('//*[@id="mainCol"]/div[2]/div[4]/ul/li[2]/ul/li[1]/a/button').text
        mondaiInfo['choise_2'] = driver.find_element_by_xpath('//*[@id="mainCol"]/div[2]/div[4]/ul/li[2]/ul/li[2]/a/button').text
        mondaiInfo['choise_3'] = driver.find_element_by_xpath('//*[@id="mainCol"]/div[2]/div[4]/ul/li[2]/ul/li[3]/a/button').text
        mondaiInfo['choise_4'] = driver.find_element_by_xpath('//*[@id="mainCol"]/div[2]/div[4]/ul/li[2]/ul/li[4]/a/button').text
    #答えをクリック
    driver.find_element_by_xpath('//*[@id="t"]').click()
    #答えの文章
    #answer_text = driver.find_element_by_xpath('//*[@id="t"]/preceding-sibling::div').text
    #答えの選択肢
    answer_choise = driver.find_element_by_xpath('//*[@id="t"]/button').text
    #答えの選択肢を数字に変換    
    mondaiInfo['answer'] = conversion[answer_choise]# + '/' + answer_text
    time.sleep(3)
    #解説
    kaisetsu = driver.find_element_by_xpath('//*[@id="kaisetsu"]/div[1]').text
    mondaiInfo['explanation'] = kaisetsu
    #春か秋か
    season = driver.find_element_by_class_name('anslink').text
    isSpring = judgeSeason(season)
    mondaiInfo['isSpring'] = isSpring

    #西暦
    year = season[2:4]#3,4文字目を抽出すれば年度が取ってこれる
    seireki = judgeYear(year)
    mondaiInfo['year'] = seireki

    #大中小で分類分け
    genre = driver.find_element_by_xpath('//*[@id="mainCol"]/div[2]/p').text

    #「»」で分割したリストを作成する
    splited_genre = genre.split('»') 

    large_genre = splited_genre[0]
    middle_genre = splited_genre[1]
    small_genre = splited_genre[2]

    mondaiInfo['small_genre_id'] = small_genre
    mondaiInfo['middle_genre_id'] = middle_genre
    mondaiInfo['large_genre_id'] = large_genre
    
    output.append(mondaiInfo)

    time.sleep(3)
    #次の問題へ
    driver.find_element_by_xpath('//*[@id="configform"]/div[1]/button[1]').click()
    
    time.sleep(3)
    num += 1

#jsonファイルを作成し、書き込み
with open(r'C:\OJT\sample.json', 'w') as f:
    json.dump(output, f, ensure_ascii=False,indent=4)


