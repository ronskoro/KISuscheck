# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from functools import reduce
from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

# set slot sample action
# class SetSlotFromUserInput(Action):
#     def name(self) -> Text:
#         return "action_set_slot_from_user_input"

#     async def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         # Extract the value from the user input
#         user_input = list(tracker.latest_message.get('text').split())[-1]
#         # slot_value = user_input # Replace this with your own logic to extract the slot value
        
#         # Set the slot value
#         return [SlotSet("user_name", user_input)]

class getProductInfoByBarcode(Action):
    def name(self) -> Text:
        return "action_get_product_info_by_barcode"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract the barcode from the user input
        barcode = None
        entities = tracker.latest_message["entities"]
        print(entities)
        for entity in entities:
            if entity["entity"] == "barcode":
                barcode = entity["value"]
                break

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if(barcode is not None):
            response = requests.get('https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            if(response.status_code == 200 and response.json().get('product') is not None):
                if(response.json()['product'].get("image_url") is not None):
                    dispatcher.utter_message(image=response.json()['product']['image_url'])
                if(response.json()['product'].get("generic_name") is not None):
                    dispatcher.utter_message(text="Product Name is " + response.json()['product']['generic_name'])
                if(response.json()['product'].get("labels") is not None):
                    dispatcher.utter_message(text= "Product Labels: " + response.json()['product']['labels'])
                if(response.json()['product'].get("nutriscore_data") is not None and response.json()['product']['nutriscore_data'].get("score") is not None):
                    dispatcher.utter_message(text="Nutrition score = " + response.json()['product']['nutriscore_data']['score'].__str__())
                if(response.json()['product'].get("nutriscore_grade") is not None):
                    dispatcher.utter_message(text="Nutrition grade = " + response.json()['product']['nutriscore_grade'])
                return []
            
            dispatcher.utter_message(text="Sorry, I can't find the product.")
        dispatcher.utter_message(text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []
    
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

        vegan=0.5
        vegetarian=0.5
        palm_oil=0.5

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if(barcode is not None):
            response = requests.get('https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            if(response.status_code == 200 and response.json().get('product') is not None):
                if(response.json()['product'].get("ingredients_analysis_tags") is not None):
                    for ing in response.json()['product'].get('ingredients_analysis_tags'):
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
                    msg = "The product "
                    if(vegan == 1):
                        msg += "is vegan."
                    elif(vegetarian == 1):
                        msg += "is vegetarian."
                    elif(vegetarian == 0):
                        msg += "is non-vegetarian."
                    else:
                        msg += "may be vegan/vegetarian."
                    if(vegan != 0 or vegetarian != 0):
                        if(palm_oil != 0):
                            msg += " However, "
                        else:
                            msg += " And, "
                    else:
                        if(palm_oil != 0):
                            msg += " And, "
                        else:
                            msg += " But, "
                    if(palm_oil != 0):
                        if(palm_oil == 0):
                            msg += "it contains "
                        else:
                            msg += "it may contain "
                        msg += "palm oil which drives deforestation that contributes to climate change, and endangers species such as the orangutan, the pigmy elephant and the Sumatran rhino."
                    else:
                        msg += "it is palm oil free!"
                    dispatcher.utter_message(text=msg)
                    return []
                dispatcher.utter_message(text="I don't have information about this product's ingredients, sorry :/")
                return []
            dispatcher.utter_message(text="Sorry, I can't find the product.")
            return []
        dispatcher.utter_message(text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []



class getProductInfoByName(Action):
    def name(self) -> Text:
        return "action_get_top_product_info_by_name"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        

        productName = None
        entities = tracker.latest_message["entities"]
        print(entities)
        for entity in entities:
            if entity["entity"] == "food":
                productName = entity["value"]
                break

        # API endpoint
        if(productName is not None):
            url = "https://world.openfoodfacts.org/api/v2/search?categories_tags="+productName+"&sort_by=popularity_key"

            # Send GET request
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                
                data = response.json()

                products = data["products"]
                for i, product in enumerate(products):
                    if i == 3:
                        break
                    if(product.get("code") is not None):
                        dispatcher.utter_message(text=str(i+1) +"- Barcode is " + product['code'])
                    if(product.get("image_url") is not None):
                        dispatcher.utter_message(image=product['image_url'])
                    if(product.get("product_name") is not None):
                        dispatcher.utter_message(text="Product Name is " + product['product_name'])
                    if(product.get("labels") is not None):
                        dispatcher.utter_message(text= "Product Labels: " + product['labels'])
                    if(product.get("nutriscore_data") is not None and product['nutriscore_data'].get("score") is not None):
                        dispatcher.utter_message(text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                    if(product.get("nutriscore_grade") is not None):
                        dispatcher.utter_message(text="Nutrition grade = " + product['nutriscore_grade'])
                return []
            
            else:
                url = "https://world.openfoodfacts.org/api/v2/search?brand_tags="+productName+"&sort_by=popularity_key"

                # Send GET request
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code == 200:
                    
                    data = response.json()

                    products = data["products"]
                    
                    for i, product in enumerate(products):
                        if i == 3:
                            break
                        if(product.get("code") is not None):
                            dispatcher.utter_message(text=str(i+1) +"- Barcode is " + product['code'])
                        if(product.get("image_url") is not None):
                            dispatcher.utter_message(image=product['image_url'])
                        if(product.get("product_name") is not None):
                            dispatcher.utter_message(text="Product Name is " + product['product_name'])
                        if(product.get("labels") is not None):
                            dispatcher.utter_message(text= "Product Labels: " + product['labels'])
                        if(product.get("nutriscore_data") is not None):
                            dispatcher.utter_message(text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                        if(product.get("nutriscore_grade") is not None):
                            dispatcher.utter_message(text="Nutrition grade = " + product['nutriscore_grade'])
                    return []
        dispatcher.utter_message(text="Sorry, I did not get that!")   
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

        # API endpoint
        if(barcode is not None and property is not None):
            # "https://world.openfoodfacts.org/api/v2/search?labels_tags="+property+"&sort_by=popularity_key"
            url = 'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json'

            # Send GET request
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                
                product = response.json()['product']
                generic_name = ""
                

                # data = response.json()

                # products = data["products"]
                # for product in products:

                    # print("xxxxxxxxxxx",product["code"])

                if(product.get("_id") is not None and product["_id"] == barcode):
                    if(product.get("generic_name") is not None):
                        generic_name = product['generic_name']

                    if(product.get("labels") is not None):
                        labels = product['labels'].split(',')
                        stripped_labels = [word.strip().lower() for word in labels]

                        if(property.lower() in stripped_labels):
                            dispatcher.utter_message(text= generic_name + " ( barcode: " + barcode + " )" +  " has " + property + " ingredients")
                        else:
                            if(product.get("labels_old") is not None):
                                labels = product['labels_old'].split(',')
                                stripped_labels = [word.strip().lower() for word in labels]

                                if(property.lower() in stripped_labels):
                                    dispatcher.utter_message(text= generic_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                else:
                                    if(product.get("ingredients_analysis_tags") is not None):
                                        labels = product['ingredients_analysis_tags']
                                        stripped_labels = [word.strip().lower() for word in labels]

                                        for label in stripped_labels:
                                            if(property.lower() in label and 'no' not in label):
                                                dispatcher.utter_message(text= generic_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients") 
                                                return []                                            
                                        
                                        dispatcher.utter_message(text= generic_name + " ( barcode: " + barcode + " )" +  " has no " + property + " ingredients")
                        return []
                    # print("yyyyyyyyyy",product)
                #     dispatcher.utter_message(text=str(i+1) +"- Barcode is " + product['code'])
                # if(product.get("image_url") is not None):
                #     dispatcher.utter_message(image=product['image_url'])
                # if(product.get("product_name") is not None):
                #     dispatcher.utter_message(text="Product Name is " + product['product_name'])
                # if(product.get("labels") is not None):
                #     dispatcher.utter_message(text= "Product Labels: " + product['labels'])
                # if(product.get("nutriscore_data") is not None):
                #     dispatcher.utter_message(text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                # if(product.get("nutriscore_grade") is not None):
                #     dispatcher.utter_message(text="Nutrition grade = " + product['nutriscore_grade'])
            # dispatcher.utter_message(text="No, the product of barcode: " + barcode +  " is not " + property)
            # return []
        
        dispatcher.utter_message(text="Sorry, I did not get that property!")   
        return []
