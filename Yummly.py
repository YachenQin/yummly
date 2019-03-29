#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 23:51:11 2019

@author: qinyachen
"""

from bs4 import BeautifulSoup
import requests
import json
from enum import Enum
import re
import time
import sys
import os

nameset = set()
authorset = set()
recipePhotoset = set()
total = 0

class recipeType(str,Enum):
    main: str = "Main course"
    drink: str = "Drink"
    breakfast: str = "Breakfast"
    dessert: str = "Dessert"
    salad: str = "Salad"
    

    
def crawlerall():
    try:
        maxresult = [2000,1500,1000,500,200,100]
        for maxnum in maxresult:
            response = response = requests.get(f"https://www.yummly.com/recipes?maxResult={maxnum}").content
            soup = BeautifulSoup(response,'lxml')
            items = soup.find('div', class_="structured-data-info")
            recipe = items.script.text
            recipe_json = json.loads(recipe)
            recipe_items = recipe_json['itemListElement']
            #print(maxresult)
            if(len(recipe_items)>50):
                break
        return recipe_items
    except AttributeError:
        print("wait 3 seconds")
        #print(tech,country)
        print("mainpage")
        time.sleep(3)
    
def crawler(tech,country):
    try:
        #response = requests.get(f"https://www.yummly.com/recipes?maxResult={maxResult}").content
        maxresult = [1500,1000,500,200,100]
        for maxnum in maxresult:
            response = requests.get(f"https://www.yummly.com/recipes?allowedCuisine=cuisine%5Ecuisine-{country}&allowedCuisine=cuisine%5Ecuisine-{tech}&maxResult={maxnum}").content
            soup = BeautifulSoup(response,'lxml')
            items = soup.find('div', class_="structured-data-info")
            recipe = items.script.text
            recipe_json = json.loads(recipe)
            recipe_items = recipe_json['itemListElement']
            if(len(recipe_items)>50):
                break  
        return recipe_items
    except AttributeError:
        print("wait 3 seconds")
        print(tech,country)
        time.sleep(3)


def create_output_file(recipe_items,file):
    count = 0
    if(recipe_items is None):
        return
    
    #which means the website go to the find nothing page
    if( len(recipe_items)==36):
        return
    for recipe_item in recipe_items:
        
        #the token to decide if this recipe is repeat or not
        judge = 0 
        if( "url" in recipe_item):
            recipeUrl = recipe_item["url"]
        else:
            recipeUrl = None
    
        if( "name" in recipe_item):
            recipeName = recipe_item["name"]
            if(recipeName in nameset):
                judge = judge + 1
            nameset.add(recipeName)
        else:
            recipeName = None
    
        if( "image" in recipe_item):
            recipePhoto = recipe_item["image"]
            if(recipePhoto in recipePhotoset):
                judge = judge + 1
            recipePhotoset.add(recipePhoto)
        else:
            recipePhoto = None
    
        if( "recipeIngredient" in recipe_item):
            ingredients = recipe_item["recipeIngredient"]
        else:
            ingredients = None
    
    
        if( "aggregateRating" in recipe_item):
            ratings = float(recipe_item["aggregateRating"]['ratingValue'])
        else:
            ratings = None
    
        if( "totalTime" in recipe_item):
            cookTime = recipe_item["totalTime"]
        else:
            cookTime = None
            
        if("author" in recipe_item):
            author = recipe_item["author"]["name"]
            if(author in authorset):
                judge = judge + 1
            authorset.add(author)
    
        if( "recipeYield" in recipe_item):
            serveall = recipe_item["recipeYield"]
            serve = int(re.findall(r"\d",serveall)[0])
        else:
            serve = None
    
        if( "keywords" in recipe_item):
            tags = recipe_item["keywords"]
        else:
            tags = None
        
        recipetype = get_type(tags)
    
        recipe_one = dict(recipeUrl=recipeUrl,
             recipeName=recipeName,
             recipePhoto=recipePhoto,
             ingredients=ingredients,
             ratings = ratings,
             cookTime=cookTime,
             serve=serve,
             tags=tags,
             recipeType = recipetype
             )
        #if there are more than one elements(recipe name,author,recipe photo) are repeat before, we consider this recipe as repeat one and didn't add it to the output
        if(judge < 2):
            json_output = json.dumps(recipe_one,indent=2)
            file.write(json_output+"\n")
            count = count + 1
    global total
    total =total + count    
    print(total)

def get_type(tags):
    if(tags is None):
        return None
    if(re.search("main",tags,re.IGNORECASE)!=None):
        return recipeType.main
    if(re.search("drink",tags,re.IGNORECASE)!=None):
        return recipeType.drink
    if(re.search("breakfast",tags,re.IGNORECASE)!=None):
        return recipeType.breakfast
    if(re.search(r"dessert|desserts",tags,re.IGNORECASE)!=None):
        return recipeType.dessert
    if(re.search("salad|salads",tags,re.IGNORECASE)!=None):
        return recipeType.salad
    else:
        return None
    
if __name__ == "__main__":
    
    #file = open('/Users/qinyachen/Documents/yummly/output.txt','w+')
    
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} filename")
        filename = sys.argv[1]
    if not os.path.exists(filename):
        sys.exit(f"Error: File '{sys.argv[1]}' not found")
        
    file=open(filename,'w+')
    file.write("["+"\n")
    recipe_items = crawlerall()
    create_output_file(recipe_items,file)
    

    cusine=["American","Asian","Barbecue","Cajun&Creole","Chinese","Cuban","English","French","German","Greek","Hawaiian","Hungarian","Indian","Irish","Italian","Japanese","Kid-Friendly","Mediterranean","Mexican","Moroccan","Portuguese","Southern&SoulFood","Southwestern","Spanish","Swedish","Thai"]
    technique=["Baking","Blending","Boiling","Braising","Brining","Broiling","Browning","Canning","Drying","Frosting","Frying","Glazing","Grilling","Marinating","Microwaving","Pickling","Poaching","Pressure","Cooking","Roasting","Sauteeing","Slow","Cooking","Steaming","Stir","Frying","Stuffing"]
    for country in cusine:
        for tech in technique:
            country = country.lower()
            tech = tech.lower()
            recipe_items = crawler(tech,country)
            create_output_file(recipe_items,file)
    
    
    file.write("]")
    file.close

    


