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
import numpy as np
from streamlit_folium import folium_static
df = pd.read_csv('../dataset/treino.csv')
st.set_page_config(
    page_title='Visão Restaurantes',
    page_icon='🏠',
    layout = 'wide'
)


#=======================================
# Funções
#=======================================
def dataProcessing(df):
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


def distanciaMedia(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distancia'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    media = np.round(df1['distancia'].mean(), 2)
    return media
    

def entregaFestival(df1, festival,op):
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
    return df_aux


def tempoEntregaCidade(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distancia'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    media = df1.loc[:, ['City', 'distancia']].groupby('City').mean().reset_index()
    graph = go.Figure(data=[go.Pie(labels=media['City'], values=media['distancia'], pull=[0, 0.1, 0])])
    return graph


def distribuicaoTempoCidade(df1):
    cols = ['City', 'Time_taken(min)']
    df_media = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_media.columns = ['avg_time', 'std_time']
    df_media = df_media.reset_index()
    graph = go.Figure()
    graph.add_trace(go.Bar(name = 'Control', x= df_media['City'], y= df_media['avg_time'], error_y=dict(type='data', array=df_media['std_time'])))
    graph.update_layout(barmode='group')
    return graph

def distribuicaoTempoTrafego(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    media_por_trafego = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    media_por_trafego.columns = ['avg_time', 'std_time']
    media_por_trafego = media_por_trafego.reset_index()
    graph = px.sunburst(media_por_trafego, path=['City', 'Road_traffic_density'], values = 'avg_time',
                    color = 'std_time', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(media_por_trafego['std_time']))
    return graph


def distribuicaoDistancia(df1):
    cols = ['City', 'Time_taken(min)', 'Type_of_order']
    df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)' : ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    return df_aux


#Iniciazação
df1 = dataProcessing(df)

#=======================================
#Layout Barra Lateral
#=======================================
st.header('Marketplace - Visao Restaurantes')

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
        st.title('Visão Geral')
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        
        with col1:
            entregadores_uniq = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Número de entregadores', entregadores_uniq)
        with col2:
            media = distanciaMedia(df1)
            col2.metric('Distancia media das entregas', media)

        with col3:
            festival = 'Yes'
            op = 'avg_time'
            df_aux = entregaFestival(df1, festival, op)
            col3.metric('Tempo medio de entrega com festival', df_aux)
        
        with col4:
            festival = 'Yes'
            op = 'std_time'
            df_aux = entregaFestival(df1, festival, op)
            col4.metric('Desvio padrão com festival', df_aux)
        
        with col5:
            festival = 'No'
            op = 'avg_time'
            df_aux = entregaFestival(df1, festival, op)
            col5.metric('Tempo medio de entrega sem festival', df_aux)

        with col6:
            festival = 'No'
            op = 'std_time'
            df_aux = entregaFestival(df1, festival, op)
            col6.metric('Desvio padrão sem festival', df_aux)

    with st.container():
        st.markdown("""___""")
        st.title('Tempo medio de entrega por cidade')
        graph = tempoEntregaCidade(df1)
        st.plotly_chart(graph, use_container_width=True)
    
    with st.container():
        st.markdown("""___""")
        st.title('Distribuição do tempo de entrega')
        col1,col2 = st.columns(2)
        with col1:
            st.markdown('Tempo medio de entrega por cidade')
            graph = distribuicaoTempoCidade(df1)
            st.plotly_chart(graph, use_container_width=True)       
        with col2:
            graph = distribuicaoTempoTrafego(df1)
            st.plotly_chart(graph, use_container_width=True)

    with st.container():
        st.markdown("""___""")
        st.title('Distribuição da distância dos restaurantes')
        df_aux = distribuicaoDistancia(df1)
        st.dataframe(df_aux)
        