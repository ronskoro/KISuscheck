# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Text, Dict, Any, List
from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType
import requests
import pandas as pd


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

        # fetch product info from https://world.openfoodfacts.org/api/v2/product/barcode.json
        if (barcode is not None):
            response = requests.get(
                'https://world.openfoodfacts.org/api/v2/product/'+barcode+'.json')
            resProduct = response.json()['product']
            if (response.status_code == 200 and response.json().get('product') is not None):
                if (resProduct.get("image_url") is not None):
                    dispatcher.utter_message(image=resProduct['image_url'])
                if (resProduct.get("product_name_en") is not None):
                    dispatcher.utter_message(
                        text="Product Name is " + resProduct['product_name_en'])
                if (resProduct.get("labels") is not None):
                    dispatcher.utter_message(
                        text="Product Labels: " + resProduct['labels'])
                if (resProduct.get("nutriscore_data") is not None and resProduct['nutriscore_data'].get("score") is not None):
                    dispatcher.utter_message(
                        text="Nutrition score = " + resProduct['nutriscore_data']['score'].__str__())
                if (resProduct.get("nutriscore_grade") is not None):
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

        # API endpoint
        if (productName is not None):
            url = "https://world.openfoodfacts.org/api/v2/search?categories_tags=" + \
                productName+"&sort_by=popularity_key"

            # Send GET request
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                print("Success")
                data = response.json()

                products = data["products"]

                if (len(products) > 0):
                    for i, product in enumerate(products):
                        if i == 3:
                            break
                        if (product.get("code") is not None):
                            dispatcher.utter_message(
                                text=str(i+1) + "- Barcode is " + product['code'])
                        if (product.get("image_url") is not None):
                            dispatcher.utter_message(
                                image=product['image_url'])
                        if (product.get("product_name") is not None):
                            dispatcher.utter_message(
                                text="Product Name is " + product['product_name'])
                        if (product.get("labels") is not None):
                            dispatcher.utter_message(
                                text="Product Labels: " + product['labels'])
                        if (product.get("nutriscore_data") is not None and product['nutriscore_data'].get("score") is not None):
                            dispatcher.utter_message(
                                text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                        if (product.get("nutriscore_grade") is not None):
                            dispatcher.utter_message(
                                text="Nutrition grade = " + product['nutriscore_grade'])
                    gotProducts = True
                    return []

            if (gotProducts == False):
                url = "https://world.openfoodfacts.org/api/v2/search?brands_tags=" + \
                    productName+"&sort_by=popularity_key"

                # Send GET request
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code == 200:

                    data = response.json()

                    products = data["products"]

                    if (len(products) > 0):
                        for i, product in enumerate(products):
                            if i == 3:
                                break
                            if (product.get("code") is not None):
                                dispatcher.utter_message(
                                    text=str(i+1) + "- Barcode is " + product['code'])
                            if (product.get("image_url") is not None):
                                dispatcher.utter_message(
                                    image=product['image_url'])
                            if (product.get("product_name") is not None):
                                dispatcher.utter_message(
                                    text="Product Name is " + product['product_name'])
                            if (product.get("labels") is not None):
                                dispatcher.utter_message(
                                    text="Product Labels: " + product['labels'])
                            if (product.get("nutriscore_data") is not None and product['nutriscore_data'].get("score") is not None):
                                dispatcher.utter_message(
                                    text="Nutrition score = " + product['nutriscore_data']['score'].__str__())
                            if (product.get("nutriscore_grade") is not None):
                                dispatcher.utter_message(
                                    text="Nutrition grade = " + product['nutriscore_grade'])
                        return []

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
        if (barcode is not None and property is not None):
            # "https://world.openfoodfacts.org/api/v2/search?labels_tags="+property+"&sort_by=popularity_key"
            url = 'https://world.openfoodfacts.org/api/v2/product/'+barcode+'.json'

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

                        if (property.lower() in stripped_labels):
                            dispatcher.utter_message(
                                text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                        else:
                            if (product.get("labels_old") is not None):
                                labels = product['labels_old'].split(',')
                                stripped_labels = [word.strip().lower()
                                                   for word in labels]

                                if (property.lower() in stripped_labels):
                                    dispatcher.utter_message(
                                        text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                else:
                                    if (product.get("ingredients_analysis_tags") is not None):
                                        labels = product['ingredients_analysis_tags']
                                        stripped_labels = [
                                            word.strip().lower() for word in labels]

                                        for label in stripped_labels:
                                            if (property.lower() in label and 'no' not in label):
                                                dispatcher.utter_message(
                                                    text=product_name + " ( barcode: " + barcode + " )" + " has " + property + " ingredients")
                                                return []

                                        dispatcher.utter_message(
                                            text=product_name + " ( barcode: " + barcode + " )" + " has no " + property + " ingredients")
                        return []

        dispatcher.utter_message(text="Sorry, I did not get that property!")
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
                    print(
                        f'The value to add is: vegan, actual value: {event.get("value")}')
                    previous_value = event.get("value")
                    break

                skipped = True

        current_values = tracker.get_slot(preference_type) or []

        # extend the previous values with the current values without duplicates.
        if (previous_value is not None):
            [current_values.append(x)
             for x in previous_value if x not in current_values]

        msg = f"Ok, got it! I've updated your {preferences[preference_type]} to: {', '.join(current_values)}. Is this correct?"
        dispatcher.utter_message(text=msg)

        return [SlotSet(preference_type, current_values)]


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

        latest_entity_values = tracker.get_latest_entity_values(
            entity_type="barcode")
        barcodes = list(latest_entity_values)
        # print(barcodes) # ['12345667778', '12345667778']

        product_comparison_list = tracker.get_slot("product_comparison_list")
        if product_comparison_list == None:
            product_comparison_list = []
        for barcode in barcodes:
            if barcode not in product_comparison_list:
                product_comparison_list.append(barcode)
            else:
                dispatcher.utter_message(
                    text="This product ({}) is already in the comparison list.".format(barcode))
            break

        product_comparison_list_length = tracker.get_slot(
            "product_comparison_list_length")
        product_comparison_list_length = len(product_comparison_list)

        return [SlotSet("product_comparison_list", product_comparison_list), SlotSet("product_comparison_list_length", product_comparison_list_length)]


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
                            "Oops, I could not find this product with barcode {} 😞 Please recheck if you typed it correctly. Otherwise, it might not be available in our dataset.".format(barcode))
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
                    'kisusscore_json': None,
                    'openfood_json': None,
                    'product_img_url': None}
            product_comparison_df = pd.DataFrame(data)
            for barcode in product_comparison_list:
                if (barcode is not None):
                    openfood_response = requests.get(
                        'https://world.openfoodfacts.org/api/v2/product/'+barcode)
                    if (openfood_response.status_code == 200 and openfood_response.json().get('product') is not None):
                        product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                            'product_name']] = openfood_response.json()['product']['product_name']
                        # product_comparison_df.loc[product_comparison_df['barcode'] == barcode, ['openfood_json']] = openfood_response.json()
                        product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                            'product_img_url']] = openfood_response.json()['product']['image_url']
                    else:
                        dispatcher.utter_message(
                            "Oops, I could not find this product with barcode {} 😞 Please recheck if you typed it correctly. Otherwise, it might not be available in our dataset.".format(barcode))
                        continue
                    susscore_response = requests.get(
                        'https://kisuscheck.org/middleware/productscore/'+barcode)
                    print(susscore_response.text)
                    if (susscore_response.status_code == 200 and susscore_response.json().get('id') == int(barcode)):
                        product_comparison_df.loc[product_comparison_df['barcode'] == barcode, [
                            'kisusscore']] = susscore_response.json()['KISusScore']['totalScore']
                        # product_comparison_df.loc[product_comparison_df['barcode'] == barcode, ['kisusscore_json']] = susscore_response.json()
                    else:
                        dispatcher.utter_message(
                            "Oops, I could not calculate the KISus-Score of this product ({}) 😞 If the barcode is correct, it might not be available in our dataset. Otherwise, there might be something wrong with our server, please try again.".format(barcode))
            product_comparison_df.sort_values(
                by=['kisusscore'], ascending=False, na_position='last', inplace=True)
            product_comparison_df.reset_index(inplace=True)
            with pd.option_context('display.max_rows', None,
                                   'display.max_columns', None
                                   ):
                print(product_comparison_df)
            for index in range(len(product_comparison_list)):
                if (product_comparison_df.iloc[index]['product_name'] is not None):
                    if (product_comparison_df.iloc[index]['kisusscore'] is not None):
                        if (product_comparison_df.iloc[index]['product_img_url'] is not None):
                            dispatcher.utter_message(
                                text=str(index+1)+". "+product_comparison_df.iloc[index]['product_name']+" ("+product_comparison_df.iloc[index]['barcode']+")\n" +
                                "   KISus-Score: " +
                                str(product_comparison_df.iloc[index]
                                    ['kisusscore']),
                                image=product_comparison_df.iloc[index]['product_img_url'])
                        else:
                            dispatcher.utter_message(
                                text=str(index+1)+". "+product_comparison_df.iloc[index]['product_name']+" ("+product_comparison_df.iloc[index]['barcode']+")\n" +
                                "   KISus-Score: "+str(round(product_comparison_df.iloc[index]['kisusscore'], 1)) +
                                "\n   no image available")
                    else:
                        if (product_comparison_df.iloc[index]['product_img_url'] is not None):
                            dispatcher.utter_message(
                                text=str(index+1)+". "+product_comparison_df.iloc[index]['product_name']+" ("+product_comparison_df.iloc[index]['barcode']+")\n" +
                                "   KISus-Score: unknow",
                                image=product_comparison_df.iloc[index]['product_img_url'])
                        else:
                            dispatcher.utter_message(
                                text=str(index+1)+". "+product_comparison_df.iloc[index]['product_name']+" ("+product_comparison_df.iloc[index]['barcode']+")\n" +
                                "   KISus-Score: unknow\n   no image available")
                else:
                    dispatcher.utter_message(
                        text=str(index+1)+". product with barcode "+product_comparison_df.iloc[index]['barcode']+" doesn't found in our database.")
            product_comparison_df = product_comparison_df.to_json()
        return [SlotSet("product_comparison_result", product_comparison_df)]


class ActionFillSecondProductForComparison(Action):
    def name(self) -> Text:
        return "action_fill_second_product_for_comparison"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        latest_entity_values = tracker.get_latest_entity_values(
            entity_type="barcode")
        if latest_entity_values != None:
            barcodes = list(latest_entity_values)

            first_product_for_comparison = tracker.get_slot(
                "first_product_for_comparison")
            second_product_for_comparison = tracker.get_slot(
                "second_product_for_comparison")
            product_comparison_list = tracker.get_slot(
                "product_comparison_list")

            for barcode in barcodes:
                if product_comparison_list != None and first_product_for_comparison != None and second_product_for_comparison == None:
                    if product_comparison_list[0] == first_product_for_comparison:
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
