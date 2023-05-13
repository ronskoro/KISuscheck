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

from typing import Text, Dict, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

# set slot sample action
class SetSlotFromUserInput(Action):
    def name(self) -> Text:
        return "action_set_slot_from_user_input"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract the value from the user input
        user_input = list(tracker.latest_message.get('text').split())[-1]
        # slot_value = user_input # Replace this with your own logic to extract the slot value
        
        # Set the slot value
        return [SlotSet("user_name", user_input)]

class getProductInfoByBarcode(Action):
    def name(self) -> Text:
        return "action_get_product_info_by_barcode"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Extract the value from the user input
        barcode = list(tracker.latest_message.get('text').split())[-1]

        # fetch product info from https://world.openfoodfacts.org/api/v0/product/barcode.json
        response = requests.get('https://world.openfoodfacts.org/api/v0/product/'+barcode+'.json')
        dispatcher.utter_message(image=response.json()['product']['image_url'])
        dispatcher.utter_message(text="Product Name is " + response.json()['product']['generic_name'])
        dispatcher.utter_message(text= "Product Labels: " + response.json()['product']['labels'])
        dispatcher.utter_message(text="Nutrition score = " + response.json()['product']['nutriscore_data']['score'].__str__())
        dispatcher.utter_message(text="Nutrition grade = " + response.json()['product']['nutriscore_grade'])
        return []

# Method to set preferences from the following categories:
# nutritional value, food processing value, allergens, ingredients, labels, environment
# More info can be found here: "https://docs.google.com/document/d/100quDLq2fWTMjHoeyUZulthfNG3Fq8NsalNo_DacQHk/edit?usp=sharing"
# Returns: sets the slot type to the list of preferences set by the user. 
class ActionSetPreference(Action):
    def name(self) -> Text:
        return "action_set_preference"

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
        
        # todo: Fix this. Right now, it has it's own slot type here. 
        # Need to find out which slot type is being set. 
        # 1st possibility: set two slots: preference_type, and preference
        preference_type = tracker.get_slot("preference_type")
        preferences = list(tracker.get_latest_entity_values("preference"))

        # check if the preference type has been set
        if not preference_type:
            msg = "I am sorry. I didn't get the type of preference you want to set. Could you specify it again?"
            dispatcher.utter_message(text=msg)
            return []

        # check if there are preferences
        if not preferences:
            msg = "I am sorry. I didn't get that. Could you specify your preferences again?"
            dispatcher.utter_message(text=msg)
            return []

        msg = f"Ok, got it! I've updated your {preferences[preference_type]}."
        dispatcher.utter_message(text=msg)

        return [SlotSet(preference_type, preferences)]

