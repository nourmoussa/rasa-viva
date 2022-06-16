# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import time
from typing import Any, Text, Dict, List
from matplotlib import image
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests
import json
from interpret import show
import joblib
from interpret import set_visualize_provider
from interpret.provider import DashProvider
from sqlalchemy import null
from http.server import BaseHTTPRequestHandler, HTTPServer


sleep_time = 0.5 # not woking when in loop, it flushes all messages together

factor_slots = ["gender", "alco", "age", "smoke", "daily_activity", "height", "weight"]

# hostName = "localhost"
# serverPort = 8070

class RiskAssessment(Action):

    def name(self) -> Text:
        return "action_risk_assessment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            url = 'http://127.0.0.1:5000'
            # url = 'https://heroku-app-cvd.herokuapp.com/'
            # payload = json.dumps({
            #     # "age": int(tracker.get_slot("age")),
            #     "age":tracker.get_slot("age"),
            #     "gender": float(tracker.get_slot("gender")),
            #     "height": tracker.get_slot("height"),
            #     "weight": tracker.get_slot("weight"),
            #     "smoke": float(tracker.get_slot("smoke")),
            #     "alco": float(tracker.get_slot("alco")),
            #     "active": float(tracker.get_slot("daily_activity"))
            #     })
            # headers = {
            #     'Content-Type': 'application/json'
            # }
            model = joblib.load('actions/reg_1.pkl')
            # prediction = model.predict([[int(tracker.get_slot("age")),0,168,62,0,1,1]])
            # prediction = model.predict([[int(tracker.get_slot("age")),int(tracker.get_slot("gender")),int(tracker.get_slot("height")),int(tracker.get_slot("weight")),int(tracker.get_slot("smoke")),int(tracker.get_slot("alco")),int(tracker.get_slot("daily_activity"))]])
            prediction = model.predict([[int(tracker.get_slot("age")),float(tracker.get_slot("gender")),tracker.get_slot("height"),tracker.get_slot("weight"),float(tracker.get_slot("smoke")),float(tracker.get_slot("alco")),float(tracker.get_slot("daily_activity"))]])            
            output = prediction[0]
            # response = requests.request("POST", url, headers=headers, data=payload)
            # result=response.json()
            # if result["result"]==1:
            #     dispatcher.utter_message(text="cvd risk")
            # elif result["result"] == 0:
            #     dispatcher.utter_message(text="no cvd")  
            if output==1:
                dispatcher.utter_message(text="Based on your inputs, I have concluded that your physiological and behavioral markers make you prone to having cardiovascular diseases.")
            elif output == 0:
                dispatcher.utter_message(text="Congratulations! Based on your inputs, I have concluded that your physiological and behavioral markers do not make you prone to having cardiovascular diseases. Keep it up!")             
            
        except: 
            dispatcher.utter_message(text="I am experiencing some issues, let's try again!")
            return []

class ExplainRisk(Action):

    def name(self) -> Text:
        return "action_explain_risk"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        model = joblib.load('actions/reg_1.pkl')
        prediction = model.predict([[int(tracker.get_slot("age")),int(tracker.get_slot("gender")),float(tracker.get_slot("height")),int(tracker.get_slot("weight")),int(tracker.get_slot("alco")),int(tracker.get_slot("smoke")),int(tracker.get_slot("daily_activity"))]])
        # prediction = model.predict([[int(tracker.get_slot("age")),0,168,62,0,1,1]])
        # prediction = model.predict([[int(tracker.get_slot("age")),float(tracker.get_slot("gender")),tracker.get_slot("height"),tracker.get_slot("weight"),float(tracker.get_slot("smoke")),float(tracker.get_slot("alco")),float(tracker.get_slot("daily_activity"))]])            
        # Take the first value of prediction

        output = prediction[0]

        # lr_local = model.explain_local([[int(tracker.get_slot("age")),0,168,62,0,1,1]])
        # lr_local = model.explain_local([[int(tracker.get_slot("age")),float(tracker.get_slot("gender")),tracker.get_slot("height"),tracker.get_slot("weight"),float(tracker.get_slot("smoke")),float(tracker.get_slot("alco")),float(tracker.get_slot("daily_activity"))]])
        lr_local = model.explain_local([[int(tracker.get_slot("age")),int(tracker.get_slot("gender")),float(tracker.get_slot("height")),int(tracker.get_slot("weight")),int(tracker.get_slot("smoke")),int(tracker.get_slot("alco")),int(tracker.get_slot("daily_activity"))]])
        # show(lr_local)

        dispatcher.utter_message(text=str(output))

        dispatcher.utter_message(text=str(output))  

        # set_visualize_provider(DashProvider.from_address(('127.0.0.1', 8070)))
        plotly_fig = lr_local.visualize(0)
        plotly_fig.write_image("fig1.jpg")

        # webServer = HTTPServer((hostName, serverPort), plotly_fig)    
        # print("Server started http://%s:%s" % (hostName, serverPort))

        # webbrowser.open('http://127.0.0.1:7001/')
        # dispatcher.utter_message(image="https://5c1a-2a0c-5bc0-40-2e34-f94a-80bd-c0d2-af90.eu.ngrok.io/fig1.jpg")


