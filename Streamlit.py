import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from sqlalchemy import create_engine
import pyodbc

# Conexão usando SQLAlchemy para melhor integração com Pandas
def init_connection():
    server = st.secrets["server"]
    database = st.secrets["database"]
    username = st.secrets["username"]
    password = st.secrets["password"]
    conn_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    return create_engine(conn_string)

engine = init_connection()

# Função simplificada para executar queries
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

    if not df.empty:
        # Titulo do aplicativo Streamlit
        st.title('Equipment Control')

        # AgGrid para edição de dados
        grid_options_builder = GridOptionsBuilder.from_dataframe(df)
        grid_options_builder.configure_pagination(enabled=True)  # Habilita paginação
        grid_options_builder.configure_columns(['Equipment', 'Organization'], editable=True)
        grid_options = grid_options_builder.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            height=400,
            width='100%'
        )

        updated_df = pd.DataFrame(grid_response['data'])

        if st.button('Save Changes to Database'):
            for idx, row in updated_df.iterrows():
                sql = "UPDATE Equipments SET Equipment = ?, Organization = ? WHERE Resources = ?"
                params = (row['Equipment'], row['Organization'], row['Resources'])
                with engine.begin() as conn:  # Garantindo que a conexão seja fechada após o commit
                    conn.execute(sql, params)
            st.success('Changes saved successfully!')
        else:
            st.write("No changes to save.")
    else:
        st.write("No data found.")










