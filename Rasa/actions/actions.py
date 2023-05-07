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
        return [SlotSet("name", user_input)]

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
        return []

