from selenium import webdriver
from bs4 import BeautifulSoup
import MySQLdb as mydb
import os

def Scrape(url):
    global browser
    browser.get(url) #get url
    return browser.page_source

def writeToDB(match,time,one,two):
    global db
    cursor = db.cursor()
    sql = "INSERT INTO leagues (NAME,TIME,ONE,TWO) VALUES (\"" + match + "\",\"" + time + "\",\"" + one + "\",\"" + two + "\");"

    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print "Error occured : %s" % e
        db.rollback()

db_username = "DATABASE USERNAME"
db_password = "DATABASE PASSWORD"
db_name = "DATABASE NAME";
db = mydb.connect("localhost",db_username,db_password,db_name)

driver_path = str(os.path.realpath(__file__))[:-7] + "chromedriver.exe"
browser = webdriver.Chrome(executable_path=driver_path)
url = "http://www.oddsportal.com/basketball/"
results = BeautifulSoup(Scrape(url),"html.parser").findAll("table",{"class":"table-main"})
tr = BeautifulSoup(str(results),"html.parser").findAll("tr")

links = []
for data in tr:
    if not str(data).startswith("<tr class=\"dark center\"") and not str(data).startswith("<tr class=\"center\""): #link to league
        try:
            link = str(data).split(">")[2].split(" ")[2][6:-1] #grab link
            links.append(link)
        except:
            pass 

for league in links:
    url = "http://www.oddsportal.com" + league
    results = BeautifulSoup(Scrape(url),"html.parser").findAll("table",{"class":"table-main"})
    tr = BeautifulSoup(str(results),"html.parser").findAll("tr")
    for data in tr:
        if not str(data).startswith("<tr class=\"dark center\"") and not str(data).startswith("<tr class=\"center") and not str(data).startswith("<tr class=\"table-dummyrow\""): #link to league
            try:
                time = str(BeautifulSoup(str(data),"html.parser").findAll("td",{"class":"table-time"})[0])[-10:-5]
                match = str(BeautifulSoup(str(data),"html.parser").findAll("td",{"class":"name"})[0])[-50:].split(">")[1][:-3]
                odds = BeautifulSoup(str(data),"html.parser").findAll("td",{"class":"odds-nowrp"})
                ones = str(odds[0])[29:33]
                twos = str(odds[1])[29:33]
                if "\"" in ones:
                    ones = ones[:3]
                if "\"" in twos:
                    twos = twos[:3]
                if "." in ones and "." in twos and "-" in match:
                    writeToDB(match,time,ones,twos)
            except:
                pass

browser.quit()
db.close()
