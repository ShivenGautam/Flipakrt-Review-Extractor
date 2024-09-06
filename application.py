from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
from pymongo.mongo_client import MongoClient
import csv
import os
import time
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pymongo

application = Flask(_name_) # initializing a flask app
app = application

@app.route('/',methods =['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/review',methods = ['POST','GET'])
@cross_origin()

def index():
    if request.method == 'POST':
        try:
            DRIVER_PATH = r"chromedriver.exe"
            service = Service(DRIVER_PATH)

            #initiating the webdriver
            driver = webdriver.Chrome(service=service)

            searchString = request.form['content'].replace(" ","")

            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            driver.get(flipkart_url)
            flipkart_page = driver.page_source
            flipkart_html = bs(flipkart_page,'html.parser')
            bigboxes = flipkart_html.findAll('div',{'class': 'tUxRFH'})
            if len(bigboxes) >3 :
                del bigboxes[0:3]
            elif len(bigboxes) == 0:
                return "No products found"
            if len(bigboxes)>0:
                prod_link = "https://www.flipkart.com" + bigboxes[0].div.div.div.a['href']
            else:
                return "No products found after filtering."
            driver.get(prod_link)
            prod_page = driver.page_source
            prod_html = bs(prod_page,'html.parser')
            commentboxes = prod_html.find_all('div',{'class': "_16PBlm"})

            filename = searchString+".csv"
            with open (filename,'w',encoding = 'utf-8') as fw:
                headers = ["Price","Product","Customer Name","Rating","Heading","Comment" ]
                writer = csv.DictWriter(fw,headers)
                writer.writeheader()

                reviews = []

                for commentbox in commentboxes:
                    try:
                        price_ele = flipkart_html.find('div', {'class': '_25b18c'}).find('div', {'class': '_30jeq3'})
                        if len(price_ele) > 0:  # *Fix 2: Check if price_ele has elements*
                            price = price_ele[0].text
                        else:
                            price = "There is no price for this product"
                    except:
                        price = "There is no price for this product"
                    
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})
                        if len(name) > 0:  # *Fix 3: Check if name has elements*
                            name = name[0].text
                        else:
                            name = "No name for this product"
                    except:
                        name = "No name of this product"
                    try:
                        rating  = commentbox.div.div.find_all('div',{'class':'_3LWZlK _1BLPMq'})[0].text
                        if len(rating) > 0:  # *Fix 4: Check if rating has elements*
                            rating = rating[0].text
                        else:
                            rating = "No rating for this product"
                    except:
                        rating = "No rating for this product"
                    try:
                        commentHead = commentbox.div.div.div.p.text
                        if commentHead:  # *Fix 5: Check if commentHead exists*
                            commentHead = commentHead.text
                        else:
                            commentHead = "No comment heading for this product"
                    except:
                        commentHead = "No comment heading for this product"
                    try:
                        comtag = commentbox.div.div.find_all('div',{'class':''})
                        if len(comtag) > 0:  # *Fix 6: Check if comtag has elements*
                            custComment = comtag[0].div.text
                        else:
                            custComment = "No comment for this product" 
                    except Exception as e:
                        print("Exception while creating dictionary: ",e)
                    mydict = {"Price":price,"Product":searchString,"Customer Name":name,"Rating":rating,"Heading":commentHead,"Comment":custComment}  
                    reviews.append(mydict) 
                
                writer.writerows(reviews)

            
            

            
            # client = pymongo.MongoClient("mongodb+srv://saman_323:saman323@cluster0.9i3r4fz.mongodb.net/?retryWrites=true&w=majority")
            # db = client["Flipkart_scrap"]
            # review_col = db['review_scrap_data']
            # review_col.insert_many(reviews)
            driver.quit()
            return render_template('results.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'Something is wrong'
        
    else:
        return render_template('index.html')

if _name_ == "_main_":
    app.run(host='127.0.0.1',port=8000,debug=True)
