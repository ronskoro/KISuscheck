# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import sys
sys.path.append(
    'C:/Users/maria/anaconda3/envs/KI-SusCheck-faq/Lib/site-packages')
# import time
from sentence_transformers import SentenceTransformer, util
from rasa_sdk.events import SlotSet, FollowupAction
# , EventType
# import torch
from sentence_transformers import SentenceTransformer
import os
from gpt_integration.processor import QueryEngine, openaiChatCompletion
from explanation.explanation_helper import Explanator
import numpy as np
import pandas as pd
from typing import Text, Dict, Any, List
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType
import requests
import json


class getProductAnimalFriendlinessInfo(Action):
    def name(self) -> Text:
        return "action_get_product_animal_friendliness_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")

        barcode = barcode_slot
        openaiContent = ""
        followupActionFlag = False

        # vegan=0.5
        # vegetarian=0.5
        # palm_oil=0.5
        vegan = float(tracker.slots["product_vegan"])
        vegetarian = float(tracker.slots["product_vegetarian"])
        palm_oil = float(tracker.slots["product_palm_oil"])

        ingredient_preferences = tracker.slots["ingredient_preference"]
        vegan_preference = False
        if (ingredient_preferences is not None and "vegan" in ingredient_preferences):
            vegan_preference = True

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if (barcode is not None):
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            if (response.status_code == 200 and response.json().get('product') is not None):
                if (response.json()['product'].get("ingredients_analysis_tags") is not None):

                    print(vegan)
                    print(vegetarian)
                    print(palm_oil)

                    if (vegan == 1 and palm_oil == 0):
                        openaiContent +="The product is vegan and it is palm oil free!"
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        
                    if (vegan == 1 and palm_oil == 1):
                        openaiContent +="The product is vegan but it contains palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True
                    if (vegan == 1 and palm_oil == 0.5):
                        openaiContent +="The product is vegan. However, it may contain palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True

                    if (vegetarian == 1 and palm_oil == 0):
                        openaiContent +="The product is vegetarian and it is palm oil free!"
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        if (vegan_preference):
                            followupActionFlag = True
                    if (vegetarian == 1 and palm_oil == 1):
                        openaiContent +="The product is vegetarian. However, it contains palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True
                    if (vegetarian == 1 and palm_oil == 0.5):
                        openaiContent +="The product is vegetarian. However, it may contain palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True

                    if (vegetarian == 0 and palm_oil == 0):
                        openaiContent +="The product is non-vegetarian but it is palm oil free."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True
                    if (vegetarian == 0 and palm_oil == 1):
                        openaiContent +="The product is non-vegetarian and it contains palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True
                    if (vegetarian == 0 and palm_oil == 0.5):
                        openaiContent +="The product is non-vegetarian and it may contain palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True

                    if (palm_oil == 0):
                        openaiContent +="The product may be vegan/vegetarian but it is palm oil free."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True
                    if (palm_oil == 1):
                        openaiContent +="The product may be vegan/vegetarian and it contains palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True
                    if (palm_oil == 0.5):
                        openaiContent +="The product may be vegan/vegetarian and it may contain palm oil."
                        openaiContent +="Palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                        followupActionFlag = True
                    messages = [{"role": "system", "content": openaiContent + "Rephrase the statement to match the user's question. Provide context that this determines the animal-friendliness status of the product. The answer should not be vague and shouldn't contain any questions."},
                            {"role": "user", "content": tracker.latest_message['text']},]
                    x = openaiChatCompletion(messages)
                    dispatcher.utter_message(x['content'])
                    if(followupActionFlag == True):
                        return [FollowupAction("action_check_animal_friendly_alternative")]
                    else:
                        return [FollowupAction("utter_did_that_help")]
                else:
                    dispatcher.utter_message(
                        text="I don't have information about this product's ingredients, sorry :/")
                    return []
            else:
                dispatcher.utter_message(
                    text="Sorry, I can't find the product.")
                return []
        dispatcher.utter_message(
            text="Oh I could not find that product! Please recheck that you entered it correctly.")

        return []

