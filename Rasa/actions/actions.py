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
                    print(f'The value to add is: vegan, actual value: {event.get("value")}')
                    previous_value = event.get("value")
                    break
                
                skipped = True

        current_values = tracker.get_slot(preference_type) or []

        # extend the previous values with the current values without duplicates. 
        [current_values.append(x) for x in previous_value if x not in current_values]

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
        food_processing_preference = tracker.get_slot("food_processing_preference")
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
            dispatcher.utter_message(text="You haven't specified any preferences yet.")
        else: 
            dispatcher.utter_message(text="Your preferences are: " + msg)
        
        return []

