# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from sentence_transformers import SentenceTransformer
from gpt_integration.processor import QueryEngine
import torch
import os
import json
from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

import numpy as np
import pandas as pd
import sys
# sys.path.append('C:/Users/maria/anaconda3/envs/rasa-faq/Lib/site-packages/torch/torch._C')
sys.path.append(
    'C:/ProgramData/Anaconda3/envs/seba-nlp/seba-nlp/Lib/site-packages')

# sentence embedding selection
sentence_transformer_select = True
# Refer: https://github.com/UKPLab/sentence-transformers/blob/master/docs/pretrained-models/nli-models.md
pretrained_model = 'bert-base-nli-mean-tokens'
score_threshold = 0.70  # This confidence scores can be adjusted based on your need!!

# Custom Action


class ActionGetFAQAnswer(Action):

    def __init__(self):
        print("ActionGetFAQAnswer init")
        super(ActionGetFAQAnswer, self).__init__()
        self.faq_data = json.load(
            open("./data/faq.json", "rt", encoding="utf-8"))
        self.sentence_embedding_choose(
            sentence_transformer_select, pretrained_model)
        self.standard_questions_encoder = np.load(
            "./data/standard_questions.npy")
        self.standard_questions_encoder_len = np.load(
            "./data/standard_questions_len.npy")
        print(self.standard_questions_encoder.shape)

    def sentence_embedding_choose(self, sentence_transformer_select=True, pretrained_model='bert-base-nli-mean-tokens'):
        self.sentence_transformer_select = sentence_transformer_select
        if sentence_transformer_select:
            self.bc = SentenceTransformer(pretrained_model)

    def get_most_similar_standard_question_id(self, query_question):
        if self.sentence_transformer_select:
            query_vector = torch.tensor(
                self.bc.encode([query_question])[0]).numpy()
        else:
            query_vector = self.bc.encode([query_question])[0]
        print("Question received at action engineer")
        score = np.sum((self.standard_questions_encoder * query_vector), axis=1) / (
            self.standard_questions_encoder_len * (np.sum(query_vector * query_vector) ** 0.5))
        top_id = np.argsort(score)[::-1][0]
        return top_id, score[top_id]

    def name(self) -> Text:
        return "action_faq_get_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        query = tracker.latest_message['text']
        # print(query)
        most_similar_id, score = self.get_most_similar_standard_question_id(
            query)
        print("The question is matched with id:{} with score: {}".format(
            most_similar_id, score))
        # This confidence scores can be adjusted based on your need!!
        if float(score) > score_threshold:
            response = self.faq_data[most_similar_id]['a']
            dispatcher.utter_message(response)
            if(self.faq_data[most_similar_id].get('img') is not None):
                imgs = self.faq_data[most_similar_id]['img']
                if(len(imgs) > 0):
                    for i in imgs:
                        print(i)
                        dispatcher.utter_message(image=i)
            if(self.faq_data[most_similar_id].get('sources') is not None):
                resources = self.faq_data[most_similar_id]['sources']
                if(len(resources) > 0):
                    dispatcher.utter_message(
                        "You can find more information about this topic here: ")
                    for i in resources:
                        dispatcher.utter_message(i)
                else:
                    dispatcher.utter_message(resources)

            # dispatcher.utter_message("Problem solved?")
        else:
            response = "Sorry, this question is beyond my ability..."
            print(response)
            dispatcher.utter_message(response)
            dispatcher.utter_message(
                "Sorry, I can't answer your question. You can dial the manual service...")
        return []


def encode_standard_question(sentence_transformer_select=True, pretrained_model='bert-base-nli-mean-tokens'):
    """
    This will encode all the questions available in question database into sentence embedding. The result will be stored into numpy array for comparision purpose.
    """
    if sentence_transformer_select:
        bc = SentenceTransformer(pretrained_model)
    # else:
    #     bc = BertClient(check_version=False)
    data = json.load(open("./data/faq.json", "rt", encoding="utf-8"))
    standard_questions = [each['q'] for each in data]
    print("Standard question size", len(standard_questions))
    print("Start to calculate encoder....")
    if sentence_transformer_select:
        standard_questions_encoder = torch.tensor(
            bc.encode(standard_questions)).numpy()
    # else:
    #     standard_questions_encoder = bc.encode(standard_questions)
    np.save("./data/standard_questions", standard_questions_encoder)
    standard_questions_encoder_len = np.sqrt(
        np.sum(standard_questions_encoder * standard_questions_encoder, axis=1))
    np.save("./data/standard_questions_len", standard_questions_encoder_len)

