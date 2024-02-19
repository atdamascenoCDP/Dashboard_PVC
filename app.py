#%%writefile app.py
from logging import PlaceHolder
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit.elements import plotly_chart
import plotly.graph_objects as go



#Carregando Dados e Ajuste
@st.cache_data
def Load_dados(endereco):
  df = pd.read_excel(endereco, sheet_name='1ª planilha')
  df["Mes"]= df["Horário desatracação"].apply(lambda x: str(x.year) + "-" + str(x.month))
  df.loc[df["Carga principal"] == "COQUE DE PETRÓLEO, BETUME DE PETRÓLEO E OUTROS RESÍDUOS DOS ÓLEOS DE PETRÓLEO","Carga principal"] = "COQUE"
  df["Berço"] = df["Berço"].astype(str)
  df = df.rename(columns={'Soma do tempo de operação paralisada': 'Paralização'})
  df["Qtd. de carga movimentada (un.)"] = df["Qtd. de carga movimentada (un.)"].astype(str)
  #df["Horário fundeio"]= df["Horário fundeio"].apply( lambda x: 0 if x=='(em branco)' else )
  return df


#Layout de Visualização da Dashboard
#/content/drive/MyDrive/Colab Notebooks/ICONS/CDP.png
st.set_page_config(page_title="Dashboard PVC", page_icon="CDP.png", layout="wide")

intro1, intro2,intro3  = st.columns(3)
with st.container():
  with intro1:
     st.title("Monitoramento PVC")
  with intro3:
    #/content/drive/MyDrive/Colab Notebooks/ICONS/cdp2.png
    st.image("cdp2.png",width=300)
    st.text('Tec. Admin. OP: Amaro Neto')



st.header('Filtros:')

col1, col2, col3 = st.columns(3)

tab1, tab2 = st.tabs(["📈 Gráficos", "🗃 Dados"])

#/content/drive/MyDrive/Colab Notebooks/banco_dados/dados.xlsx
df = Load_dados('dados.xlsx')

with st.container():

  with col1:
    month = st.selectbox("Mês",df["Mes"].unique())
    df_filtered = df[df["Mes"] == month]

  with col2:
    tipo_carga = st.selectbox("Tipo de Carga",df["Carga principal"].unique(),index=None,placeholder="")
    if tipo_carga == None:
      df_filtered = df_filtered[df_filtered["Mes"] == month]
    else:
      df_filtered = df_filtered[df_filtered["Carga principal"] == tipo_carga]

  with col3:
    berco = st.selectbox("Berço",df["Berço"].unique(),index=None,placeholder="")
    if berco == None:
      df_filtered = df_filtered[df_filtered["Mes"] == month]
    else:
      df_filtered = df_filtered[df_filtered["Berço"] == berco]


#Gráficos
with st.container():
  with tab1:
      col4, col5, col6, col7  = st.columns(4)
      col8, col9  = st.columns(2)
      col10, col11  = st.columns(2)
      with st.container():
        with col4:

          st.metric("TEMPO DE ESPERA PARA ATRACAÇÃO","----")
        with col5:
          st.metric("CUMPRIMENTO DA PROGRAMAÇÃO DE ATRACAÇÃO","----")
        with col6:
          st.metric("INDICE DE MOVIMENTAÇÃO DE CONTEINERES","----")
        with col7:
          st.metric("----","----")


      #-----------------------------------------------------------------------------------------------------------------------
      fig_date = px.pie(df_filtered, values='Peso da carga movimentada (t)', names='Operador',title="Operador Por Carga")
      col8.plotly_chart(fig_date)

      df_sem_conteiner = df_filtered[df_filtered['Carga principal']!='CONTÊINERES']
      fig_date = px.treemap(df_sem_conteiner, path=[px.Constant("Porto de Vila do Conde"), 'Carga principal','Berço'], hover_data=['Paralização'],values='Peso da carga movimentada (t)',title="Quantidade de Carga Movimentada (t)")
      col9.plotly_chart(fig_date)

      #-----------------------------------------------------------------------------------------------------------------------
      df_so_conteiner = df_filtered[df_filtered['Carga principal']=='CONTÊINERES']
      fig_date = px.pie(df_so_conteiner, values='Qtd. de contêineres movimentados (un.)', names='Operador',hover_data=['Berço'],title="Quantidade de Conteiner Movimentada (Un)")
      col10.plotly_chart(fig_date)

      df_filtered["Tempo de Atracação"] = df_filtered["Horário desatracação"] - df_filtered["Horário atracação"]
      df_tempo_navio_carga = df_filtered.groupby('Carga principal').agg({'Tempo de Atracação':'sum','Agendamento':'count','Paralização':'sum'}).reset_index()
      df_tempo_navio_carga["Tempo Médio"] = df_tempo_navio_carga["Tempo de Atracação"] / df_tempo_navio_carga["Agendamento"]
      
      df_tempo_navio_carga["Tempo Médio"] = df_tempo_navio_carga["Tempo Médio"].round('min')
      df_tempo_navio_carga = df_tempo_navio_carga.sort_values("Tempo Médio")
      df_tempo_navio_carga["Tempo Médio"] = df_tempo_navio_carga["Tempo Médio"].astype(str)
      df_tempo_navio_carga["Paralização"] = df_tempo_navio_carga["Paralização"].round(2)
      fig_date = px.bar(df_tempo_navio_carga, x="Tempo Médio", y="Carga principal",color='Paralização',orientation='h',text_auto=True,width=700,height=750, title="ESTADIA DAS EMBARCAÇÃO POR CARGA (Média) E PARALIZAÇÃO(Hrs)")
      col11.plotly_chart(fig_date)
      #-----------------------------------------------------------------------------------------------------------------------

  with tab2:
    st.dataframe(df_filtered,2000,600,hide_index=True)