def slow_response (msg, dispatcher: CollectingDispatcher):
    time.sleep(sleep_time)
    dispatcher.utter_message(text=msg) 
    return []

#age 
class ActionReceiveAge(Action):
    def name(self) -> Text:
        return "action_set_age"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        age = tracker.latest_message['age']
        dispatcher.utter_message(text="Your age is {age}")
        #return [SlotSet("age")]
        return[]

class ActionReceiveAlco(Action):
    def name(self) -> Text:
        return "action_set_alco"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
           tracker.get_slot("alco")
        except:
            dispatcher.utter_message(text="Error Occur!")
        dispatcher.utter_message(text="Alcohol consumption status set")
        return []

class ActionReceivesSmoke(Action):
    def name(self) -> Text:
        return "action_set_smoke"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
           tracker.get_slot("smoke")
        except:
            dispatcher.utter_message(text="Error Occur!")
        dispatcher.utter_message(text="Smoking status set")
        return []


#BMI
class WeightSET(Action):
    def name(self) -> Text:
        return "action_set_weight"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
           tracker.get_slot("weight")
        except:
            dispatcher.utter_message(text="Error Occur!")
        dispatcher.utter_message(text="Weight set")
        return []
        #return [SlotSet("weight", weight)]

class HeightSET(Action):
    def name(self) -> Text:
        return "action_set_height"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            tracker.get_slot("height")
        except:
            dispatcher.utter_message(text="Error Occur!")
        dispatcher.utter_message(text="Height set")
        return []


# def convert_cm_to_meter(height):
#     return float((height)/100)

def bmi_calculation(weight, height):
    #return float((weight)/(height*height))
    return float(weight)/((height**2))

def get_bmi_status(bmi):
    if bmi < 15:
       return  "Unfortunately, you fall into the severely underweight percentile."
    elif bmi >= 15 and bmi <16:
        return "Severely underweight"
    elif bmi >=16 and bmi < 18.5:
        return "Underweight"
    elif bmi >= 18.5 and bmi < 26: 
        return "Good news! You fall into the normal healthy BMI percentile."
    elif  bmi >= 26 and bmi <30:
        return "Unfortunately, you fall into the overweight percentile. It is important to focus on factors you can control, such as weight. Weight gain increases blood pressure, insulin resistance and cholesterol, which affect the CVD risk."
    elif bmi>= 30 and bmi <35:
        return "Unfortunately, you fall into the moderately obese percentile. It is important to focus on factors you can control, such as weight. Weight gain increases blood pressure, insulin resistance and cholesterol, which affect the CVD risk."
    else:
        return "Unfortunately, you fall into the severely overweight percentile. It is important to focus on factors you can control, such as weight. Weight gain increases blood pressure, insulin resistance and cholesterol, which affect the CVD risk."


class CalculeteBMI(Action):
    def name(self) -> Text:
        return "action_calculate_bmi"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            height =  float(tracker.get_slot("height"))
            print(height)
            # height = convert_cm_to_meter(height)
       
            weight = float(tracker.get_slot("weight"))
            print(weight)
            bmi = bmi_calculation(weight, height)
            bmi_status = get_bmi_status(bmi)
            dispatcher.utter_message(text="Your BMI is: "+ str(round(bmi, 2))+ ". " + bmi_status)
        except:
            dispatcher.utter_message(text="Error Occur!")
            return []
