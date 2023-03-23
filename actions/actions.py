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
from datetime import date

warnings.filterwarnings("ignore")

df = pd.read_csv('./esercizi.csv', encoding='utf-8', sep=';')
remain, exs, scheda = df, None, None
fb_stretch = ['Stretching', '', 'Full body', '-', '-', '-', '-']


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def set_scheda(place: str, special=False):
    global df
    s = None
    if not special:
        if place == "palestra":
            x = df[(df['place'] == 'Palestra') | (df['place'] == 'Casa_palestra')]

            s = x[x['es_name'].isin(['Tapis roulant', 'Cyclette'])].sample(1).drop_duplicates()
            s = pd.concat([s,
                           x[(x['target'] == 'Aerobico') & (~x['es_name'].isin(['Tapis roulant', 'Cyclette']))].sample(
                               1).drop_duplicates()],
                          ignore_index=True, sort=False)
            s = pd.concat([s, x[(x['target'] == 'Braccia') & (x['type'] != 'Corpolibero')].sample(1).drop_duplicates()],
                          ignore_index=True, sort=False)
            s = pd.concat([s, x[(x['target'] == 'Busto')].sample(1).drop_duplicates()],
                          ignore_index=True, sort=False)
            s = pd.concat([s, x[(x['target'] == 'Schiena')].sample(1).drop_duplicates()],
                          ignore_index=True, sort=False)
            s = pd.concat([s, x[(x['target'] == 'Gambe')].sample(1).drop_duplicates()],
                          ignore_index=True, sort=False)
            s = pd.concat([s, x[(x['target'] == 'Addominali')].sample(1).drop_duplicates()],
                          ignore_index=True, sort=False)
            s.loc[len(s)] = fb_stretch

        elif place == "casa":
            x = df[(df['place'] == 'Casa') | (df['place'] == 'Casa_palestra')]

            s = x[x['target'] == 'Aerobico'].sample(2).drop_duplicates()
            s = pd.concat([s, x[(x['target'] == 'Braccia')].sample(2).drop_duplicates()],
                          ignore_index=True, sort=False)
            s = pd.concat([s, x[(x['target'] == 'Gambe')].sample(2).drop_duplicates()],
                          ignore_index=True, sort=False)
            s = pd.concat([s, x[(x['target'] == 'Addominali')].sample(1).drop_duplicates()],
                          ignore_index=True, sort=False)
            s.loc[len(s)] = fb_stretch
    else:
        es1 = {"es_name": "Camminata veloce", "desc": "", "target": "Aerobico", "place": "Casa", "type": "Corpolibero",
               "recupero": "", "ripetizioni": "20min"}
        x = df[df['es_name'] == 'Squat']
        s = pd.concat([pd.DataFrame.from_dict([es1]), x], ignore_index=True, sort=False)
        s = pd.concat([s, df[(df['es_name'] == 'Push Up')]], ignore_index=True, sort=False)
        s = pd.concat([s, df[(df['es_name'] == 'Walking Lunges')]], ignore_index=True, sort=False)
        s = pd.concat([s, df[(df['es_name'] == 'Crunch')]], ignore_index=True, sort=False)
        s.loc[len(s)] = fb_stretch

        print(s.head(10))

    # Creazione del DataFrame
    app = pd.DataFrame(
        {'Nome esercizi': s['es_name'], 'Target': s['target'], 'Tempo di recupero': s['recupero'],
         'Ripetizioni': s['ripetizioni']})
    app = app.set_index('Nome esercizi')
    s.drop(s.tail(1).index, inplace=True)
    return app, s


# set_scheda('casa', True)

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

        if slot_value.lower() in ['casa', 'palestra']:
            dispatcher.utter_message(text=f" Bene! Hai scelto di allenarti in {slot_value}. "
                                          f"Provo a generare una scheda full-body che possa andar bene per le tue prime "
                                          f"settimane di fitness! Attendi un secondo...")
            # dispatcher.utter_message(response="utter_generate_scheda")

            return {"Ecasapalestra": slot_value.lower()}
        else:
            dispatcher.utter_message(text="Mi sa che non ho capito bene...")
            return {"Ecasapalestra": None}


