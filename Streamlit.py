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
@st.cache_data(ttl=10)  # cache por 10 seg
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

    st.title('Equipment Control')

    if not df.empty:
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
            update_mode=GridUpdateMode.MANUAL,  # Evita atualizações automáticas
            fit_columns_on_grid_load=True,
            height=550,
            width='100%'
        )
        updated_df = pd.DataFrame(grid_response['data'])

        if st.button('Save Equipment Changes'):
            for idx, row in updated_df.iterrows():
                sql = "UPDATE Equipments SET Equipment = ?, Organization = ? WHERE Resources = ?"
                params = (row['Equipment'], row['Organization'], row['Resources'])
                with engine.begin() as conn:
                    conn.execute(sql, params)
            st.cache_data.clear()  # Limpa o cache após salvar as mudanças
            st.experimental_rerun()  # Recarrega a página para atualizar os dados exibidos
            st.success('Equipment changes saved successfully!')
    else:
        st.write("No equipment data found.")
else:
    st.sidebar.warning("Please log in to view the application.")













        








