## medical quiz
* medical_quiz_trigger
    - utter_quiz_introduction
* affirm
    - medical_quiz_form
    - form{"name": "medical_quiz_form"}
    - slot{"requested_slot": "age"}
* form: inform{"age": "50"}
    - slot{"age": "50"}
    - form: medical_quiz_form
    - slot{"age": "50"}
    - slot{"requested_slot": "living_alone"}
* form: inform{"living_alone": "yes"}
    - slot{"living_alone": "yes"}
    - form: medical_quiz_form
    - slot{"living_alone": "yes"}
    - slot{"requested_slot": "taking_care_of_people"}
* form: inform{"taking_care_of_people": "yes"}
    - slot{"taking_care_of_people": "yes"}
    - form: medical_quiz_form
    - slot{"taking_care_of_people": "yes"}
    - slot{"requested_slot": "crowded_workplace"}
* form: inform{"crowded_workplace": "yes"}
    - slot{"crowded_workplace": "yes"}
    - form: medical_quiz_form
    - slot{"crowded_workplace": "yes"}
    - slot{"requested_slot": "smoking"}
* form: inform{"smoking": "yes"}
    - slot{"smoking": "yes"}
    - form: medical_quiz_form
    - form{"name": null} 
* thanks
    - utter_noworries

## unhappy path
* medical_quiz_trigger
    - utter_quiz_introduction
* deny
    - utter_help_with_something_else

## happy_path
* greet
    - utter_ask_me_anything   
* inform{"facility_type": "hospital"}    
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": 4245}
    - server_facility_search
    - utter_address
* thanks
    - utter_noworries

## happy_path_multi_requests
* greet
    - utter_ask_me_anything
* inform{"facility_type": "hospital"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "747604"}
    - server_facility_search
    - utter_address
* search_provider{"facility_type": "hospital"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": 4245}   
    - server_facility_search
    - utter_address

## happy_path_2
* search_provider{"location": "Austin", "facility_type": "hospital"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "450871"}
    - server_facility_search
    - utter_address
* thanks
    - utter_noworries

## story_goodbye
* goodbye
    - utter_goodbye

## story_thankyou
* thanks
    - utter_noworries

## Handle insult
* handleinsult
    - utter_handle_insult

## Handle "Are you bot?" question
* is_bot_question
    - utter_is_bot

## Handle feedback
* canthelp
    - utter_cant_help