class ActionBmi(Action):
    def name(self) -> Text:
        return "action_calc_bmi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:

        pesoIn = float(tracker.get_slot('Epeso'))
        # print(pesoIn)

        altezzaIn = float(tracker.get_slot('Ealtezza'))
        # print(altezzaIn)

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

            global scheda

            s_df, scheda = set_scheda(tracker.get_slot("Ecasapalestra"), True)

            fig = ff.create_table(s_df, index=True, index_title='ESERCIZI',
                                  colorscale=[[0, '#000000'], [.5, '#80beff'], [1, '#cce5ff']],
                                  font_colors=['#ffffff', '#000000', '#000000']
                                  )

            fig.update_layout(autosize=True,
                              title_text=f'<b>Scheda esercizi di:</b>     {tracker.get_slot("Enome")}'
                                         f'                                                                           '
                                         f'<span style="font-size: 20px;"><i>Creata il: </i> {date.today().strftime("%d/%m/%Y")}</span><br>'
                                         f'<sup><i>(Principiante - 2gg a settimana)</i></sup>',
                              paper_bgcolor='#cce5ff',
                              font=dict(
                                  family="Monaco",
                                  size=18,
                                  color="Black"
                              ),
                              margin={'t': 65},
                              width=1270,
                              height=720,
                              )

            fig.write_image("scheda.png", scale=2)

            client = imgbbpy.SyncClient('b8e02f4fc7878ae94060c35ba45fa540')
            image = client.upload(file='scheda.png')
            # print(image.url)
            os.remove('scheda.png')

            dispatcher.utter_message(
                text=f"Inoltre, ti consigliamo di seguire il seguente piano di allenamento mirato a riportarti in una condizione fisica ottimale, da accompagnare alla dieta precedentemente fornita. Visualizza la scheda al seguente link: {image.url}")
        else:
            dispatcher.utter_message(
                text=f"Dal tuo BMI risulta che sei normopeso, nel caso in cui tu sia interessato a mettere su massa musacolare ecco la dieta per te.")
            dispatcher.utter_message(
                text=f"https://www.my-personaltrainer.it/alimentazione/esempio-dieta-per-aumentare-massa-muscolare.html")

        dispatcher.utter_message(
            text=f"Dimmi pure come potrei continuare ad aiutarti! :)")

        return [SlotSet("Epeso", None), SlotSet("Ealtezza", None)]


class ActionGetServizi(Action):
    def name(self) -> Text:
        return "action_get_servizi"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:
        global scheda
        scheda = None
        latest_intent = tracker.latest_message.get("intent", {}).get("name", "")
        print(latest_intent)
        if tracker.get_slot('Enome') is not None and latest_intent != 'parametriBmi':
            dispatcher.utter_message(text=f'Okay {tracker.get_slot("Enome")}! Allora ti ripeto subito i miei servizi.')
        elif latest_intent != 'parametriBmi':
            dispatcher.utter_message(text='Ora ti mostro subito che ho da offrirti!')

        dispatcher.utter_message(response="utter_servizi")

        dispatcher.utter_message(text='Dimmi tu cosa preferisci!')

        return []


class ActionCreateScheda(Action):
    def name(self) -> Text:
        return "action_create_scheda"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:
        global scheda

        s_df, scheda = set_scheda(tracker.get_slot("Ecasapalestra"))

        fig = ff.create_table(s_df, index=True, index_title='ESERCIZI',
                              colorscale=[[0, '#000000'], [.5, '#80beff'], [1, '#cce5ff']],
                              font_colors=['#ffffff', '#000000', '#000000']
                              )

        fig.update_layout(autosize=True,
                          title_text=f'<b>Scheda esercizi di:</b>     {tracker.get_slot("Enome")}'
                                     f'                                                                           '
                                     f'<span style="font-size: 20px;"><i>Creata il: </i> {date.today().strftime("%d/%m/%Y")}</span><br>'
                                     f'<sup><i>(Principiante - 2gg a settimana)</i></sup>',
                          paper_bgcolor='#cce5ff',
                          font=dict(
                              family="Monaco",
                              size=18,
                              color="Black"
                          ),
                          margin={'t': 65},
                          width=1270,
                          height=720,
                          )

        fig.write_image("scheda.png", scale=2)

        client = imgbbpy.SyncClient('b8e02f4fc7878ae94060c35ba45fa540')
        image = client.upload(file='scheda.png')
        # print(image.url)
        os.remove('scheda.png')

        dispatcher.utter_message(
            text=f"Scheda creata! Visualizzala al seguente link: {image.url}")
        dispatcher.utter_message(
            text=f"Vorresti ricevere informazioni aggiuntive sugli esercizi presenti nella scheda?")

        return [SlotSet("Ecasapalestra", None)]


