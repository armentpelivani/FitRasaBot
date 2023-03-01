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
import random
import pandas as pd  
import numpy as np
import matplotlib.pyplot as plt
import tabulate
from tabulate import tabulate
import os
import requests
import csv



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
    
    
class ValidateNomeForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_nome_form"
    
    def validate_Enome(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        dispatcher.utter_message(text=f" Molto piacere {slot_value}")
        return{"Enome":slot_value}
    

class ValidateCasaPalestraForm(FormValidationAction):
        
     def name(self) -> Text:
        return "validate_casapalestra_form"
    
     def validate_Ecasapalestra(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        dispatcher.utter_message(text=f" hai scelto di allenarti in {slot_value}")
        return{"Ecasapalestra":slot_value}

class ActionBmi(Action):
#
    def name(self) -> Text:
         return "action_calc_bmi"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> Dict[Text, Any]:
          
          dispatcher.utter_message(text=f"Bene, sto procedendo con il calcolo, pochi secondi e conoscerai la dieta migliore da seguire per il tuo fisico ")
        
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
               dispatcher.utter_message(text=f"Ti consigliamo di seguire il seguente piano di allenamento mirato a riportarti in una condiione fisic ottimale, da accompagnare alla dieta precedentemente fornita")
          else :
               dispatcher.utter_message(text=f"Dal tuo BMI risulta che sei NORMOPESO, nel caso in cui tu sia interessato a mettere su massa musacolare ecco la dieta per te ")
               dispatcher.utter_message(text=f"https://www.my-personaltrainer.it/alimentazione/esempio-dieta-per-aumentare-massa-muscolare.html")     
          
          

          return {}