class checkAnimalFriendlyAlternative(Action):
    def name(self) -> Text:
        return "action_check_animal_friendly_alternative"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("getting an alternative")

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")
        barcode = barcode_slot

        vegan = float(tracker.slots["product_vegan"])
        vegetarian = float(tracker.slots["product_vegetarian"])
        palm_oil = float(tracker.slots["product_palm_oil"])

        ingredient_preferences = tracker.slots["ingredient_preference"]
        vegan_preference = False
        if (ingredient_preferences is not None and "vegan" in ingredient_preferences):
            vegan_preference = True

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if (barcode is not None):
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            if (response.status_code == 200 and response.json().get('product') is not None):
                if (response.json()['product'].get("ingredients_analysis_tags") is not None and
                   response.json()['product'].get("categories_tags") is not None):

                    if (vegan == 1 and palm_oil != 0):
                        dispatcher.utter_message(
                            text="Would you like an alternative that is palm oil free and is also vegan?")

                    elif (vegetarian == 1 and palm_oil == 0):
                        if (vegan_preference):
                            dispatcher.utter_message(
                                text="Since you prefer vegan products, would you like a vegan alternative that is also palm oil free?")

                    elif (vegetarian == 1 and palm_oil != 0):
                        if (vegan_preference):
                            dispatcher.utter_message(
                                text="Since you prefer vegan products, would you like a vegan alternative that is palm oil free?")
                        else:
                            dispatcher.utter_message(
                                text="Would you like an alternative that is palm oil free and is also vegetarian?")

                    elif (palm_oil == 0):
                        if (vegan_preference):
                            dispatcher.utter_message(
                                text="Would you like a vegan alternative that is also palm oil free?")
                        else:
                            dispatcher.utter_message(
                                text="Would you like a vegetarian alternative that is also palm oil free?")

                    elif (palm_oil != 0):
                        if (vegan_preference):
                            dispatcher.utter_message(
                                text="Would you like a vegan alternative that is palm oil free?")
                        else:
                            dispatcher.utter_message(
                                text="Would you like a vegetarian alternative that is palm oil free?")

                    return []
                else:
                    # don't suggest an alternative if ingredients or categories tags for the product are missing
                    return [FollowupAction("utter_did_that_help")]
            else:
                dispatcher.utter_message(
                    text="Sorry, I can't find the product.")
                return []
        dispatcher.utter_message(
            text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []


class suggestAnimalFriendlyAlternative(Action):
        def name(self) -> Text:
            return "action_suggest_animal_friendly_alternative"
        async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
            # Extract the barcode from the user input
            barcode = None
            barcode_slot = tracker.get_slot("barcode")
            barcode = barcode_slot

            vegan = float(tracker.slots["product_vegan"])
            vegetarian = float(tracker.slots["product_vegetarian"])
            palm_oil = float(tracker.slots["product_palm_oil"])

            ingredient_preferences = tracker.slots["ingredient_preference"]
            vegan_preference = False
            if(ingredient_preferences is not None and "Vegetarian" in ingredient_preferences):
                vegan_preference = True

            # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
            if(barcode is not None):
                response = requests.get('https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
                
                if(response.status_code == 200 and response.json().get('product') is not None):
                    resProduct = response.json()['product']

                    if(resProduct['ingredients_analysis_tags'] is not None
                       and resProduct['categories_tags'] is not None):
                        categories_tags = resProduct['categories_tags']
                        categories_tags_str = ','.join(categories_tags)
                        ingredients_analysis_tags = resProduct['ingredients_analysis_tags']
                        ingredients_analysis_tags_str = ','.join(ingredients_analysis_tags)
                        print(categories_tags_str)
                        print(ingredients_analysis_tags_str)
                        

                        if(vegan == 1 and palm_oil != 0):
                            ingredients_analysis_tags_str = "en:palm-oil-free,en:vegan"
                            url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"

                        elif(vegetarian == 1 and palm_oil == 0):
                            if(vegan_preference):
                                #Since you prefer vegan products, would you like a vegan alternative that is also palm oil free?
                                ingredients_analysis_tags_str = "en:palm-oil-free,en:vegan"
                                url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"
                            else:
                                print("vegetarian and palm oil free and the user doesn't prefer vegan products")
                                return []

                        elif(vegetarian == 1 and palm_oil != 0):
                            if(vegan_preference):
                                #Since you prefer vegan products, would you like a vegan alternative that is palm oil free?
                                ingredients_analysis_tags_str = "en:palm-oil-free,en:vegan"
                                url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"
                            else:
                                #Would you like an alternative that is palm oil free and is also vegetarian?
                                ingredients_analysis_tags_str = "en:palm-oil-free,en:vegetarian"
                                url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"
                        
                        elif(palm_oil == 0):
                            if(vegan_preference):
                                #"Would you like a vegan alternative that is also palm oil free?
                                ingredients_analysis_tags_str = "en:palm-oil-free,en:vegan"
                                url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"

                            else:
                                #Would you like a vegetarian alternative that is also palm oil free?  
                                ingredients_analysis_tags_str = "en:palm-oil-free,en:vegetarian"
                                url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"

                                
                            
                        elif(palm_oil != 0):
                            if(vegan_preference):
                                #Would you like a vegan alternative that is palm oil free?
                                ingredients_analysis_tags_str = "en:palm-oil-free,en:vegan"
                                url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"
                                
                            else:
                                #Would you like a vegetarian alternative that is palm oil free?
                                ingredients_analysis_tags_str = "en:palm-oil-free,en:vegetarian"
                                url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&ingredients_analysis_tags="+ingredients_analysis_tags_str+"&sort_by=popularity_key"
                            
                        else:
                            print("nothing wrong with product")
                            return []
                        
                        # Send GET request
                        response = requests.get(url)

                        # Check if the request was successful
                        if response.status_code == 200:
                            print(url)
                            print("Success")
                            products = response.json()["products"]

                            if(len(products) > 0):
                                if(len(products) < 3):    
                                    dispatcher.utter_message(text="Here you go!")
                                else:    
                                    dispatcher.utter_message(text="Here you go! These are the top 3 products:")
                                for i, alternativeProduct in enumerate(products):
                                    if i == 3:
                                        break
                                    msg = str(i+1) +"- "
                                    img = None
                                    if(alternativeProduct.get("image_url") is not None):
                                        img = alternativeProduct['image_url']
                                    if(alternativeProduct.get("code") is not None):
                                        msg += "("+alternativeProduct['code']+") "
                                    if(alternativeProduct.get("product_name") is not None):
                                        msg += alternativeProduct['product_name']
                                    if(img is not None):
                                        dispatcher.utter_message(image = img, text = msg )
                                    else:
                                        dispatcher.utter_message(text = msg )
                                return[]
                            else:
                                dispatcher.utter_message(text="There were no alternative products found that match the criteria :/")
                                return []
                        else:
                            dispatcher.utter_message(text="There were no alternative products found that match the criteria :/")
                            return []
                    else:
                        dispatcher.utter_message(text="I don't have information about this product's ingredients, sorry :/")
                        return []
                else:
                    dispatcher.utter_message(text="Sorry, I can't find the product.")
                    return []
            dispatcher.utter_message(text="Oh I could not find that product! Please recheck that you entered it correctly.")
            
            return []


#region social impact
class getProductSocialImpactInfo(Action):
    def name(self) -> Text:
        return "action_get_product_social_impact_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")

        barcode = barcode_slot
        fairTradeLabel = False
        openaiContent = ""
        followupActionFlag = False

        
        response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
        
        if (response.status_code == 200 and response.json().get('product') is not None):
            resProduct = response.json()['product']
            if (resProduct.get("labels_tags") is not None):
                if("en:fair-trade" in resProduct.get("labels_tags")):
                    fairTradeLabel = True
            else:
                dispatcher.utter_message("I can't find any labels on this product to answer your question, sorry :/")
                return []
        else:
            dispatcher.utter_message("I can't find this product sorry :/")
            return []
        
        if(fairTradeLabel == False):
            openaiContent += "The product doesn't have a Fair Trade Lable indicating a negative social impact."
            openaiContent += "The fair trade label indicates that the product meets certain social and economic standards, such as fair wages and working conditions, and supports small-scale farmers and workers in developing countries."
            followupActionFlag = True
        else:
            openaiContent += "The product has a Fair Trade Lable indicating a positive social impact."
            openaiContent += "The fair trade label indicates that the product meets certain social and economic standards, such as fair wages and working conditions, and supports small-scale farmers and workers in developing countries."

        messages = [{"role": "system", "content": openaiContent + "Rephrase the statement to match the user's question. Provide context that this determines the social impact status of the product according to the fair trade label. The answer should not be vague and shouldn't contain any questions."},
        {"role": "user", "content": tracker.latest_message['text']},]
        x = openaiChatCompletion(messages)
        dispatcher.utter_message(x['content'])
        if(followupActionFlag == True):
            return [FollowupAction("action_check_positive_social_impact_alternative")]
        else:
            return [FollowupAction("utter_did_that_help")]
class checkPositiveSocialImpactAlternative(Action):
    def name(self) -> Text:
        return "action_check_positive_social_impact_alternative"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("getting an alternative")

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")
        barcode = barcode_slot

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if (barcode is not None):
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            if (response.status_code == 200 and response.json().get('product') is not None and 
                response.json()['product'].get("categories_tags") is not None):
                #https://world.openfoodfacts.org/api/v2/search?categories_tags_en=en:breakfasts&sort_by=popularity_key&labels_tags=en:fair-trade
                dispatcher.utter_message(text="Would you like an alternative that has the Fair Trade label?")
                return []
            else:
                dispatcher.utter_message(text="Sorry, I can't find products of the same category.")
                return []
        dispatcher.utter_message(
            text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []
class suggestPositiveSocialImpactAlternative(Action):
        def name(self) -> Text:
            return "action_suggest_positive_social_impact_alternative"
        async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
            # Extract the barcode from the user input
            barcode = None
            barcode_slot = tracker.get_slot("barcode")
            barcode = barcode_slot

            # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
            if(barcode is not None):
                response = requests.get('https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
                
                if (response.status_code == 200 and response.json().get('product') is not None and 
                    response.json()['product'].get("categories_tags") is not None):
                    resProduct = response.json()['product']
                    categories_tags = resProduct['categories_tags']
                    categories_tags_str = ','.join(categories_tags)
                    print(categories_tags_str)
                        
                    url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"sort_by=popularity_key&labels_tags=en:fair-trade"
                    print(url)
                    # Send GET request
                    response = requests.get(url)

                    # Check if the request was successful
                    if response.status_code == 200:
                        print("Success")
                        products = response.json()["products"]

                        if(len(products) > 0):
                            if(len(products) < 3):    
                                dispatcher.utter_message(text="Here you go!")
                            else:    
                                dispatcher.utter_message(text="Here you go! These are the top 3 products:")
                            for i, alternativeProduct in enumerate(products):
                                if i == 3:
                                    break
                                msg = str(i+1) +"- "
                                img = None
                                if(alternativeProduct.get("image_url") is not None):
                                    img = alternativeProduct['image_url']
                                if(alternativeProduct.get("code") is not None):
                                    msg += "("+alternativeProduct['code']+") "
                                if(alternativeProduct.get("product_name") is not None):
                                    msg += alternativeProduct['product_name']
                                if(img is not None):
                                    dispatcher.utter_message(image = img, text = msg )
                                else:
                                    dispatcher.utter_message(text = msg )
                            return[]
                        else:
                            dispatcher.utter_message(text="There were no alternative products found that match the criteria :/")
                            return []
                        
                    else:
                        dispatcher.utter_message(text="I don't have information about this product's ingredients, sorry :/")
                        return []
                else:
                    dispatcher.utter_message(text="Sorry, I can't find the product.")
                    return []
            dispatcher.utter_message(text="Oh I could not find that product! Please recheck that you entered it correctly.")
            
            return []

#endregion

#region nutritional value
class getProductNutritionalValueInfo(Action):
    def name(self) -> Text:
        return "action_get_product_nutritional_value_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")

        barcode = barcode_slot
        nutriscore = "e"
        nutrient_levels_tags = ""
        openaiContent = ""
        followupActionFlag = False

        response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
        
        if (response.status_code == 200 and response.json().get('product') is not None):
            resProduct = response.json()['product']
            if (resProduct.get("nutriscore_grade") is not None 
                and resProduct.get("nutrient_levels_tags") is not None):
                nutrient_levels_tags = resProduct['nutrient_levels_tags']
                nutriscore = resProduct['nutriscore_grade']
                nutrient_levels_tags_str = ','.join(nutrient_levels_tags)
            else:
                dispatcher.utter_message("I can't find the nutritional value information of this product, sorry :/")
                return []
        else:
            dispatcher.utter_message("I can't find this product sorry :/")
            return []
        
        
        if(nutriscore == "a"):
            openaiContent += "The product has a nutriscore (a) which indicates a high nutritional value."
        elif(nutriscore == "b"):
            openaiContent += "The product has a nutriscore (b) which indicates a relatively high nutritional value."
            followupActionFlag = True
        elif(nutriscore == "c"):
            openaiContent += "The product has a nutriscore (c) which indicates a moderate nutritional value."
            followupActionFlag = True
        elif(nutriscore == "d"):
            openaiContent += "The product has a nutriscore (d) which indicates a low nutritional value."
            followupActionFlag = True
        else:
            openaiContent += "The product has a nutriscore (e) which indicates a very low nutritional value."
            followupActionFlag = True

        messages = [{"role": "system", "content": openaiContent + "Rephrase the statement to match the user's question. Use the following tags to explain why the product has this nutriscore:"+nutrient_levels_tags_str+" The answer should not be vague and shouldn't contain any questions."},
        {"role": "user", "content": tracker.latest_message['text']},]
        x = openaiChatCompletion(messages)
        dispatcher.utter_message(x['content'])
        if(followupActionFlag == True):
            return [FollowupAction("action_check_high_nutritional_value_alternative")]
        else:
            return [FollowupAction("utter_did_that_help")]
class checkHighNutritionalValueAlternative(Action):
    def name(self) -> Text:
        return "action_check_high_nutritional_value_alternative"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("getting an alternative")

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")
        barcode = barcode_slot

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if (barcode is not None):
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            if (response.status_code == 200 and response.json().get('product') is not None and 
                response.json()['product'].get("categories_tags") is not None and
                response.json()['product'].get("nutriscore_grade") is not None 
                and response.json()['product'].get("nutrient_levels_tags") is not None):
                #https://world.openfoodfacts.org/api/v2/search?categories_tags_en=en:breakfasts&sort_by=popularity_key&labels_tags=en:fair-trade
                dispatcher.utter_message(text="Would you like an alternative that has a higher nutriscore?")
                return []
            else:
                dispatcher.utter_message(text="Sorry, I can't find products of the same category.")
                return []
        dispatcher.utter_message(
            text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []
class suggestHighNutritionalValueAlternative(Action):
        def name(self) -> Text:
            return "action_suggest_high_nutritional_value_alternative"
        async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
            # Extract the barcode from the user input
            barcode = None
            barcode_slot = tracker.get_slot("barcode")
            barcode = barcode_slot

            # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
            if(barcode is not None):
                response = requests.get('https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
                
                if (response.status_code == 200 and response.json().get('product') is not None and 
                    response.json()['product'].get("categories_tags") is not None and
                    response.json()['product'].get("nutriscore_grade") is not None 
                    and response.json()['product'].get("nutrient_levels_tags")is not None):
                    resProduct = response.json()['product']
                    categories_tags = resProduct['categories_tags']
                    categories_tags_str = ','.join(categories_tags)
                    print(categories_tags_str)
                        
                    url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&sort_by=nutriscore_score"
                    print(url)
                    # Send GET request
                    response = requests.get(url)

                    # Check if the request was successful
                    if response.status_code == 200:
                        print("Success")
                        products = response.json()["products"]

                        if(len(products) > 0):
                            if(len(products) < 3):    
                                dispatcher.utter_message(text="Here you go!")
                            else:    
                                dispatcher.utter_message(text="Here you go! These are the top 3 products sorted by nutriscore:")
                            for i, alternativeProduct in enumerate(products):
                                if i == 3:
                                    break
                                msg = str(i+1) +"- "
                                img = None
                                if(alternativeProduct.get("image_url") is not None):
                                    img = alternativeProduct['image_url']
                                if(alternativeProduct.get("code") is not None):
                                    msg += "("+alternativeProduct['code']+") "
                                if(alternativeProduct.get("product_name") is not None):
                                    msg += alternativeProduct['product_name']
                                if(img is not None):
                                    dispatcher.utter_message(image = img, text = msg )
                                else:
                                    dispatcher.utter_message(text = msg )
                            return[]
                        else:
                            dispatcher.utter_message(text="There were no alternative products found that match the criteria :/")
                            return []
                        
                    else:
                        dispatcher.utter_message(text="I don't have information about this product's ingredients, sorry :/")
                        return []
                else:
                    dispatcher.utter_message(text="Sorry, I can't find the product.")
                    return []
            dispatcher.utter_message(text="Oh I could not find that product! Please recheck that you entered it correctly.")
            
            return []

#endregion
#region environmental impact
class getProductEnvironmentalImpactInfo(Action):
    def name(self) -> Text:
        return "action_get_product_environmental_impact_info"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")

        barcode = barcode_slot
        ecoscore = "e"
        packagings = []
        packagings_str = ""
        palm_oil = float(tracker.slots["product_palm_oil"])
        openaiContent = ""
        followupActionFlag = False

        response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
        
        if (response.status_code == 200 and response.json().get('product') is not None):
            resProduct = response.json()['product']
            if (resProduct.get("ecoscore_grade") is not None 
                and resProduct["ecoscore_data"].get("adjustments").get("packaging").get("packagings") is not None):
                packagings = resProduct["ecoscore_data"].get("adjustments").get("packaging").get("packagings")
                packagings_str = str(packagings)
                ecoscore = resProduct['ecoscore_grade']
            else:
                dispatcher.utter_message("I can't find the environmental impact information of this product, sorry :/")
                return []
        else:
            dispatcher.utter_message("I can't find this product sorry :/")
            return []
        
        if(ecoscore == "a"):
            openaiContent += "The product has a ecoscore (a) which indicates very low environmental impact."
        elif(ecoscore == "b"):
            openaiContent += "The product has a ecoscore (b) which indicates relatively low environmental impact."
            followupActionFlag = True
        elif(ecoscore == "c"):
            openaiContent += "The product has a ecoscore (c) which indicates moderate environmental impact."
            followupActionFlag = True
        elif(ecoscore == "d"):
            openaiContent += "The product has a ecoscore (d) which indicates a high environmental impact."
            followupActionFlag = True
        else:
            openaiContent += "The product has a ecoscore (e) which indicates a very high environmental impact."
            followupActionFlag = True


        if(palm_oil == 0.5):
            openaiContent += "The product may contain palm oil which is bad for the environment as it endangers species and causes deforestation."
        elif(palm_oil == 1):
            openaiContent += "The product contains palm oil which is bad for the environment as it endangers species and causes deforestation."
        else:
            openaiContent += "The product is palm oil free which is good for the environment as it protects endangered species and avoids deforestation."

        messages = [{"role": "system", "content": openaiContent + "Rephrase the statement to match the user's question and explain why the product has the specific ecoscore. Use the following list of packagings to suggest why the product might have this ecoscore:"+packagings_str+" The answer should not be vague and shouldn't contain any questions."},
        {"role": "user", "content": tracker.latest_message['text']},]
        x = openaiChatCompletion(messages)
        dispatcher.utter_message(x['content'])
        if(followupActionFlag == True):
            return [FollowupAction("action_check_positive_environmental_impact_alternative")]
        else:
            return [FollowupAction("utter_did_that_help")]
class checkPositiveEnvironmentalImpactAlternative(Action):
    def name(self) -> Text:
        return "action_check_positive_environmental_impact_alternative"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("getting an alternative")

        # Extract the barcode from the user input
        barcode = None
        barcode_slot = tracker.get_slot("barcode")
        barcode = barcode_slot

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if (barcode is not None):
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            if (response.status_code == 200 and response.json().get('product') is not None and 
                response.json()['product'].get("categories_tags") is not None and
                response.json()['product'].get("ecoscore_data").get("adjustments").get("packaging").get("packagings") is not None):
                #https://world.openfoodfacts.org/api/v2/search?categories_tags_en=en:breakfasts&sort_by=popularity_key&labels_tags=en:fair-trade
                dispatcher.utter_message(text="Would you like an alternative that has a higher ecoscore?")
                return []
            else:
                dispatcher.utter_message(text="Sorry, I can't find products of the same category.")
                return []
        dispatcher.utter_message(
            text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []
class suggestPositiveEnvironmentalImpactAlternative(Action):
        def name(self) -> Text:
            return "action_suggest_positive_environmental_impact_alternative"
        async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
            # Extract the barcode from the user input
            barcode = None
            barcode_slot = tracker.get_slot("barcode")
            barcode = barcode_slot

            # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
            if(barcode is not None):
                response = requests.get('https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
                
                if (response.status_code == 200 and response.json().get('product') is not None and 
                    response.json()['product'].get("categories_tags") is not None and
                    response.json()['product'].get("ecoscore_data").get("adjustments").get("packaging").get("packagings") is not None):
                    resProduct = response.json()['product']
                    categories_tags = resProduct['categories_tags']
                    categories_tags_str = ','.join(categories_tags)
                    print(categories_tags_str)
                        
                    url = "https://world.openfoodfacts.org/api/v2/search?categories_tags_en="+categories_tags_str+"&sort_by=ecoscore_score"
                    print(url)
                    # Send GET request
                    response = requests.get(url)

                    # Check if the request was successful
                    if response.status_code == 200:
                        print("Success")
                        products = response.json()["products"]

                        if(len(products) > 0):
                            if(len(products) < 3):    
                                dispatcher.utter_message(text="Here you go!")
                            else:    
                                dispatcher.utter_message(text="Here you go! These are the top 3 products sorted by ecoscore:")
                            for i, alternativeProduct in enumerate(products):
                                if i == 3:
                                    break
                                msg = str(i+1) +"- "
                                img = None
                                if(alternativeProduct.get("image_url") is not None):
                                    img = alternativeProduct['image_url']
                                if(alternativeProduct.get("code") is not None):
                                    msg += "("+alternativeProduct['code']+") "
                                if(alternativeProduct.get("product_name") is not None):
                                    msg += alternativeProduct['product_name']
                                if(img is not None):
                                    dispatcher.utter_message(image = img, text = msg )
                                else:
                                    dispatcher.utter_message(text = msg )
                            return[]
                        else:
                            dispatcher.utter_message(text="There were no alternative products found that match the criteria :/")
                            return []
                        
                    else:
                        dispatcher.utter_message(text="I don't have information about this product's ingredients, sorry :/")
                        return []
                else:
                    dispatcher.utter_message(text="Sorry, I can't find the product.")
                    return []
            dispatcher.utter_message(text="Oh I could not find that product! Please recheck that you entered it correctly.")
            
            return []

#endregion

class ActionConfirmPreference(Action):
    def name(self) -> Text:
        return "action_confirm_preference"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # preference categories
        preferences = {
            "ingredient_preference": "ingredient preferences",
            "nutr_value_preference": "nutritional value preferences",
            "food_processing_preference": "food processing preferences",
            "allergen_preference": "allergen preferences",
            "label_preference": "label preferences",
            "env_preference": "environmental preferences",
        }

        intent = tracker.get_intent_of_latest_message()

        preference_type = None

        # set the preference type
        if intent == "set_ingredient_preference":
            preference_type = "ingredient_preference"
        elif intent == "set_nutr_value_preference":
            preference_type = "nutr_value_preference"
        elif intent == "set_food_processing_preference":
            preference_type = "food_processing_preference"
        elif intent == "set_allergen_preference":
            preference_type = "allergen_preference"
        elif intent == "set_label_preference":
            preference_type = "label_preference"
        elif intent == "set_env_preference":
            preference_type = "env_preference"
        else:
            msg = "I'm sorry. I didn't get that. Could you specify your preference again?"
            dispatcher.utter_message(text=msg)
            return []

        previous_value = None

        skipped = False
        for event in reversed(tracker.events):
            # Since the slot event is triggered before the action, the latest slot event has the
            # newest value, not the previous value. Therefore, we skip it.
            if event.get("event") == "slot" and event.get("name") == preference_type:
                # set the value if the current slot event has already been skipped
                if skipped:
                    previous_value = event.get("value")
                    break

                skipped = True

        current_values = tracker.get_slot(preference_type) or []

        # extend the previous values with the current values without duplicates.
        if (previous_value is not None):
            [current_values.append(x)
             for x in previous_value if x not in current_values]

        # remove duplicate values
        current_values = list({x for x in current_values})

        msg = f"Ok, got it! I've updated your {preferences[preference_type]} to: {', '.join(current_values)}."
        dispatcher.utter_message(text=msg)
        dispatcher.utter_message(text="Now all you search for will be based on your preferences!🥳")

        product_cat_limit = tracker.get_slot("product_cat_limit")
        if (product_cat_limit is not None):
            for key, val in product_cat_limit.items():
                print(key, val)
                product_cat_limit[key] = 0
                print(key, product_cat_limit[key])

        return [SlotSet(preference_type, current_values), SlotSet("product_cat_limit", product_cat_limit)]

class ActionPrintPreferences(Action):
    def name(self) -> Text:
        return "action_print_preferences"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the values of the preferences from the slots
        ingredient_preference = tracker.get_slot("ingredient_preference")
        nutr_value_preference = tracker.get_slot("nutr_value_preference")
        food_processing_preference = tracker.get_slot(
            "food_processing_preference")
        allergen_preference = tracker.get_slot("allergen_preference")
        label_preference = tracker.get_slot("label_preference")
        env_preference = tracker.get_slot("env_preference")

        msg = "\n"

        if ingredient_preference is not None:
            msg += ', '.join(ingredient_preference)
        if nutr_value_preference is not None:
            msg += ", \n" + ', '.join(nutr_value_preference)
        if food_processing_preference is not None:
            msg += ", \n" + ', '.join(food_processing_preference)
        if allergen_preference is not None:
            msg += ", \n" + ', '.join(allergen_preference)
        if label_preference is not None:
            msg += ", \n" + ', '.join(label_preference)
        if env_preference is not None:
            msg += ", \n" + ', '.join(env_preference)

        if msg == "\n":
            dispatcher.utter_message(
                text="You haven't specified any preferences yet.")
        else:
            dispatcher.utter_message(text="Your preferences are: " + msg)

        return []


class ActionUpdateComparisonListAndLength(Action):
    def name(self) -> Text:
        return "action_update_comparison_list_and_length"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        comparison_path_active = tracker.get_slot("comparison_path_active")
        if comparison_path_active == True:

            product_comparison_list = tracker.get_slot(
                "product_comparison_list")
            if product_comparison_list == None:
                product_comparison_list = []
            barcodes = tracker.get_slot("barcode_list")
            if barcodes != None:
                for barcode in barcodes:
                    if barcode not in product_comparison_list:
                        product_comparison_list.append(barcode)
                    else:
                        dispatcher.utter_message(
                            text="This product ({}) is already in the comparison list.".format(barcode))

            product_comparison_list_length = tracker.get_slot(
                "product_comparison_list_length")
            product_comparison_list_length = len(product_comparison_list)

            return [SlotSet("product_comparison_list", product_comparison_list), SlotSet("product_comparison_list_length", product_comparison_list_length)]

        return []


class ActionShowProductComparisonList(Action):
    def name(self) -> Text:
        return "action_show_product_comparison_list"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        product_comparison_list = tracker.get_slot("product_comparison_list")
        if (product_comparison_list == None or product_comparison_list == []):
            dispatcher.utter_message(
                "The comparison list is currently empty, please add product's barcode.")
        else:
            counter = 0
            for barcode in product_comparison_list:
                counter += 1
                if (barcode is not None):
                    response = requests.get(
                        'https://world.openfoodfacts.org/api/v2/product/'+barcode+'?fields=code,product_name,image_url')
                    if (response.status_code == 200 and response.json().get('product') is not None):
                        if (response.json()['product'].get("image_url") is not None):
                            dispatcher.utter_message(
                                text=str(counter)+". "+response.json()['product']['product_name']+" ("+str(response.json()['product']['code'])+")", image=response.json()['product']['image_url'])
                        else:
                            dispatcher.utter_message(
                                text=str(counter)+". "+response.json()['product']['product_name']+" ("+str(response.json()['product']['code'])+")\n   no image available")
                    else:
                        dispatcher.utter_message(
                            "Oops, I could not find this product with barcode {} 😞 Please recheck if you typed it correctly. Otherwise, it might not be available in our database.".format(barcode))
                else:
                    dispatcher.utter_message(
                        "Sorry, the {}. barcode is invalid (None).".format(counter))
        return []


class ActionCompareProductsByBarcode(Action):
    def name(self) -> Text:
        return "action_compare_products_by_barcode"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        product_comparison_df = None
        product_comparison_list = tracker.get_slot("product_comparison_list")
        if (product_comparison_list == None or product_comparison_list == []):
            dispatcher.utter_message(
                "The comparison list is currently empty, please add product's barcode.")
        elif (len(product_comparison_list) == 1):
            dispatcher.utter_message(
                "There is only 1 product in the comparison list. I need at least 2 products to start comparison. Please add more product's barcode.")
        else:
            data = {'barcode': product_comparison_list,
                    'product_name': None,
                    'kisusscore': None,
                    'nutri_score': None,
                    'nova_score': None,
                    'eco_score': None,
                    'input_quality': None,
                    'other_properties': None,
                    'product_img_url': None,
                    'kisusscore_json': None,
                    'openfood_json': None}
            product_comparison_df = pd.DataFrame(data)
            for barcode in product_comparison_list:
                if (barcode is not None):
                    openfood_response = requests.get(
                        'https://world.openfoodfacts.org/api/v2/product/'+barcode)
                    if (openfood_response.status_code == 200 and openfood_response.json().get('product') is not None):
                        product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                            'product_name']] = openfood_response.json()['product']['product_name']
                        if "nutriscore_grade" in openfood_response.json()['product']:
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'nutri_score']] = openfood_response.json()['product']['nutriscore_grade']
                        else:
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'nutri_score']] = "unknown"
                        if "nova_group" in openfood_response.json()['product']:
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'nova_score']] = openfood_response.json()['product']['nova_group']
                        else:
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'nova_score']] = "unknown"
                        if "ecoscore_grade" in openfood_response.json()['product']:
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'eco_score']] = openfood_response.json()['product']['ecoscore_grade']
                        else:
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'eco_score']] = "unknown"
                        product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                            'product_img_url']] = openfood_response.json()['product']['image_url']
                    else:
                        dispatcher.utter_message(
                            "Oops, I could not find this product with barcode {} 😞 Please recheck if you typed it correctly. Otherwise, it might not be available in our database.".format(barcode))
                        continue
                    susscore_response = requests.get(
                        'https://kisuscheck.org/middleware/productscore/'+barcode)
                    # print(susscore_response.text)
                    if susscore_response.status_code == 200 and "error" not in susscore_response.json():
                        if susscore_response.json().get('id') == int(barcode):
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'kisusscore']] = round(susscore_response.json()['KISusScore']['totalScore'], 1)
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'input_quality']] = susscore_response.json()['inputQuality']
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'other_properties']] = str(susscore_response.json()['other_properties'])
                            product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                                'kisusscore_json']] = susscore_response.text
                        else:
                            dispatcher.utter_message(
                                "Oops, I could not calculate the KISus-Score of this product ({}) 😞 If the barcode is correct, it might not be available in our database. Otherwise, there might be something wrong with our server, please try again.".format(barcode))
                    else:
                        dispatcher.utter_message(
                            "Oops, I could not calculate the KISus-Score of this product ({}) 😞 If the barcode is correct, it might not be available in our database. Otherwise, there might be something wrong with our server, please try again.".format(barcode))
            product_comparison_df.sort_values(
                by=['kisusscore'], ascending=False, na_position='last', inplace=True)
            product_comparison_df.reset_index(inplace=True)
            product_comparison_df.loc[product_comparison_df['kisusscore'].isnull(
            ), 'kisusscore'] = "unknown"
            # with pd.option_context('display.max_rows', None,
            #                        'display.max_columns', None
            #                        ):
            #     print(product_comparison_df)
            for index in range(len(product_comparison_list)):
                if (product_comparison_df.iloc[index]['product_name'] is not None):
                    if (product_comparison_df.iloc[index]['product_img_url'] is not None):
                        dispatcher.utter_message(
                            text=str(index+1)+". "+product_comparison_df.iloc[index]['product_name']+" ("+product_comparison_df.iloc[index]['barcode']+") \n" +
                            "   KISus-Score: " + str(product_comparison_df.iloc[index]['kisusscore'])+"\n" +
                            "   (Nutri-Score: " + str(product_comparison_df.iloc[index]['nutri_score']) +
                            ", Nova-Group: "+str(product_comparison_df.iloc[index]['nova_score']) +
                            ", Eco-Score: "+str(product_comparison_df.iloc[index]['eco_score'])+") \n" +
                            "   Other properties: " +
                            str(product_comparison_df.iloc[index]
                                ['other_properties']),
                            image=product_comparison_df.iloc[index]['product_img_url'])
                    else:
                        dispatcher.utter_message(
                            text=str(index+1)+". "+product_comparison_df.iloc[index]['product_name']+" ("+product_comparison_df.iloc[index]['barcode']+") \n" +
                            "   KISus-Score: " + str(product_comparison_df.iloc[index]['kisusscore'])+" \n" +
                            "   (Nutri-Score: " + str(product_comparison_df.iloc[index]['nutri_score']) +
                            ", Nova-Group: "+str(product_comparison_df.iloc[index]['nova_score']) +
                            ", Eco-Score: "+str(product_comparison_df.iloc[index]['eco_score'])+") \n" +
                            "   Other properties: "+str(product_comparison_df.iloc[index]['other_properties']) +
                            " \n   no image available")
                else:
                    dispatcher.utter_message(
                        text=str(index+1)+". product with barcode "+product_comparison_df.iloc[index]['barcode']+" doesn't found in our database.")
            if product_comparison_df is not None:
                product_comparison_df = product_comparison_df.to_json()
                # print(product_comparison_df)
        return [SlotSet("comparison_or_kisusscore_result", product_comparison_df)]


