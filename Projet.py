import streamlit as st
import numpy as np
import random
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import plotly_express as px
import time
import streamlit.components.v1 as components
from functools import wraps
import altair as alt
import seaborn as sns
from streamlit.proto.Checkbox_pb2 import Checkbox
import pydeck as pdk



def config():

    st.set_page_config(
        page_title = 'Dashboard',
        page_icon = '✅',
        layout = 'wide')
config()

def check_time(func):
    def wrapper(*args, **kwargs):
        with open("logs.txt", "a") as f:
            start = time.time()
            val = func(*args, **kwargs)
            end = time.time()
            f.write("\nThe function %s " % func.__name__ + " took " + str(end - start) + "s to complete\n")
            f.write('\n-----------------------------------------------------------------\n')
        return val
    return wrapper

def get_weekday(df):
    return df.weekday()

def get_dom(df):
    return df.day

def get_hours(df):
    return df.hour

def count_rows(rows):
    return len(rows)


@st.cache  
@check_time(func)
def load(dataframe):
    

    df = pd.read_csv(dataframe,sep=',',low_memory=False)
    df = df.sample(700000)
    df = df.sort_values(by = ['code_departement'])
    return df

def topdata(df):
    st.write(df.head(10))



def altair():
    df1 = df.sample(70000)
    c = alt.Chart(df1).mark_circle().encode(
    x='code_departement', y='surface_reelle_bati', color='valeur_fonciere', tooltip=['valeur_fonciere', 'surface_reelle_bati', 'surface_terrain'])

    return st.altair_chart(c, use_container_width=True)