class AskForTargetCorpo(Action):
    def name(self) -> Text:
        return "action_ask_Etargetcorpo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:
        df['target'] = df['target'].apply(lambda x: x.strip())
        cats = df['target'].unique()
        target = '\n'.join('- ' + t for t in cats)
        dispatcher.utter_message(text="Gli esercizi sono stati categorizzati in base alla parte del corpo. "
                                      "Le categorie attualmente gestite sono: \n" + target +
                                      "\nQuale categoria di esercizi vuoi approfondire?")

        return {}


class AskForEesercizio(Action):
    def name(self) -> Text:
        return "action_ask_Eesercizio"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:
        global remain, exs
        # genero in maniera randomica e unica gli esercizi del blocco scelto
        # poi aggiorno gli esercizi che ancora non sono stati mostrati
        exs = remain[remain["target"] == tracker.get_slot("Etargetcorpo")]
        rand_samp = 5 if exs.shape[0] > 4 else exs.shape[0]
        exs = exs.sample(rand_samp).drop_duplicates()
        remain = pd.merge(remain, exs, indicator=True, how='outer').query('_merge=="left_only"') \
            .drop('_merge', axis=1)

        # generazione bottoni
        dispatcher.utter_message(text="Clicca su uno degli esercizi per avere più informazioni.",
                                 buttons=[{"title": str(es['es_name']),
                                           "payload": '/richiesta_info_esercizio{"Eesercizio":"' + str(
                                               es['es_name']) + '"}'}
                                          for idx, es in exs.iterrows()])

        return [SlotSet("Etargetcorpo", None)]


class AskForEeserciziAction(Action):
    def name(self) -> Text:
        return "action_ask_Eesercizio"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:
        global remain, exs, scheda

        latest_intent = tracker.latest_message.get("intent", {}).get("name", "")
        print(latest_intent)
        if latest_intent == 'informazioni_scheda' and scheda is not None:
            # generazione bottoni
            dispatcher.utter_message(
                text="Clicca su uno dei seguenti esercizi della scheda per avere maggiori informazioni.",
                buttons=[{"title": str(es['es_name']),
                          "payload": '/richiesta_info_esercizio{"Eesercizio":"' + str(
                              es['es_name']) + '"}'}
                         for idx, es in scheda.iterrows()])

            return []
        else:
            # genero in maniera randomica e unica gli esercizi del blocco scelto
            # poi aggiorno gli esercizi che ancora non sono stati mostrati
            exs = remain[remain["target"] == tracker.get_slot("Etargetcorpo")]
            rand_samp = 5 if exs.shape[0] > 4 else exs.shape[0]
            exs = exs.sample(rand_samp).drop_duplicates()
            remain = pd.merge(remain, exs, indicator=True, how='outer').query('_merge=="left_only"') \
                .drop('_merge', axis=1)

            # generazione bottoni
            dispatcher.utter_message(text="Clicca su uno degli esercizi per avere più informazioni.",
                                     buttons=[{"title": str(es['es_name']),
                                               "payload": '/richiesta_info_esercizio{"Eesercizio":"' + str(
                                                   es['es_name']) + '"}'}
                                              for idx, es in exs.iterrows()])

            return [SlotSet("Etargetcorpo", None)]


class GetInfoEs(Action):
    def name(self) -> Text:
        return "action_get_info_es"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Any:
        global exs, scheda, df

        esercizioin = str(tracker.get_slot('Eesercizio'))
        # print(esercizioin)
        descrizione = df[df['es_name'] == esercizioin].iloc[0]['desc']

        dispatcher.utter_message(text=f"{esercizioin}: {descrizione}")

        if scheda is not None:
            buttons = scheda
        else:
            buttons = exs

        # generazione bottoni
        dispatcher.utter_message(text="Clicca su uno degli esercizi per avere più informazioni.",
                                 buttons=[{"title": str(es['es_name']),
                                           "payload": '/richiesta_info_esercizio{"Eesercizio":"' + str(
                                               es['es_name']) + '"}'}
                                          for idx, es in buttons.iterrows()])
        return [SlotSet("Eesercizio", None)]


class ValidateTargetCorpoForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_targetcorpo_form"

    def validate_Etargetcorpo(
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
            return {"Etargetcorpo": None}

        # check se sono già stati mostrati tutti gli esercizi disponibili
        if remain[remain["target"] == slot_value.capitalize()].shape[0] == 0:
            dispatcher.utter_message(
                text="Ti ho già mostrato tutti gli esercizi che avevo disponibili, perciò te li ripropongo!")
            remain = df
        else:
            dispatcher.utter_message(
                text=f"OK! Di seguito troverai alcuni esercizi del blocco '{slot_value.capitalize()}'")
        return {"Etargetcorpo": slot_value.capitalize(), "Eesercizio": None}
