# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Any, Text, Dict, List, Union

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.forms import FormAction

import requests
import random
import json

ENDPOINTS = {"get_facility": "http://127.0.0.1:8282/webhooks/rasa/webhook/get_facility"}
FACILITY_TYPES = {"hospital": {"singular": "hospital", "mult": "hospitals"}, 
                  "pharmacy": {"singular": "pharmacy", "mult": "pharmacies"}, 
                  "mask": {"singluar": "mask", "mult": "masks"}}
FACILITY_TYPE_MESSAGES = ["Choose one of the following to search for: hospital, pharmacy, or masks.",
                          "What do you need me to find? Hospital? Pharmaceutical? Masks?"]

# Add spellchecker here later
def get_form(word: str, form: str) -> str:
    return FACILITY_TYPES[word][form]

class ChooseFacilityTypes(Action):
    def name(self) -> Text:
        return "choose_facility_types"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List:

        text = random.choice(FACILITY_TYPE_MESSAGES)
        dispatcher.utter_message(text)
        return []

class ServerFacilitySearch(Action):

    def name(self) -> Text:
        return "server_facility_search"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Call database
        data_req = json.dumps({"facility_id": tracker.get_slot('facility_id'), 
                               "facility_type": tracker.get_slot('facility_type')})
        data_resp = requests.post(ENDPOINTS['get_facility'], json=data_req)
        data = data_resp.json()

        return [SlotSet("facility_address", data.get('facility_address', 'not found'))]


class FacilityForm(FormAction):
    """ Extract city data or zip code """

    def name(self) -> Text:
        return "facility_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["facility_type", "location"]

    def slot_mappings(self) -> Dict[Text, Any]:
        return {"facility_type": self.from_entity(entity="facility_type",
                                                  intent=["inform", "search_provider"]),
                "location": self.from_entity(entity="location", intent=["inform", "search_provider"])}

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any],
               ) -> List[Dict]:
        word = tracker.get_slot('facility_type')
        #
        if word in FACILITY_TYPES:
            # Call main server for data
            data_req = json.dumps({"location": tracker.get_slot('location'), "facility_type": tracker.get_slot('facility_type'), 'amount': 3})
            data_resp = requests.post(ENDPOINTS['get_facility'], json=data_req)
            data = data_resp.json()
            keys = [k for k in data if 'facility_address' in k]
            if not keys:
                addresses = ['Not found']
            else:
                addresses = []
                for each in keys:
                    addresses.append(data[each])
            message = "\n".join(addresses)

            word = tracker.get_slot('facility_type')
            if len(addresses) == 1:
                dispatcher.utter_message(f"Here is a {get_form(word, 'singular')} near you:{message}")
            else:
                dispatcher.utter_message(f"Here are {len(addresses)} {get_form(word, 'mult')} near you:\n{message}")
        else:
            dispatcher.utter_message(f"Couldn't recognize the facility type: {word}")

        return []

class MedicalQuizForm(FormAction):
    """ Medical quiz to get help """

    def name(self) -> Text:
        return "medical_quiz_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["age", "living_alone", "taking_care_of_people", "crowded_workplace", "smoking"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
        "age": self.from_entity(entity="age", intent=["inform"]),
        "living_alone": [
            self.from_intent(intent="affirm", value=True),            
            self.from_intent(intent="deny", value=False),
        ],
        "taking_care_of_people": [
            self.from_intent(intent="affirm", value=True),
            self.from_intent(intent="deny", value=False),
        ],
        "crowded_workplace": [
            self.from_intent(intent="affirm", value=True),
            self.from_intent(intent="deny", value=False),
        ],
        "smoking": [
            self.from_intent(intent="affirm", value=True),
            self.from_intent(intent="deny", value=False),
        ]
    }

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any],
               ) -> List[Dict]:
        age = tracker.get_slot('facility_type')
        living_alone = tracker.get_slot('living_alone')
        taking_care = tracker.get_slot('taking_care_of_people')
        crowded_workplace = tracker.get_slot('crowded_workplace')
        smoking = tracker.get_slot('smoking')
        msg =  "Here is your form:\n"
        msg += f"* age:                 {age}\n"
        msg += f"* living alone:        {living_alone}\n"
        msg += f"* taking_care:         {taking_care}\n"
        msg += f"* crowded_workplace:   {crowded_workplace}\n"
        msg += f"* smoking:             {smoking}\n"
        msg += "This information will be proceed to medics, stay tuned"
        dispatcher.utter_message(msg)
        return []