class ActionFillSecondProductForComparison(Action):
    def name(self) -> Text:
        return "action_fill_second_product_for_comparison"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        comparison_path_active = tracker.get_slot("comparison_path_active")
        if comparison_path_active == True:

            barcodes = tracker.get_slot("barcode_list")
            if barcodes != None:

                first_product_for_comparison = tracker.get_slot(
                    "first_product_for_comparison")
                second_product_for_comparison = tracker.get_slot(
                    "second_product_for_comparison")
                product_comparison_list = tracker.get_slot(
                    "product_comparison_list")

                for barcode in barcodes:
                    if product_comparison_list != None and first_product_for_comparison != None and second_product_for_comparison == None:
                        if first_product_for_comparison != barcode:
                            return [SlotSet("second_product_for_comparison", barcode)]
                        else:
                            dispatcher.utter_message(
                                text="This product ({}) is already in the comparison list.".format(barcode))
                    break
        return []


class ValidateProductComparisonForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_product_comparison_form"

    def validate_first_product_for_comparison(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        return {"first_product_for_comparison": slot_value}

    def validate_second_product_for_comparison(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        first_product_for_comparison = tracker.get_slot(
            "first_product_for_comparison")

        if first_product_for_comparison != slot_value:
            return {"second_product_for_comparison": slot_value}
        else:
            dispatcher.utter_message(
                text="This product ({}) is already in the comparison list.".format(slot_value))
        return {"second_product_for_comparison": None}


class ActionStopComparingAndClearCompareHistory(Action):
    def name(self) -> Text:
        return "action_stop_comparing_and_clear_compare_history"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        comparison_path_active = tracker.get_slot("comparison_path_active")
        if comparison_path_active == True:
            product_comparison_list = tracker.get_slot(
                "product_comparison_list")
            dispatcher.utter_message(text="The product comparison between {} is stopped, and this comparison history will be cleared.".format(
                ', '.join(product_comparison_list)))
            return [SlotSet("product_comparison_list", None), SlotSet("product_comparison_list_length", 0),
                    SlotSet("first_product_for_comparison", None), SlotSet(
                        "second_product_for_comparison", None),
                    SlotSet("comparison_or_kisusscore_result", None), SlotSet("comparison_path_active", False), SlotSet("barcode_list", None)]
        return []


class ActionSetComparisonPathActiveToTrue(Action):
    def name(self) -> Text:
        return "action_set_comparison_path_active_to_true"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent_of_latest_message = tracker.get_intent_of_latest_message()
        if intent_of_latest_message in ["ask_for_product_comparison", "compare_products_with_name", "compare_products_with_barcode_given"]:
            comparison_path_active = tracker.get_slot("comparison_path_active")
            if comparison_path_active == False:
                return [SlotSet("comparison_path_active", True),
                        SlotSet("product_comparison_list", None), SlotSet(
                            "product_comparison_list_length", 0),
                        SlotSet("first_product_for_comparison", None), SlotSet(
                            "second_product_for_comparison", None),
                        SlotSet("comparison_or_kisusscore_result", None)]
            else:
                # dispatcher.utter_message(
                #     text="The comparison path is already active. Please check if the previous comparison was stopped correctly.")
                return [SlotSet("comparison_path_active", True),
                        SlotSet("product_comparison_list", None), SlotSet(
                            "product_comparison_list_length", 0),
                        SlotSet("first_product_for_comparison", None), SlotSet(
                            "second_product_for_comparison", None),
                        SlotSet("comparison_or_kisusscore_result", None)]
        return []


class ActionSetComparisonPathActiveToFalse(Action):
    def name(self) -> Text:
        return "action_set_comparison_path_active_to_false"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("comparison_path_active", False),
                SlotSet("product_comparison_list", None), SlotSet(
            "product_comparison_list_length", 0),
            SlotSet("first_product_for_comparison", None), SlotSet(
            "second_product_for_comparison", None), SlotSet("barcode_list", None)]


# Refer: https://github.com/UKPLab/sentence-transformers/blob/master/docs/pretrained-models/nli-models.md
# pretrained_model = 'bert-base-nli-mean-tokens'
pretrained_model = 'all-mpnet-base-v2'
score_threshold = 0.80  # This confidence scores can be adjusted based on your need!!


class ActionGetFAQAnswer(Action):

    def __init__(self):
        print("ActionGetFAQAnswer init")
        super(ActionGetFAQAnswer, self).__init__()
        self.bc = SentenceTransformer(pretrained_model)
        self.faq_data = json.load(
            open("./data/faq.json", "rt", encoding="utf-8"))
        self.faq_questions = [each['q'] for each in self.faq_data]
        self.standard_questions_encoder = np.load(
            "./data/standard_questions-all-mpnet-base-v2.npy")

        # self.standard_questions_encoder = np.load(
        #     "./data/standard_questions.npy")
        # self.standard_questions_encoder_len = np.load(
        #     "./data/standard_questions_len.npy")
        # print(self.standard_questions_encoder.shape)

    def get_most_similar_standard_question_id(self, query_question):
        # query_vector = torch.tensor(
        #     self.bc.encode([query_question])[0]).numpy()
        query_vector = self.bc.encode([query_question])[0]
        print("Question received at action engineer")
        # score = np.sum((self.standard_questions_encoder * query_vector), axis=1) / (
        #     self.standard_questions_encoder_len * (np.sum(query_vector * query_vector) ** 0.5))
        score = util.cos_sim(
            query_vector, self.standard_questions_encoder).tolist()[0]
        score = [(x + 1) / 2 for x in score]
        print(score)
        print(len(score))
        top_id = np.argsort(score)[::-1][0]
        return top_id, score[top_id]

    def name(self) -> Text:
        return "action_faq_get_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        query = tracker.latest_message['text']
        most_similar_id, score = self.get_most_similar_standard_question_id(
            query)
        print("The question is matched with id:{} with score: {}".format(
            most_similar_id, score))
        # This confidence scores can be adjusted based on your need!!
        if float(score) > score_threshold:
            response = self.faq_data[most_similar_id]['a']
            dispatcher.utter_message(response)
            if (self.faq_data[most_similar_id].get('img') is not None):
                imgs = self.faq_data[most_similar_id]['img']
                if (len(imgs) > 0):
                    for i in imgs:
                        print(i)
                        dispatcher.utter_message(image=i)
            if (self.faq_data[most_similar_id].get('sources') is not None):
                resources = self.faq_data[most_similar_id]['sources']
                if (len(resources) > 0):
                    dispatcher.utter_message(
                        "You can find more information about this topic here: ")
                    for i in resources:
                        dispatcher.utter_message(i)
                else:
                    dispatcher.utter_message(resources)
        else:
            response = "Sorry, this question is beyond my ability..."
            print(response)
            dispatcher.utter_message(response)
            dispatcher.utter_message(
                "You can check these links for more information: ")
            dispatcher.utter_message("https://gesund.bund.de/")
            dispatcher.utter_message("https://www.bmel.de/")
        return []


def encode_standard_question(pretrained_model):
    """
    This will encode all the questions available in question database into sentence embedding. The result will be stored into numpy array for comparision purpose.
    """
    bc = SentenceTransformer(pretrained_model)
    data = json.load(open("./data/faq.json", "rt", encoding="utf-8"))
    standard_questions = [each['q'] for each in data]
    print("Standard question size", len(standard_questions))
    print("Start to calculate encoder....")
    standard_questions_encoder = bc.encode(standard_questions)
    np.save("./data/standard_questions-all-mpnet-base-v2",
            standard_questions_encoder)
    # standard_questions_encoder = torch.tensor(
    #     bc.encode(standard_questions)).numpy()
    # np.save("./data/standard_questions", standard_questions_encoder)
    # standard_questions_encoder_len = np.sqrt(
    #     np.sum(standard_questions_encoder * standard_questions_encoder, axis=1))
    # np.save("./data/standard_questions_len", standard_questions_encoder_len)

# encode_standard_question(pretrained_model)
# x = ActionGetFAQAnswer()
# x.run()


class getProductInfoByBarcode(Action):
    def name(self) -> Text:
        return "action_get_product_info_by_barcode"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract the barcode from the user input
        barcode = None
        entities = tracker.latest_message["entities"]
        openaiContent = ""
        # print(entities)

        for entity in entities:
            if entity["entity"] == "barcode":
                barcode = entity["value"]
                break

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if (barcode is not None):
            SlotSet("barcode", barcode)
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            resProduct = response.json()['product']
            if (response.status_code == 200 and response.json().get('product') is not None):
                if (resProduct.get("image_url") is not None):
                    dispatcher.utter_message(image=resProduct['image_url'])
                if (resProduct.get("product_name_en") is not None):
                    openaiContent += "Product Name is " + \
                        resProduct['product_name_en'] + "\n"
                    # dispatcher.utter_message(
                    #     text="Product Name is " + resProduct['product_name_en'])
                if (resProduct.get("labels") is not None):
                    openaiContent += "Product Labels: " + \
                        resProduct['labels'] + "\n"
                    # dispatcher.utter_message(
                    #     text="Product Labels: " + resProduct['labels'])
                if (resProduct.get("nutriscore_data") is not None and resProduct['nutriscore_data'].get("score") is not None):
                    openaiContent += "Nutrition score = " + \
                        resProduct['nutriscore_data']['score'].__str__() + "\n"
                    # dispatcher.utter_message(
                    #     text="Nutrition score = " + resProduct['nutriscore_data']['score'].__str__())
                if (resProduct.get("nutriscore_grade") is not None):
                    openaiContent += "Nutrition grade = " + \
                        resProduct['nutriscore_grade'] + "\n"
                    # dispatcher.utter_message(
                    #     text="Nutrition grade = " + resProduct['nutriscore_grade'])
                messages = [{"role": "system", "content": "summarize the following information in a nice way"},
                            {"role": "user", "content": openaiContent}]
                x = openaiChatCompletion(messages)
                dispatcher.utter_message(text=x['content'])

                # set animal friendliness slots
                if(resProduct.get("ingredients_analysis_tags") is not None):
                    vegan=0.5
                    vegetarian=0.5
                    palm_oil=0.5
                    for ing in resProduct.get('ingredients_analysis_tags'):
                        if("vegan" in ing.lower()):
                            if(ing == "en:vegan"):
                                vegan = 1
                            elif(ing == "en:non-vegan"):
                                vegan = 0
                                
                        if("vegetarian" in ing.lower()):
                            if(ing == "en:vegetarian"):
                                vegetarian = 1
                            elif(ing == "en:non-vegetarian"):
                                vegetarian = 0
                        if("palm" in ing.lower()):
                            if(ing == "en:palm-oil-free"):
                                palm_oil = 0
                            elif(ing == "en:palm-oil"):
                                palm_oil = 1
                    return [
                            SlotSet("product_vegan", str(vegan)),
                            SlotSet("product_vegetarian", str(vegetarian)),
                            SlotSet("product_palm_oil", str(palm_oil))]
                return [
                            SlotSet("product_vegan", None),
                            SlotSet("product_vegetarian", None),
                            SlotSet("product_palm_oil", None)]

            dispatcher.utter_message(text="Sorry, I can't find the product.")
        dispatcher.utter_message(
            text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []


class getProductInfoByName(Action):
    def name(self) -> Text:
        return "action_get_top_product_info_by_name"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        productName = None
        gotProducts = False
        entities = tracker.latest_message["entities"]
        # print(entities)

        for entity in entities:
            if entity["entity"] == "food":
                productName = entity["value"]
                break
        if (productName is None and tracker.get_slot("last_searched_product_name") is not None):
            productName = tracker.get_slot("last_searched_product_name")

        # API endpoint
        if (productName is not None):
            ingredient_preference = ""
            allergen_preference = ""
            if (tracker.get_slot("ingredient_preference") is not None):
                ingredient_preference = "&labels_tags=" + \
                    ','.join(tracker.get_slot("ingredient_preference"))
            if (tracker.get_slot("allergen_preference") is not None):
                allergen_preference = "&allergens_tags=" + \
                    ','.join(tracker.get_slot("allergen_preference"))
            url = "https://world.openfoodfacts.org/api/v2/search?categories_tags="+productName + \
                ingredient_preference + allergen_preference + "&sort_by=popularity_key"
            print(url)
            # Send GET request
            response = requests.get(url)

            product_cat_limit = tracker.get_slot("product_cat_limit")
            if (product_cat_limit is None):
                product_cat_limit = {productName: 0}
            elif (product_cat_limit.get(productName) is None):
                product_cat_limit[productName] = 0
            curr_product_cat_limit = product_cat_limit[productName]

            # Check if the request was successful
            if response.status_code == 200:
                # print("Success")
                data = response.json()

                products = data["products"]

                if (len(products) > 0 and curr_product_cat_limit < len(products)):
                    for i in range(curr_product_cat_limit, curr_product_cat_limit+3):
                        # openaiContent = ""
                        # i, product in enumerate(products):
                        if (i < len(products)):
                            product = products[i]
                        if (product.get("code") is not None):
                            # openaiContent+= str(i+1) + "- Barcode is " + product['code'] + "\n"
                            dispatcher.utter_message(
                                text=str(i+1) + "- Barcode is " + product['code'])
                        if (product.get("image_url") is not None):
                            dispatcher.utter_message(
                                image=product['image_url'])
                        if (product.get("product_name") is not None):
                            # openaiContent+= "Product Name is " + product['product_name'] + "\n"
                            dispatcher.utter_message(
                                text="Product Name is " + product['product_name'])
                        if (product.get("labels") is not None):
                            # openaiContent+= "Product Labels: " + product['labels'] + "\n"
                            dispatcher.utter_message(
                                text="Product Labels: " + product['labels'])
                        if (product.get("nutriscore_data") is not None and product['nutriscore_data'].get("score") is not None):
                            # openaiContent+= "Nutrition score = " + product['nutriscore_data']['score'].__str__() + "\n"
                            dispatcher.utter_message(
                                text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                        if (product.get("nutriscore_grade") is not None):
                            # openaiContent+= "Nutrition grade = " + product['nutriscore_grade'] + "\n"
                            dispatcher.utter_message(
                                text="Nutrition grade = " + product['nutriscore_grade'])
                        # messages = [{"role": "system", "content": "summarize the following information in a nice way"},
                        # {"role": "user", "content": openaiContent}]
                        # x= openaiChatCompletion(messages)
                        # print(x)
                        # dispatcher.utter_message(x['content'])
                    gotProducts = True

                    curr_product_cat_limit += 3
                    product_cat_limit[productName] = curr_product_cat_limit

                    return [SlotSet("product_cat_limit", product_cat_limit), SlotSet("last_searched_product_name", productName)]

            if (gotProducts == False):
                url = "https://world.openfoodfacts.org/api/v2/search?brands_tags=" + \
                    productName + ingredient_preference + "&sort_by=popularity_key"

                # Send GET request
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code == 200:

                    data = response.json()

                    products = data["products"]

                    if (len(products) > 0 and curr_product_cat_limit < len(products)):
                        for i in range(curr_product_cat_limit, curr_product_cat_limit+3):
                            # openaiContent = ""
                            # i, product in enumerate(products):
                            if (i < len(products)):
                                product = products[i]
                            if (product.get("code") is not None):
                                # openaiContent+= str(i+1) + "- Barcode is " + product['code'] + "\n"
                                dispatcher.utter_message(
                                    text=str(i+1) + "- Barcode is " + product['code'])
                            if (product.get("image_url") is not None):
                                dispatcher.utter_message(
                                    image=product['image_url'])
                            if (product.get("product_name") is not None):
                                # openaiContent+= "Product Name is " + product['product_name'] + "\n"
                                dispatcher.utter_message(
                                    text="Product Name is " + product['product_name'])
                            if (product.get("labels") is not None):
                                # openaiContent+= "Product Labels: " + product['labels'] + "\n"
                                dispatcher.utter_message(
                                    text="Product Labels: " + product['labels'])
                            if (product.get("nutriscore_data") is not None and product['nutriscore_data'].get("score") is not None):
                                # openaiContent+= "Nutrition score = " + product['nutriscore_data']['score'].__str__() + "\n"
                                dispatcher.utter_message(
                                    text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                            if (product.get("nutriscore_grade") is not None):
                                # openaiContent+= "Nutrition grade = " + product['nutriscore_grade'] + "\n"
                                dispatcher.utter_message(
                                    text="Nutrition grade = " + product['nutriscore_grade'])
                            # messages = [{"role": "system", "content": "summarize the following information in a nice way"},
                            # {"role": "user", "content": openaiContent}]
                            # x= openaiChatCompletion(messages)
                            # print(x)
                            # dispatcher.utter_message(x['content'])

                        curr_product_cat_limit += 3
                        product_cat_limit[productName] = curr_product_cat_limit
                        return [SlotSet("product_cat_limit", product_cat_limit), SlotSet("last_searched_product_name", productName)]

        dispatcher.utter_message(text="Sorry, I could not find that product!")
        return []


class answerAboutProductPropertyByBarcode(Action):
    def name(self) -> Text:
        return "action_answer_about_product_property_by_barcode"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        barcode = None
        property = None
        entities = tracker.latest_message["entities"]
        print(entities)

        for entity in entities:
            if entity["entity"] == "barcode":
                barcode = entity["value"]
            elif entity["entity"] == "food_property":
                property = entity["value"]
                propertyFirst = property.split(' ')[0]

        # API endpoint
        if (barcode is not None and propertyFirst is not None):
            # "https://world.openfoodfacts.org/api/v2/search?labels_tags="+property+"&sort_by=popularity_key"
            url = 'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json'

            # Send GET request
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:

                product = response.json()['product']
                product_name = ""

                if (product.get("_id") is not None and product["_id"] == barcode):
                    if (product.get("product_name") is not None):
                        product_name = product['product_name']

                    if (product.get("labels") is not None):
                        labels = product['labels'].split(',')
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        if (propertyFirst.lower() in stripped_labels):
                            dispatcher.utter_message(
                                text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                            return []

                    if (product.get("labels_old") is not None):
                        labels = product['labels_old'].split(',')
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        if (propertyFirst.lower() in stripped_labels):
                            dispatcher.utter_message(
                                text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                            return []

                    if (product.get("ingredients_analysis_tags") is not None):
                        labels = product['ingredients_analysis_tags']
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        for label in stripped_labels:
                            if (propertyFirst.lower() in label and ('no' not in label and 'free' not in label)):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                return []
                            elif (propertyFirst.lower() in label and ('no' in label or 'free' in label)):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has non-" + property + " ingredients")
                                return []
                    if (product.get("ingredients_tags") is not None):
                        labels = product['ingredients_tags']
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        for label in stripped_labels:
                            if (propertyFirst.lower() in label and ('no' not in label and 'free' not in label)):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                return []
                            elif (propertyFirst.lower() in label and ('no' in label or 'free' in label)):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has non-" + property + " ingredients")
                                return []

                    if (product.get("traces_hierarchy") is not None):
                        labels = product['traces_hierarchy']
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        for label in stripped_labels:
                            if (propertyFirst.lower() in label and ('no' not in label and 'free' not in label)):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                return []
                            elif (propertyFirst.lower() in label and ('no' in label or 'free' in label)):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has non" + property + " ingredients")
                                return []

                        dispatcher.utter_message(text="Sorry, I don't know if " + product_name +
                                                 " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                        return []

        dispatcher.utter_message(text="Sorry, I did not get that property!")
        return []


class ActionScanReport(Action):
    def name(self) -> Text:
        return "action_scan_report"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("The tracker object is: ", tracker.latest_message)
        query = tracker.latest_message['text']

        print('The API key is:', os.environ.get('OPENAI_API_KEY'))

        csv_embeddings_file = 'gpt_integration/embeddings.csv'
        K_DOCS = 5

        queryEngine = QueryEngine()
        # search and return the 5 most similar documents
        res = queryEngine.search_chunks(
            csv_embeddings_file=csv_embeddings_file, query=query, k=K_DOCS, pprint=False)
        # query
        gpt_response = queryEngine.query(res, query, 2, 20)
        text = gpt_response.content

        dispatcher.utter_message(text=text)

        return []


class ActionCalculateKisusscoreByBarcode(Action):
    def name(self) -> Text:
        return "action_calculate_kisusscore_by_barcode"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        kisusscore_df = None
        barcode = tracker.get_slot("barcode")
        if (barcode == None):
            dispatcher.utter_message(
                "Please specify the barcode of the product to calculate its KISus-Score.")
        else:
            data = {'barcode': barcode,
                    'product_name': None,
                    'kisusscore': None,
                    'nutri_score': None,
                    'nova_score': None,
                    'eco_score': None,
                    'input_quality': None,
                    'other_properties': None,
                    'product_img_url': None,
                    'kisusscore_json': None}
            kisusscore_df = pd.DataFrame(data, index=[0])
            openfood_response = requests.get(
                'https://world.openfoodfacts.org/api/v2/product/'+barcode)
            if (openfood_response.status_code == 200 and openfood_response.json().get('product') is not None):
                kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                    'product_name']] = openfood_response.json()['product']['product_name']
                if "nutriscore_grade" in openfood_response.json()['product']:
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'nutri_score']] = openfood_response.json()['product']['nutriscore_grade']
                else:
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'nutri_score']] = "unknown"
                if "nova_group" in openfood_response.json()['product']:
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'nova_score']] = openfood_response.json()['product']['nova_group']
                else:
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'nova_score']] = "unknown"
                if "ecoscore_grade" in openfood_response.json()['product']:
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'eco_score']] = openfood_response.json()['product']['ecoscore_grade']
                else:
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'eco_score']] = "unknown"
                kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                    'product_img_url']] = openfood_response.json()['product']['image_url']
            else:
                dispatcher.utter_message(
                    "Oops, I could not find this product with barcode {} 😞 Please recheck if you typed it correctly. Otherwise, it might not be available in our database.".format(barcode))
            susscore_response = requests.get(
                'https://kisuscheck.org/middleware/productscore/'+barcode)
            if susscore_response.status_code == 200 and "error" not in susscore_response.json():
                if susscore_response.json().get('id') == int(barcode):
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'kisusscore']] = round(susscore_response.json()['KISusScore']['totalScore'], 1)
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'input_quality']] = susscore_response.json()['inputQuality']
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'other_properties']] = str(susscore_response.json()['other_properties'])
                    kisusscore_df.loc[kisusscore_df['barcode'] == barcode, [
                        'kisusscore_json']] = susscore_response.text
                else:
                    dispatcher.utter_message(
                        "Oops, I could not calculate the KISus-Score of this product ({}) 😞 If the barcode is correct, it might not be available in our database. Otherwise, there might be something wrong with our server, please try again.".format(barcode))
            else:
                dispatcher.utter_message(
                    "Oops, I could not calculate the KISus-Score of this product ({}) 😞 If the barcode is correct, it might not be available in our database. Otherwise, there might be something wrong with our server, please try again.".format(barcode))
            kisusscore_df.loc[kisusscore_df['kisusscore'].isnull(
            ), 'kisusscore'] = "unknown"
            if (kisusscore_df.iloc[0]['product_name'] is not None):
                if (kisusscore_df.iloc[0]['product_img_url'] is not None):
                    dispatcher.utter_message(
                        text=kisusscore_df.iloc[0]['product_name']+" ("+kisusscore_df.iloc[0]['barcode']+") \n" +
                        "   KISus-Score: " + str(kisusscore_df.iloc[0]['kisusscore'])+"\n" +
                        "   (Nutri-Score: " + str(kisusscore_df.iloc[0]['nutri_score']) +
                        ", Nova-Group: "+str(kisusscore_df.iloc[0]['nova_score']) +
                        ", Eco-Score: "+str(kisusscore_df.iloc[0]['eco_score'])+") \n" +
                        "   Other properties: " +
                        str(kisusscore_df.iloc[0]
                            ['other_properties']),
                        image=kisusscore_df.iloc[0]['product_img_url'])
                else:
                    dispatcher.utter_message(
                        text=kisusscore_df.iloc[0]['product_name']+" ("+kisusscore_df.iloc[0]['barcode']+") \n" +
                        "   KISus-Score: " + str(kisusscore_df.iloc[0]['kisusscore'])+" \n" +
                        "   (Nutri-Score: " + str(kisusscore_df.iloc[0]['nutri_score']) +
                        ", Nova-Group: "+str(kisusscore_df.iloc[0]['nova_score']) +
                        ", Eco-Score: "+str(kisusscore_df.iloc[0]['eco_score'])+") \n" +
                        "   Other properties: "+str(kisusscore_df.iloc[0]['other_properties']) +
                        " \n   no image available")
            if kisusscore_df is not None:
                kisusscore_df = kisusscore_df.to_json()
                # print(kisusscore_df)
        return [SlotSet("comparison_or_kisusscore_result", kisusscore_df)]


