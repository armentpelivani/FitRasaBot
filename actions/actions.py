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
from rasa_sdk.events import EventType, SlotSet, FollowupAction
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
remain = df
exs = None
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

        es_name = ['Squat', 'Bench press', 'Deadlift', 'Shoulder press', 'Leg press', 'Lat pulldown', 'Barbell curl',
                   'Dumbbell fly', 'Plank', 'Russian twist']
        target = ['Gambe', 'Petto', 'Schiena', 'Spalle', 'Gambe', 'Schiena', 'Bicipiti', 'Petto', 'Core', 'Addominali']
        tempo_recupero = [120, 90, 150, 60, 120, 90, 60, 60, 30, 30]
        ripetizioni = [5, 8, 5, 10, 12, 10, 12, 8, 60, 40]
        peso = [100, 80, 120, 50, 150, 80, 30, 10, 0, 0]

        # Creazione del DataFrame
        df = pd.DataFrame(
            {'Nome esercizi': es_name, 'Target': target, 'Ripetizioni': ripetizioni,
             'Peso': peso, 'Tempo di recupero': tempo_recupero})
        df = df.set_index('Nome esercizi')
        # Visualizzazione del DataFrame
        print(df)

        fig = ff.create_table(df, index=True, index_title='ESERCIZI')
        fig.update_layout(autosize=True, title_text='Scheda esercizi', margin={'t': 40, 'b': 20})
        fig.write_image("scheda.png", scale=2)

        client = imgbbpy.SyncClient('b8e02f4fc7878ae94060c35ba45fa540')
        image = client.upload(file='scheda.png')
        # print(image.url)
        os.remove('scheda.png')

        dispatcher.utter_message(
            text=f"Scheda creata! Visualizzala al seguente link: {image.url}")

        return {}


class AskForEeserciziAction(Action):
    def name(self) -> Text:
        return "action_ask_Eesercizio"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:

        global remain, exs
        # genero in maniera randomica e unica gli esercizi del blocco scelto
        # poi aggiorno gli esercizi che ancora non sono stati mostrati
        exs = remain[remain["target"] == tracker.get_slot("Ecorpoallenamento")]
        rand_samp = 5 if exs.shape[0] > 4 else exs.shape[0]
        exs = exs.sample(rand_samp).drop_duplicates()
        remain = pd.merge(remain, exs, indicator=True, how='outer').query('_merge=="left_only"') \
            .drop('_merge', axis=1)

        # generazione bottoni
        dispatcher.utter_message(text="Clicca su uno degli esercizi per avere più informazioni.",
                                 buttons=[{"title": str(es['es_name']),
                                           "payload":'/richiesta_info_esercizio{"Eesercizio":"'+str(es['es_name'])+'"}'}
                                          for idx, es in exs.iterrows()])

        return [SlotSet("Ecorpoallenamento", None)]




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
        global remain
        if slot_value.capitalize() not in df['target'].unique():
            dispatcher.utter_message(
                text=f"Non riconosco questa parte del corpo. I target gestiti sono: {'/'.join(df['target'].unique())}.")
            return {"Ecorpoallenamento": None}

        # check se sono già stati mostrati tutti gli esercizi disponibili
        if remain[remain["target"] == slot_value.capitalize()].shape[0] == 0:
            dispatcher.utter_message(
                text="Ti ho già mostrato tutti gli esercizi che avevo disponibili, perciò te li ripropongo!")
            remain = df
        else:
            dispatcher.utter_message(
                text=f"OK! Di seguito troverai alcuni esercizi del blocco '{slot_value.capitalize()}'")
        return {"Ecorpoallenamento": slot_value.capitalize()}
    
# validazione dell' esercizio selezionato
    def validate_Eesercizio(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Any:
        global exs
        esercizioin = str(tracker.get_slot('Eesercizio'))
        descrizione = df[df['es_name'] == esercizioin].iloc[0]['desc']

        dispatcher.utter_message(text=f"{esercizioin}: {descrizione}")

        '''# generazione bottoni
        dispatcher.utter_message(text="Clicca su uno degli esercizi per avere più informazioni.",
                                 buttons=[{"title": str(es['es_name']),
                                           "payload": '/richiesta_info_esercizio{"Eesercizio":"' + str(
                                               es['es_name']) + '"}'}
                                          for idx, es in exs.iterrows()])'''

        return[SlotSet("Eesercizio", None)]