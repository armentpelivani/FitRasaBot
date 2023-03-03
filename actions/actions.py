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
import plotly.figure_factory as ff
import plotly.graph_objs as go
import imgbbpy
import numpy as np
import matplotlib.pyplot as plt
import tabulate
from tabulate import tabulate
import os
import requests
import csv
from os import path
import warnings
warnings.filterwarnings("ignore")


df = pd.read_csv('./esercizi.csv', encoding='utf-8', sep=';')
#print(df.head(), df.shape)

# estraggo i sottodataframe
schienadf = df.loc[1:6] 
bracciadf = df.loc[7:13]
gambedf = df.loc[14:20]
bustodf = df.loc[21:28]

# mi creo i dataframe con gli indici di colonna randomici

schienadf.index=np.random.permutation(np.arange(len(schienadf)))
bracciadf.index=np.random.permutation(np.arange(len(bracciadf)))
gambedf.index=np.random.permutation(np.arange(len(gambedf)))
bustodf.index=np.random.permutation(np.arange(len(bustodf)))



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


        fig = ff.create_table(df[['es_name', 'target']])
        fig.update_layout(autosize=True, title_text='Scheda esercizi', margin={'t': 40, 'b': 20})
        fig.write_image("scheda.png", scale=2)

        client = imgbbpy.SyncClient('b8e02f4fc7878ae94060c35ba45fa540')
        image = client.upload(file='scheda.png')
        #print(image.url)
        os.remove('scheda.png')


        dispatcher.utter_message(
                text=f"Scheda creata! Visualizzala al seguente link: {image.url}")

        return {}

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
        if tracker.get_intent_of_latest_message() == "affermazione":
            dispatcher.utter_message(
                text="questa è la descrizione dell' esercizio"
            )
        return {"Eesercizi": True}
    
class ValidateCorpoAllenamentoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_corpoallenamento_form"
    
    def validate_Ecorpoallenamento(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
        ) -> Dict[Text, any]:
        # mi costruisco il dataset degli esercizi per le gambe 
        #gambedf = df.loc[14:20]
        #genero in maniera randomica e non ripetitiva gli indici del dataframe degli esercizi gambe 
        gambedf.index=np.random.permutation(np.arange(len(gambedf)))
        

        
        if slot_value == ("gambe"):

            dispatcher.utter_message(
                buttons= [
                    {"title":str(gambedf.iloc[0]['es_name']) ,"payload":str(gambedf.iloc[0]['desc'])},
                    {"title":str(gambedf.iloc[1]['es_name']) ,"payload":str(gambedf.iloc[1]['desc'])},
                    {"title":str(gambedf.iloc[2]['es_name']) ,"payload":str(gambedf.iloc[2]['desc'])},
                    {"title":str(gambedf.iloc[3]['es_name']) ,"payload":str(gambedf.iloc[3]['desc'])}
                    ])


        elif slot_value == ("braccia"):
             dispatcher.utter_message(
                text="questi sono gli esercizi delle braccia"
            )
        elif slot_value == ("schiena"):
             dispatcher.utter_message(
                text="questi sono gli esercizi delle schiena"
            )
        elif slot_value == ("busto"):
             dispatcher.utter_message(
                text="questi sono gli esercizi delle busto"
            )
        else:
            dispatcher.utter_message(
                text="la tua richiesta non è valida (grupby colonne dataframe)"
            )
        return {"Ecorpoallenamento" : slot_value }




# Azione per la creazinoe di pulsanti
class AskEserciziInfo(Action):
    def name(self) -> Text:
        return "action_ask_Eesercizi"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        
        return[]