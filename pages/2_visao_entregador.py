#=======================================
#Bibliotecas
#=======================================

from haversine import haversine 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from datetime import datetime 
from PIL import Image
import plotly.express as px
import folium
from streamlit_folium import folium_static
df = pd.read_csv('../dataset/treino.csv')
st.set_page_config(
    page_title='Visão Entregadores',
    page_icon='👨‍🍳',
    layout = 'wide'
)


#=======================================
# Funções
#=======================================
def dataProcessing(df1):
    df1 = df.copy()
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']
    df1 = df1[df1['Road_traffic_density'] != 'NaN ']
    df1 = df1[df1['City'] != 'NaN ']
    df1 = df1[df1['Festival'] != 'NaN ']
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1 = df1[df1['multiple_deliveries'] != 'NaN ']
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['ID'] = df1['ID'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['City'] = df1['City'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1]).astype(int)
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df1['Weatherconditions'] = df1['Weatherconditions'].apply(lambda x: x.split('conditions')[1])
    return df1


def topDelivers(df1, asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
           .groupby(['Delivery_person_ID', 'City'])
           .mean()
           .sort_values(['City', 'Time_taken(min)'], ascending=asc)
           .reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitan', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3  
    



#Inicialização
df1 = dataProcessing(df)



#=======================================
#Layout Barra Lateral
#=======================================
st.header('Marketplace - Visao Entregadores')

image_path = 'C:\\Users\\IgorMagro\\Documents\\istockphoto-1252769165-612x612.jpg'
image = Image.open( image_path )
st.sidebar.image (image, width=120)
st.sidebar.markdown('# Cury company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
                        'Até qual valor?',
                        value=datetime(2022, 4, 13),
                        min_value=datetime(2022, 2, 11),
                        max_value=datetime(2022, 4, 6),
                        format='DD-MM-YYYY')

st.sidebar.markdown("""___""")
traffic_options = st.sidebar.multiselect('Quais as opções de transito?', ['Low', 'Medium', 'High', 'Jam'], default = ['Low', 'Medium', 'High', 'Jam']
)

linhas_selecionadas = df1['Order_Date'] < date_slider  
df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]




#=======================================
#Layout Streamlit
#=======================================

tab1, tab2, tab3 =  st.tabs(['Visão Gerencial', '-', '-'])
with tab1:
    with st.container():
        st.header('Overall Metrics')
        col1, col2, col3 , col4= st.columns(4, gap='large')
        with col1:
            idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', idade)
        with col2:
            idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', idade)
        with col3:
            condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição de veículo', condicao)
        with col4:
            condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', condicao)
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')

        col1,col2 = st.columns(2)
        with col1:
            st.markdown('#### Avaliação media por entregador')
            df_av = df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_av)
        with col2:
            st.markdown('#### Avaliação media por transito')
            df_avg = (df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density'). agg({'Delivery_person_Ratings':['mean', 'std']}))
            df_avg.columns = ['Media_entrega', 'Std_entrega']
            st.dataframe(df_avg)
            st.markdown('Avaliação media por clima')
            df_avg_climate = df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').mean().reset_index()
            st.dataframe(df_avg_climate)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Top entregadores mais rapidos')
            asc = False
            df3 = topDelivers(df1, asc)
            st.dataframe(df3)
        with col2:
            st.markdown('#### Top entregadores mais lentos')
            asc = True
            df3 = topDelivers(df1, asc)
            st.dataframe(df3)