# encode_standard_question(sentence_transformer_select,pretrained_model)
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
        print(entities)

        for entity in entities:
            if entity["entity"] == "barcode":
                barcode = entity["value"]
                break

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if(barcode is not None):
            SlotSet("barcode", barcode)
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
            resProduct = response.json()['product']
            if(response.status_code == 200 and response.json().get('product') is not None):
                if(resProduct.get("image_url") is not None):
                    dispatcher.utter_message(image=resProduct['image_url'])
                if(resProduct.get("product_name_en") is not None):
                    dispatcher.utter_message(
                        text="Product Name is " + resProduct['product_name_en'])
                if(resProduct.get("labels") is not None):
                    dispatcher.utter_message(
                        text="Product Labels: " + resProduct['labels'])
                if(resProduct.get("nutriscore_data") is not None and resProduct['nutriscore_data'].get("score") is not None):
                    dispatcher.utter_message(
                        text="Nutrition score = " + resProduct['nutriscore_data']['score'].__str__())
                if(resProduct.get("nutriscore_grade") is not None):
                    dispatcher.utter_message(
                        text="Nutrition grade = " + resProduct['nutriscore_grade'])
                return []

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
        print(entities)

        for entity in entities:
            if entity["entity"] == "food":
                productName = entity["value"]
                break
        if(productName is None and tracker.get_slot("last_searched_product_name") is not None):
            productName = tracker.get_slot("last_searched_product_name")

        # API endpoint
        if(productName is not None):
            ingredient_preference = ""
            allergen_preference = ""
            if(tracker.get_slot("ingredient_preference") is not None):
                ingredient_preference = "&labels_tags=" + \
                    ','.join(tracker.get_slot("ingredient_preference"))
            if(tracker.get_slot("allergen_preference") is not None):
                allergen_preference = "&allergens_tags=" + \
                    ','.join(tracker.get_slot("allergen_preference"))
            url = "https://world.openfoodfacts.org/api/v2/search?categories_tags="+productName + \
                ingredient_preference + allergen_preference + "&sort_by=popularity_key"
            print(url)
            # Send GET request
            response = requests.get(url)

            product_cat_limit = tracker.get_slot("product_cat_limit")
            if(product_cat_limit is None):
                product_cat_limit = {productName: 0}
            elif(product_cat_limit.get(productName) is None):
                product_cat_limit[productName] = 0
            curr_product_cat_limit = product_cat_limit[productName]

            # Check if the request was successful
            if response.status_code == 200:
                # print("Success")
                data = response.json()

                products = data["products"]

                if(len(products) > 0 and curr_product_cat_limit < len(products)):
                    for i in range(curr_product_cat_limit, curr_product_cat_limit+3):
                        # i, product in enumerate(products):
                        if(i < len(products)):
                            product = products[i]
                        if(product.get("code") is not None):
                            dispatcher.utter_message(
                                text=str(i+1) + "- Barcode is " + product['code'])
                        if(product.get("image_url") is not None):
                            dispatcher.utter_message(
                                image=product['image_url'])
                        if(product.get("product_name") is not None):
                            dispatcher.utter_message(
                                text="Product Name is " + product['product_name'])
                        if(product.get("labels") is not None):
                            dispatcher.utter_message(
                                text="Product Labels: " + product['labels'])
                        if(product.get("nutriscore_data") is not None and product['nutriscore_data'].get("score") is not None):
                            dispatcher.utter_message(
                                text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                        if(product.get("nutriscore_grade") is not None):
                            dispatcher.utter_message(
                                text="Nutrition grade = " + product['nutriscore_grade'])
                    gotProducts = True

                    curr_product_cat_limit += 3
                    product_cat_limit[productName] = curr_product_cat_limit

                    return [SlotSet("product_cat_limit", product_cat_limit), SlotSet("last_searched_product_name", productName)]

            if(gotProducts == False):
                url = "https://world.openfoodfacts.org/api/v2/search?brands_tags=" + \
                    productName + ingredient_preference + "&sort_by=popularity_key"

                # Send GET request
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code == 200:

                    data = response.json()

                    products = data["products"]

                    if(len(products) > 0 and curr_product_cat_limit < len(products)):
                        for i in range(curr_product_cat_limit, curr_product_cat_limit+3):
                            # i, product in enumerate(products):
                            if(i < len(products)):
                                product = products[i]
                            if(product.get("code") is not None):
                                dispatcher.utter_message(
                                    text=str(i+1) + "- Barcode is " + product['code'])
                            if(product.get("image_url") is not None):
                                dispatcher.utter_message(
                                    image=product['image_url'])
                            if(product.get("product_name") is not None):
                                dispatcher.utter_message(
                                    text="Product Name is " + product['product_name'])
                            if(product.get("labels") is not None):
                                dispatcher.utter_message(
                                    text="Product Labels: " + product['labels'])
                            if(product.get("nutriscore_data") is not None and product['nutriscore_data'].get("score") is not None):
                                dispatcher.utter_message(
                                    text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                            if(product.get("nutriscore_grade") is not None):
                                dispatcher.utter_message(
                                    text="Nutrition grade = " + product['nutriscore_grade'])

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

        # API endpoint
        if(barcode is not None and property is not None):
            # "https://world.openfoodfacts.org/api/v2/search?labels_tags="+property+"&sort_by=popularity_key"
            url = 'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json'

            # Send GET request
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:

                product = response.json()['product']
                product_name = ""

                if(product.get("_id") is not None and product["_id"] == barcode):
                    if(product.get("product_name") is not None):
                        product_name = product['product_name']

                    if(product.get("labels") is not None):
                        labels = product['labels'].split(',')
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        if(property.lower() in stripped_labels):
                            dispatcher.utter_message(
                                text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                            return []

                    if(product.get("labels_old") is not None):
                        labels = product['labels_old'].split(',')
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        if(property.lower() in stripped_labels):
                            dispatcher.utter_message(
                                text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                            return []

                    if(product.get("ingredients_analysis_tags") is not None):
                        labels = product['ingredients_analysis_tags']
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        for label in stripped_labels:
                            if(property.lower() in label and 'no' not in label):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                return []
                            elif(property.lower() in label and 'no' in label):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has no " + property + " ingredients")
                                return []
                    if(product.get("ingredients_tags") is not None):
                        labels = product['ingredients_tags']
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        for label in stripped_labels:
                            if(property.lower() in label and 'no' not in label):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                return []
                            elif(property.lower() in label and 'no' in label):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has no " + property + " ingredients")
                                return []

                    if(product.get("traces_hierarchy") is not None):
                        labels = product['traces_hierarchy']
                        stripped_labels = [word.strip().lower()
                                           for word in labels]

                        for label in stripped_labels:
                            if(property.lower() in label and 'no' not in label):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                return []
                            elif(property.lower() in label and 'no' in label):
                                dispatcher.utter_message(
                                    text=product_name + " ( barcode: " + barcode + " )" + " has no " + property + " ingredients")
                                return []

                        dispatcher.utter_message(text="Sorry, I don't know if " + product_name +
                                                 " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                        return []

        dispatcher.utter_message(text="Sorry, I did not get that property!")
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

        vegan = 0.5
        vegetarian = 0.5
        palm_oil = 0.5

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        if(barcode is not None):
            response = requests.get(
                'https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
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
                dispatcher.utter_message(
                    text="I don't have information about this product's ingredients, sorry :/")
                return []
            dispatcher.utter_message(text="Sorry, I can't find the product.")
            return []
        dispatcher.utter_message(
            text="Oh I could not find that product! Please recheck that you entered it correctly.")
        return []


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
        if(previous_value is not None):
            [current_values.append(x)
             for x in previous_value if x not in current_values]

        # remove duplicate values
        current_values = list({x for x in current_values})

        msg = f"Ok, got it! I've updated your {preferences[preference_type]} to: {', '.join(current_values)}. Is this correct?"
        dispatcher.utter_message(text=msg)

        product_cat_limit = tracker.get_slot("product_cat_limit")
        if(product_cat_limit is not None):
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


class ActionScanReport(Action):
    def name(self) -> Text:
        return "action_scan_report"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("The tracker object is: ", tracker.latest_message)
        query = tracker.latest_message['text']

        print('The API key is:', os.environ.get('OPENAI_API_KEY'))

        embeddings_file = 'gpt_integration/embeddings.csv'
        K_DOCS = 5

        queryEngine = QueryEngine()
        # search and return the 5 most similar documents
        res = queryEngine.search_chunks(
            embeddings_file=embeddings_file, query=query, k=K_DOCS, pprint=False)
        # query
        gpt_response = queryEngine.query(res, query, 2, 20)
        text = gpt_response.content

        dispatcher.utter_message(text=text)

        return []