class ActionExplainKisusscoreOrComparisonResult(Action):
    def name(self) -> Text:
        return "action_explain_kisusscore_or_comparison_result"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        comparison_or_kisusscore_result = tracker.get_slot(
            "comparison_or_kisusscore_result")
        # print(type(comparison_or_kisusscore_result)) # str
        comparison_or_kisusscore_result = json.loads(
            comparison_or_kisusscore_result)
        del comparison_or_kisusscore_result["product_img_url"]
        # print(comparison_or_kisusscore_result)

        knowledge_base_type = "empty"
        if len(comparison_or_kisusscore_result['barcode']) == 1:
            knowledge_base_type = "single product"
        elif len(comparison_or_kisusscore_result['barcode']) > 1:
            knowledge_base_type = "comparison result"

        user_preferences = {}
        user_preferences["ingredient_preference"] = tracker.get_slot(
            "ingredient_preference")
        user_preferences["allergen_preference"] = tracker.get_slot(
            "allergen_preference")
        user_preferences["nutr_value_preference"] = tracker.get_slot(
            "nutr_value_preference")
        user_preferences["food_processing_preference"] = tracker.get_slot(
            "food_processing_preference")
        user_preferences["label_preference"] = tracker.get_slot(
            "label_preference")
        user_preferences["env_preference"] = tracker.get_slot("env_preference")
        # print(user_preferences)

        explanator = Explanator(comparison_or_kisusscore_result=comparison_or_kisusscore_result,
                                knowledge_base_type=knowledge_base_type, user_preferences=user_preferences)
        user_question = tracker.latest_message['text']

        dispatcher.utter_message(
            text=explanator.get_answer(user_question=user_question))

        return []
