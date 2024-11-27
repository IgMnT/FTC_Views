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

st.set_page_config(
    page_title='Visão Empresa',
    page_icon='📈',
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
    
    return df1

def orderMetric(df1):
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    graph = px.bar(df_aux, x= 'Order_Date', y = 'ID')
    return graph


def trafficOrderShare(df1):
    cols = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN', :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    graph = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
    return graph

def trafficOrderCity(df1):
    cols = ['ID','City', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN', :]
    df_aux = df_aux.loc[df_aux['City']!='NaN', :]
    graph = px.scatter( df_aux, x= 'City', y='Road_traffic_density', size='ID', color='City')
    return graph

def orderByWeek(df1):
    df1['semana'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = df1.loc[:, ['ID', 'semana']].groupby('semana').count().reset_index()
    graph = px.line(df_aux, x='semana', y='ID')
    return graph

def orderShareByWeek(df1):
    df_aux1 = df1.loc[:, ['ID', 'semana']].groupby('semana').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'semana']].groupby('semana').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner', on='semana')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    graph = px.line(df_aux, x='semana', y='order_by_deliver')
    return graph

def CountryMap(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!='NaN', :]
    df_aux = df_aux.loc[df_aux['City']!='NaN', :]
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                            location_info['Delivery_location_longitude']],
                            popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    return map

# Importando o dataset
df = pd.read_csv('../dataset/treino.csv')

# Limpando os dados
df1 = dataProcessing(df)

#=======================================
#Layout Barra Lateral
#=======================================
st.header('Marketplace - Visão cliente')

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
st.dataframe( df1 )



#=======================================
#Layout Streamlit
#=======================================

tab1, tab2, tab3 =  st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

    

with tab1:
    with st.container():    
        st.markdown("# Orders by day")    
        graph = orderMetric(df1)
        st.plotly_chart(graph, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('# Traffic Order Share')
            graph = trafficOrderShare(df1)
            st.plotly_chart(graph, use_container_width=True)
        with col2:
            st.markdown('# Traffic Order City')
            graph = trafficOrderCity(df1)
            st.plotly_chart(graph, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Orders per week')
        graph = orderByWeek(df1)
        st.plotly_chart(graph, use_container_width=True)
    with st.container():
        st.markdown('# Order Share by Week')
        graph = orderShareByWeek(df1)
        st.plotly_chart(graph, use_container_width=True)

with tab3:
    st.header('# Map')
    
    map = CountryMap(df1)
    folium_static( map, width=1024, height=600)