@st.cache(allow_output_mutation=True)
def transformation(df):
    df['valeur_fonciere'] = df['valeur_fonciere'].astype(float)
    df['surface_reelle_bati'] = df['surface_reelle_bati'].astype(float)
    df['nombre_pieces_principales'] = df['nombre_pieces_principales'].astype(float)
    df['surface_terrain'] = df['surface_terrain'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    df['latitude'] = df['latitude'].astype(float)
    return df

@st.cache(allow_output_mutation=True)
def metrecarre(df):
    df['mettrecarre'] = df['valeur_fonciere'] / df['surface_reelle_bati']
    return df

@st.cache(allow_output_mutation=True)
def drop(df):
    df = df.drop(['adresse_code_voie', 'id_mutation', 'date_mutation', 'numero_disposition', 'nature_culture', 'ancien_code_commune', 'ancien_nom_commune', 'ancien_id_parcelle','lot1_numero','lot2_numero','lot3_numero','lot4_numero','lot5_numero','lot1_surface_carrez','lot2_surface_carrez','lot3_surface_carrez','lot4_surface_carrez','lot5_surface_carrez'], axis=1)
    return df


def select_region(df):
    select_region = getregion(df)
    select_region = getsales(df, select_region)
    st.write("Nombre de maison dans le département : " + str(select_region))


def graph_bar(abs, ord,databar):
     data=alt.Chart(databar).mark_bar().encode(  x = abs, y = ord)
     data


def getsales(df, option):
    cpt = 0
    choix_region = st.select_slider('choissisez un departement', options = option)
    for i in df['code_departement']:
        if i == choix_region:
            cpt += 1
    return cpt

@st.cache()
def getregion(df):
    dept = []
    for i in df['code_departement']:
        if i not in dept  :
            dept.append(i)
    return dept 

def graph_line(abs,ord,databar):
    data=alt.Chart(databar).mark_line().encode(x=abs,y=ord)
    data

def type_habit():
    choice = st.selectbox('Choose the type of habitation :', ['Maison', 'Appartement', 'Dépendance', 'Local industriel. commercial ou assimilé'])
    return choice

def mask1(nom,valeur1):
    return df.mask(df[nom]<valeur1)

def mask2(nom,valeur2):
    return df.mask(df[nom]!=valeur2)

def histogram(nom,bins,range1,range2):
    hist_values = np.histogram(
        df[nom], bins=bins, range=(range1,range2))[0]
    st.bar_chart(hist_values)

def slider():
    number = st.slider('Combien de villes souhaitez vous afficher ?', 2, 50, 10)
    return number

def classement(df,nb):

    st.subheader("")
    mask = (df['nature_mutation']=="Vente")
    df = df.loc[mask]
    
    
    df = df.groupby('nom_commune').apply(count_rows)
    

    df = df.sort_values(ascending = False)

    fig = px.bar(df.head(nb))
    st.plotly_chart(fig)

def map_pourcent(df):
    percentage = st.number_input("choix du pourcentage d'affichage")
    st.write("Map avec " + str(percentage) + "% de la dataset")
    df1 = df.sample(frac = percentage/100)
    st.map(df1[np.isnan(df1['latitude']) == False])

def compare_data(df, column1, column2):
    c1 = df[column1]
    c2 = df[column2]

    compare = pd.concat([c1, c2], axis=1)

    fig1, ax = plt.subplots()
    ax.plot(compare)

    st.pyplot(fig1)

def locd_df(df, colu, param):
    return df.loc[df[colu] == param] 

def pie_chart(df):
    countfiltered3 = df['nombre_pieces_principales'].value_counts()
    fig = px.pie(countfiltered3, values='nombre_pieces_principales', names=countfiltered3.index, title='distribution des nombres de pièces')
    st.plotly_chart(fig)

def plot_frequency_by_local_type(dataframe):
        figure = plt.figure()
        x = ["Appartement","Dépendance", "Local industriel.\ncommercial\nassimilé", "Maison"]
        y = dataframe.groupby("type_local").apply(count_rows)
        plt.pie(y, labels=x)
        return figure
def areachart():
    df1 = df.sample(70000)
    data = pd.DataFrame()
    data['nombre de pieces'] = df1['nombre_pieces_principales'] 
    data['valeur_fonciere'] = df1['valeur_fonciere'] 
   
    return st.area_chart(data)   

def prixm2(df):
    st.subheader('Voici quelques données par m² :')
    col1, col2, col3= st.columns(3) 
    col1.metric("Valeur moyenne de la propriété", df['mettrecarre'].min())
    col2.metric("Par m² du terrain total", df['mettrecarre'].max())
    col3.metric("Par m² de bâtiment", df['mettrecarre'].mean()) 

filepath = "full_2020.csv"
df = load(filepath)
df = drop(df)
df = transformation(df)
df = metrecarre(df)
def box(nom1,list1):
    return st.selectbox(nom1,list1)

def choix(arg1,arg2):
    choice = [arg1,arg2]
    return choice
choice = choix('Vision Globale','Les stats')

def option(arg):
    choice = choix('Vision Globale','Les stats')
    optionss = st.sidebar.selectbox(arg, choice)
    
   
    st.set_option('deprecation.showPyplotGlobalUse', False)
    if optionss == choice[0]:
       
        st.header('Vision Globale')
        st.text("Cette page représente la vision globale de la dataset full_2020.csv")
        
        topdata(df)
        st.text("ici vous trouverez un slider permettant de select un departement et de trouver le nombre d'habitation dans celui-ci")
        select_region(df)
        map_pourcent(df)

    elif optionss == choice[1]:
        st.header('La DATASET')
        topdata(df)
        if st.checkbox('description de la dataset'):
            st.write(df.describe())
        st.title('Les stats !')
        st.text("Les 10 premières lignes de la dataset")
        pie_chart(df)
        


        #histogram('date_mutation',0,0,13)
    
        st.subheader("Valeur fonciere en fonction de la surface réel du batiment")
        choice = type_habit()
        data_created = locd_df(df, 'type_local', choice)
        compare_data(data_created, 'surface_reelle_bati', 'valeur_fonciere')
        st.header("Voici le classement des ventes en fonctions des villes")
        nb = slider()
        
        classement(df,nb)
        st.header('comparaison du prix en fonction du m2')
        compare_data(df,"valeur_fonciere","mettrecarre")
        figure = plot_frequency_by_local_type(df)
        st.header("Répartition des différents type de local")
        st.write(figure)
        prixm2(df)
        st.title('Graphique représentant la surface réelle du batiment en fonction du département et comme paramètre la valeur fonciere')
        altair()
        st.title('Graphique représentant la valeur fonciere en fonction du nomnbre de piece')
        areachart()
        


option('Où voulez vous aller ?')
components.html("""
<link href="https://unpkg.com/tailwindcss@%5E2/dist/tailwind.min.css" rel="stylesheet">
<div class="max-w-sm rounded overflow-hidden shadow-lg mx-auto my-8">
    <img class="w-full" src="data:image/jpeg;base64,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" alt="Coucou c'est moi !">
    <div class="px-6 py-4">
      <div class="font-bold text-xl mb-2">Futur Data Scientist</div>
      <p class="text-gray-600 text-base">
        Voici donc mon travail sur cet énorme dataset, le chargement des données fut une vrai problématique, mais j'ai beaucoup aimé travaillé sur cet aspect la
      </p>
    </div>
    <div class="px-6 py-4">
      <span class="inline-block bg-gray-100 rounded-full px-3 py-1 text-sm font-semibold text-gray-600 mr-2">#DataViZ</span>
      <span class="inline-block bg-gray-100 rounded-full px-3 py-1 text-sm font-semibold text-gray-600 mr-2">#Dataset</span>
      
    </div>
  </div>
      </div>
    """,
    height=600,

)


            