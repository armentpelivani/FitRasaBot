# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker,FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType
from rasa_sdk.types import DomainDict
from reportlab.pdfgen import canvas
import random
import pandas as pd  
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import tabulate
from tabulate import tabulate
import os
import requests
import csv

import io

my_canvas = canvas.Canvas("./hello.pdf")
my_canvas.drawString(100, 750, "Welcome to Reportlab!")
my_canvas.save()
df = pd.read_csv(r".\csv esercizi.csv",sep=';',encoding='utf-8') 

print(df) 


class ValidateBmiForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_bmi_form"
    
    def validate_Epeso(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        dispatcher.utter_message(text=f" Il tuo peso è di {slot_value}")
        return{"Epeso":slot_value}
    
    def validate_Ealtezza(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        dispatcher.utter_message(text=f" la tua altezza è di {slot_value}")
        return{"Ealtezza":slot_value}


class ActionBmi(Action):
#
    def name(self) -> Text:
         return "action_calc_bmi"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> Dict[Text, Any]:
        
          pesoIn =float(tracker.get_slot('Epeso'))
          print(pesoIn)
          
          altezzaIn =float(tracker.get_slot('Ealtezza'))
          print(altezzaIn)

          bmi =  pesoIn/(altezzaIn * altezzaIn)

          if bmi < 18.4:
               dispatcher.utter_message(text=f" Dal tuo BMI risulta che sei sottopeso per tenato questa è la dieta consigliata per te ")
               dispatcher.utter_message(text=f"https://www.my-personaltrainer.it/alimentazione/esempio-dieta-per-aumentare-massa-muscolare.html")
          elif bmi > 25 :
               dispatcher.utter_message(text=f"Dal tuo BMI risulta che sei sovrappeso per tenato questa è la dieta consigliata per te")
               dispatcher.utter_message(text=f"https://www.my-personaltrainer.it/alimentazione/dieta-mediterranea-menu-settimanale-nutrizionista.html")
          else :
               dispatcher.utter_message(text=f"Dal tuo BMI risulta che sei NORMOPESO, nel caso in cui tu sia interessato a mettere su massa musacolare ecco la dieta per te ")
               dispatcher.utter_message(text=f"https://www.my-personaltrainer.it/alimentazione/esempio-dieta-per-aumentare-massa-muscolare.html")     
          
          # apri il file pdf
          # with open('./hello.pdf', 'rb') as f:
          #      pdf_data = f.read()

          # # crea una stringa di byte
          # pdf_bytes = io.BytesIO(pdf_data)
               
          # # aggiungi l'evento di risposta con il file pdf allegato
          # dispatcher.utter_attachment(pdf_bytes,"hello.pdf")

          return {}

