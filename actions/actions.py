# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
import time
# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.types import DomainDict
import random
import pandas as pd
from pandas.plotting import table
import dataframe_image as dfi
import plotly.figure_factory as ff
import plotly.graph_objs as go
import numpy as np
import matplotlib.pyplot as plt
import tabulate
from tabulate import tabulate
import os
import requests
import csv
from imgur_python import Imgur
from os import path
import warnings
warnings.filterwarnings("ignore")


df = pd.read_csv('./esercizi.csv', encoding='utf-8', sep=';')
print(df.head(), df.shape)



def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


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

        peso = slot_value.replace(',', '.')
        if isfloat(peso) and 10 < float(peso) < 200:
            dispatcher.utter_message(text=f" Il tuo peso è di {peso}")
            return {"Epeso": peso}
        else:
            dispatcher.utter_message(text=f"Sembrerebbe che tu non abbia inserito correttamente il tuo peso..")
            return {"Epeso": None}


    def validate_Ealtezza(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        altezza = slot_value.replace(',', '.')
        if isfloat(altezza) and 0.20 < float(altezza) < 2.30:
            dispatcher.utter_message(text=f" La tua altezza è di {altezza}")
            return {"Ealtezza": altezza}
        else:
            dispatcher.utter_message(text=f"Sembrerebbe che tu non abbia inserito correttamente la tua altezza..")
            return {"Ealtezza": None}


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
        dispatcher.utter_message(text=f" Molto piacere {slot_value}!")
        return {"Enome": slot_value}


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
        return {"Ecasapalestra": slot_value}


class ActionBmi(Action):
    #
    def name(self) -> Text:
        return "action_calc_bmi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:

        pesoIn = float(tracker.get_slot('Epeso'))
        print(pesoIn)

        altezzaIn = float(tracker.get_slot('Ealtezza'))
        print(altezzaIn)

        bmi = pesoIn / (altezzaIn * altezzaIn)

        if bmi < 18.4:
            dispatcher.utter_message(
                text=f" Dal tuo BMI risulta che sei sottopeso per tanto questa è la dieta consigliata per te.")
            dispatcher.utter_message(
                text=f"https://www.my-personaltrainer.it/alimentazione/esempio-dieta-per-aumentare-massa-muscolare.html")
        elif bmi > 25:
            dispatcher.utter_message(
                text=f"Dal tuo BMI risulta che sei sovrappeso per tanto questa è la dieta consigliata per te.")
            dispatcher.utter_message(
                text=f"https://www.my-personaltrainer.it/alimentazione/dieta-mediterranea-menu-settimanale-nutrizionista.html")
            dispatcher.utter_message(
                text=f"Ti consigliamo di seguire il seguente piano di allenamento mirato a riportarti in una condizione fisica ottimale, da accompagnare alla dieta precedentemente fornita.")
        else:
            dispatcher.utter_message(
                text=f"Dal tuo BMI risulta che sei normopeso, nel caso in cui tu sia interessato a mettere su massa musacolare ecco la dieta per te.")
            dispatcher.utter_message(
                text=f"https://www.my-personaltrainer.it/alimentazione/esempio-dieta-per-aumentare-massa-muscolare.html")

        return [SlotSet("Epeso", None), SlotSet("Ealtezza", None)]


class ActionCreateScheda(Action):
    #
    def name(self) -> Text:
        return "action_create_scheda"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:

        # TODO: Andare a generare la scheda per l'utente sulla base degli slot settati

        # BT: 0ab4fb1600d1b92585cfd70a1fcef76d813c62a4
        fig = ff.create_table(df[['es_name', 'target']])
        fig.update_layout(autosize=True, title_text='Scheda esercizi', margin={'t': 40, 'b': 20})
        fig.write_image("scheda.png", scale=2)

        imgur_client = Imgur({'client_id': '9d34aee8442dac3'})
        file = path.realpath('./scheda.png')
        title = 'Scheda esercizi'
        description = ''
        album = None
        disable_audio = 0
        response = imgur_client.image_upload(file, title, description, album, disable_audio)
        #print(response['response']['data']['link'])
        os.remove('scheda.png')


        dispatcher.utter_message(
                text=f"Scheda creata! Visualizzala al seguente link: {response['response']['data']['link']}")

        return {}

# Azione per la creazinoe di pulsanti 

class AskEserciziInfo(Action):
    def name(self) -> Text:
        return "action_ask_Eesercizi"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        dispatcher.utter_message(
            text="Questi sono alcuni dei nostri esercizi",
            buttons=[
                {"title":"esercizio1","payload":"/affermazione"}
            ],

        )
        return[]


class ValidateEserciziForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_esercizi_form"


    def validate_Eesercizi(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pizza_size` value."""
        if tracker.get_intent_of_latest_message() == "affermazione":
            dispatcher.utter_message(
                text="questa è la descrizione dell' esercizio"
            )
        return {"Eesercizi": True}