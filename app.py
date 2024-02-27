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
  #df = pd.read_csv(DATA_URL)
  df["Mes"]= df["Horário desatracação"].apply(lambda x: str(x.year) + "-" + str(x.month))
  df.loc[df["Carga principal"] == "COQUE DE PETRÓLEO, BETUME DE PETRÓLEO E OUTROS RESÍDUOS DOS ÓLEOS DE PETRÓLEO","Carga principal"] = "COQUE"
  df["Berço"] = df["Berço"].astype(str)
  df = df.rename(columns={'Soma do tempo de operação paralisada': 'Paralisação'})
  df["Qtd. de carga movimentada (un.)"] = df["Qtd. de carga movimentada (un.)"].astype(str)
  df["Tempo de Atracação"] = df["Horário desatracação"] - df["Horário atracação"]
  #df["Horário fundeio"]= df["Horário fundeio"].astype(str)
  return df

def graf_op_mov_carg():
  fig_date = px.pie(df_filtered, values='Peso da carga movimentada (t)', names='Operador',title="Operador Por Carga")
  return fig_date

def graf_carg_mov(df_enviado):
  df_sem_conteiner = df_enviado[df_enviado['Carga principal']!='CONTÊINERES']
  fig_date = px.treemap(df_sem_conteiner, path=[px.Constant("Porto de Vila do Conde"), 'Carga principal','Berço'],values='Peso da carga movimentada (t)',title="Quantidade de Carga Movimentada (t)")
  return fig_date

def graf_paralizacao(df_enviado):
  df_temp_berco_carga = df_enviado.groupby('Berço').agg({'Paralisação':'sum'}).reset_index()
  df_temp_berco_carga["Paralisação"] = df_temp_berco_carga["Paralisação"].round(2)
  fig_date = px.sunburst(df_temp_berco_carga, path=['Berço'], values='Paralisação',width=700,title="PARALISAÇÃO(Hora) Por Berço")
  #fig_date = px.bar(df_temp_berco_carga, x="Berço", y="Paralisação",color="Berço",text_auto=True,width=700,height=750, title="PARALISAÇÃO(Hrs) Por Berço")
  return fig_date

def graf_stad_emb(df_enviado):
  df_tempo_navio_carga = df_enviado.groupby('Carga principal').agg({'Tempo de Atracação':'sum','Agendamento':'count','Paralisação':'sum'}).reset_index()
  df_tempo_navio_carga["Tempo Médio"] = df_tempo_navio_carga["Tempo de Atracação"] / df_tempo_navio_carga["Agendamento"]

  df_tempo_navio_carga["Tempo Médio"] = df_tempo_navio_carga["Tempo Médio"].round('min')
  df_tempo_navio_carga = df_tempo_navio_carga.sort_values("Tempo Médio")
  df_tempo_navio_carga["Tempo Médio"] = df_tempo_navio_carga["Tempo Médio"].astype(str)
  fig_date = px.bar(df_tempo_navio_carga, x="Tempo Médio", y="Carga principal",orientation='h',text_auto=True,width=700,height=750, title="ESTADIA DAS EMBARCAÇÃO POR CARGA (Média)")
  return fig_date

def graf_mov_conteiner(df_enviado):
  df_so_conteiner = df_enviado[df_enviado['Carga principal']=='CONTÊINERES']
  fig_date = px.pie(df_so_conteiner, values='Qtd. de contêineres movimentados (un.)', names='Operador',hover_data=['Berço'],title="Quantidade de Conteiner Movimentada (Un)")
  return fig_date

#Layout de Visualização da Dashboard
#/content/drive/MyDrive/Colab Notebooks/ICONS/CDP.png
#Img/CDP.png
st.set_page_config(page_title="Dashboard PVC", page_icon="Img/CDP.png", layout="wide")

intro1, intro2,intro3  = st.columns(3)
with st.container():
  with intro1:
     st.title("Monitoramento PVC")
  with intro3:
    #/content/drive/MyDrive/Colab Notebooks/ICONS/cdp2.png
    #Img/cdp2.png
    st.image("Img/cdp2.png",width=300)
    st.text('Tec. Admin. OP: Amaro Neto')



st.header('Filtros:')

col1, col2, col3 = st.columns(3)

tab1, tab2, tab3 = st.tabs(["📈 Gráficos", ":ship: Embarcações",":bookmark_tabs: Relatório"])

#/content/drive/MyDrive/Colab Notebooks/banco_dados/dados.xlsx
#Base_Dados/dados.xlsx
df = Load_dados('Base_Dados/dados.xlsx')

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
      col10,col11  = st.columns(2)
      col12, col13  = st.columns(2)

      with st.container():
        with col4:
          st.metric("TEMPO DE ESPERA PARA ATRACAÇÃO","----")
        with col5:
          st.metric("CUMPRIMENTO DA PROGRAMAÇÃO DE ATRACAÇÃO","----")

        with col6:
          st.metric("INDICE DE MOVIMENTAÇÃO DE CONTEINERES","----")

        with col7:
          emb = df_filtered['Embarcação'].count()
          st.metric("Total de Embarcações",emb)

        with col8:
          fig_date = graf_op_mov_carg()
          col8.plotly_chart(fig_date)

        with col9:
          fig_date = graf_carg_mov(df_filtered)
          col9.plotly_chart(fig_date)

        with col10:
          fig_date = graf_paralizacao(df_filtered)
          col10.plotly_chart(fig_date)

        with col11:
          fig_date = graf_stad_emb(df_filtered)
          col11.plotly_chart(fig_date)

        with col12:
          fig_date = graf_mov_conteiner(df_filtered)
          col12.plotly_chart(fig_date)
      #-----------------------------------------------------------------------------------------------------------------------

  with tab2:
    st.dataframe(df_filtered[['Embarcação','Agência','Navegação','Carga principal']],2000,600,hide_index=True)
  with tab3:
    
    st.subheader('INDICADORES', divider='violet')
    
    df_relatorio = pd.DataFrame(
    [
        {"INDICADORES": "Quantidade de caminhões que acessam o porto", "CENÁRIO": "Setoriais", "PERÍODO": "Mensal","DESCRIÇÃO":"------", month :17608 },
        {"INDICADORES": "Índice de movimentação de contêineres (vazios)", "CENÁRIO": "Setoriais", "PERÍODO": "Mensal","DESCRIÇÃO":"------", month :"DEZEMBRO 2023" },
        {"INDICADORES": "Cumprimento da programação de atracação","CENÁRIO": "Setoriais", "PERÍODO": "Mensal","DESCRIÇÃO":"------", month:"DEZEMBRO 2023" },
        {"INDICADORES": "Tempo de espera para atracação (dias)","CENÁRIO": "Setoriais", "PERÍODO": "Mensal","DESCRIÇÃO":"------", month :"DEZEMBRO 2023" },
        {"INDICADORES": "Cumprimento da programação de atracação","CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"------", month :"DEZEMBRO 2023" },
        
    ]
    )
    st.dataframe(df_relatorio,2000,hide_index=True)
    
    
    st.subheader('Tempo de espera para atracação por berço (dias)', divider='violet')
    df_relatorio2 = pd.DataFrame(
    [
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"101", month : "0,27" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"102", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"201", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"202", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"301", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"302", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"401", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"402", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"501", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"502", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"Rampa", month : "0,22" },
        {"CENÁRIO": "Setoriais" , "PERÍODO": "Mensal","DESCRIÇÃO":"TGL", month : "0,22" },
    ]
    )
    st.dataframe(df_relatorio2,2000,hide_index=True)
