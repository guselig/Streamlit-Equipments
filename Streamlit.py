import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from sqlalchemy import create_engine
import pyodbc

# Inicialização da conexão
def init_connection():
    server = st.secrets["server"]
    database = st.secrets["database"]
    username = st.secrets["username"]
    password = st.secrets["password"]
    conn_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    return create_engine(conn_string)

engine = init_connection()

# Função para executar queries
@st.cache_data(ttl=600)  # cache por 10 minutos
def run_query(query):
    return pd.read_sql_query(query, engine)

# Definição das credenciais para login
USER = "admin"
PASSWORD = "Dorf$"

# Verificação das credenciais
def check_login(username, password):
    return username == USER and password == PASSWORD

# Tela de login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if check_login(username, password):
        st.session_state['logged_in'] = True
        st.experimental_rerun()
    else:
        st.sidebar.error("Incorrect Username or Password")

# Restante da aplicação após login
if st.session_state['logged_in']:
    df = run_query("SELECT * FROM Equipments;")
    df2 = run_query("SELECT * FROM Capacities;")
    df2 = pd.DataFrame(df2)
    df2 = df2[['Equipment', 'Ideal_production_rate', 'Hours_available_per_day', 'Hours_scheduled_shutdowns_month', 'Capacity']]

    aba1, aba2 = st.tabs(['Equipment Control', 'Capacities'])

    with aba1:
        if not df.empty:
            st.title('Equipment Control')
            grid_options_builder = GridOptionsBuilder.from_dataframe(df)
            grid_options_builder.configure_pagination(enabled=True)
            equipment_options = df2['Equipment'].unique().tolist()  
            organization_options = ['Macaé', 'NSR']
            grid_options_builder.configure_column("Equipment", cellEditor='agSelectCellEditor', cellEditorParams={'values': equipment_options}, editable=True)
            grid_options_builder.configure_column("Organization", cellEditor='agSelectCellEditor', cellEditorParams={'values': organization_options}, editable=True)
            grid_options = grid_options_builder.build()
            grid_response = AgGrid(
                df,
                gridOptions=grid_options,
                enable_enterprise_modules=True,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                fit_columns_on_grid_load=True,
                height=480,
                width='100%'
            )
            updated_df = pd.DataFrame(grid_response['data'])

    with aba2:
        if not df2.empty:
            st.title('Capacities')

            # Configurando o GridOptionsBuilder a partir do DataFrame
            grid_options_builder = GridOptionsBuilder.from_dataframe(df2)
            grid_options_builder.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True, hide=True)
            grid_options_builder.configure_column("Equipment", hide=False, editable=False, headerName="Equipment")
            grid_options_builder.configure_column("Capacity", hide=False, editable=True, headerName="Capacity (kg/month)")

            # Habilitando a paginação
            grid_options_builder.configure_pagination(enabled=True)

            # Construindo as opções do grid
            grid_options = grid_options_builder.build()

            # Exibindo o AgGrid com as opções configuradas
            grid_response = AgGrid(
                df2,
                gridOptions=grid_options,
                enable_enterprise_modules=True,
                fit_columns_on_grid_load=True,
                height=275,
                width= 50  # Ajustando a largura automaticamente
            )

            updated_df2 = pd.DataFrame(grid_response['data'])








        








