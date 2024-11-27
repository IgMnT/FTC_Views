import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🏠',
)


image_path = 'C:\\Users\\IgorMagro\\Documents\\istockphoto-1252769165-612x612.jpg'
image = Image.open( image_path )
st.sidebar.image (image, width=120)
st.sidebar.markdown('# Cury company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""___""")
st.write("# Curry Company Growth Dashboard")
st.markdown(
    """
    ### 📈 Growth Dashboard
    ### Como usar:
    - Visão Empresa:
        - Visão Gerencial
        - Visão Tática
        - Visão Geográfica
    - Visão Restaurantes
    - Visão Entregadores
    """
)

