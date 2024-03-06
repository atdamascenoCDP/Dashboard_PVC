#%%writefile app.py
from logging import PlaceHolder
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit.elements import plotly_chart
import plotly.graph_objects as go
import re


#Carregando Dados e Ajuste
@st.cache_data
def Load_dados(endereco):
  #df = pd.read_excel(endereco, sheet_name='1ª planilha')
  df = pd.read_csv(endereco)

  df["Horário desatracação"] = pd.to_datetime(df['Horário desatracação'], format="%d/%m/%Y %H:%M")
  df["Horário atracação"] = pd.to_datetime(df['Horário atracação'], format="%d/%m/%Y %H:%M")
  df["Horário chegada no porto"] = pd.to_datetime(df['Horário chegada no porto'], format="%d/%m/%Y %H:%M")
  df["Horário início operação"] = pd.to_datetime(df['Horário início operação'], format="%d/%m/%Y %H:%M")
  df["Horário término da operação"] = pd.to_datetime(df['Horário término da operação'], format="%d/%m/%Y %H:%M")
 

  df['Peso da carga movimentada (t)'] = df['Peso da carga movimentada (t)'].apply(lambda x: float(x.replace(".","").replace(",",".")))
  df["Mes"]= df["Horário desatracação"].apply(lambda x: str(x.year) + "-" + str(x.month))
  df.loc[df["Carga principal"] == "COQUE DE PETRÓLEO, BETUME DE PETRÓLEO E OUTROS RESÍDUOS DOS ÓLEOS DE PETRÓLEO","Carga principal"] = "COQUE"
  df["Berço"] = df["Berço"].astype(str)
  df = df.rename(columns={'Soma do tempo de operação paralisada': 'Paralisação'})
  df['Paralisação'] = df['Paralisação'].apply(lambda x: float(x.replace(",",".")))
  df["Qtd. de carga movimentada (un.)"] = df["Qtd. de carga movimentada (un.)"].astype(str)
  df["Tempo de Atracação"] = df["Horário desatracação"] - df["Horário atracação"]
  df['Tempo Operando'] = df['Horário término da operação'] - df['Horário início operação']
  df['Tempo Atracado'] = df['Horário desatracação'] - df['Horário atracação']

  return df

def convert_google_sheet_url(url):
  # Regular expression to match and capture the necessary part of the URL
  pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

  # Replace function to construct the new URL for CSV export
  # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
  replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

  # Replace using regex
  new_url = re.sub(pattern, replacement, url)

  return new_url

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
url = 'https://docs.google.com/spreadsheets/d/1nHv38Vp7VcH5Ut4fp90eBXAW2siUwwvZCPt8WKwFDP4/edit#gid=704208139'

new_url = convert_google_sheet_url(url)
df = Load_dados(new_url)

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
    st.dataframe(df_filtered[['Embarcação','Agência','Navegação','Carga principal']],1000,hide_index=True)
  with tab3:
    col1_tab3, col2_tab3 = st.columns(2)
    col3_tab3, col4_tab3 = st.columns(2)
    col5_tab3, col6_tab3 = st.columns(2)
    
    with col1_tab3:
      st.subheader('Indicadores', divider='violet')
      df_relatorio2 = pd.DataFrame(
      [
          {"": "Quantidade de caminhões que acessam o porto" , month: "Mensal" },
          {"": "Índice de movimentação de contêineres (vazios)" , month: "Mensal" },
          {"": "Cumprimento da programação de atracação" , month: "Mensal" },
          {"": "Tempo de espera para atracação (dias)" , month: "Mensal" },
          
      ]
      )
      st.dataframe(df_relatorio2,700,hide_index=True)

    with col2_tab3:
      st.subheader('Tempo de espera para atracação  ('+ month +')', divider='violet')
      df_espera_berco = df_filtered.groupby('Berço').agg({'Horário chegada no porto':'mean','Horário atracação':'mean'}).reset_index()
      df_espera_berco['Média'] = df_espera_berco['Horário chegada no porto'] - df_espera_berco['Horário atracação']
          
      st.dataframe(df_espera_berco[['Berço','Média']],700,460,hide_index=True)

      #---------------------------------------------------------------------------------------------------------------------------
    with col3_tab3:
      st.subheader('Capacidade Instalada  ('+ month +')', divider='violet')
      url = 'https://docs.google.com/spreadsheets/d/1PKaF2Ah5HaGEY2EK0lyJ7oomtg2NV3Z0vkhakGn0ld0/edit#gid=853419680'
      url_convertida = convert_google_sheet_url(url)
      df_capacidade = pd.read_csv(url_convertida)
      df_capacidade['CAPACIDADE (T/ANO)'] = df_capacidade['CAPACIDADE (T/ANO)'].apply(lambda x: float(x.replace(".","").replace(",",".")))
      df_resultado = df_filtered.groupby('Carga principal')[['Peso da carga movimentada (t)']].sum().reset_index()
      df_resultado2 = pd.merge(df_resultado, df_capacidade, left_on='Carga principal', right_on='Carga principal')
      df_resultado2['CAPACIDADE %'] = df_resultado2['Peso da carga movimentada (t)']/df_resultado2['CAPACIDADE (T/ANO)']*100
      #.round(2)
      st.dataframe(df_resultado2[['Carga principal','CAPACIDADE %']],700,460,hide_index=True)

    with col4_tab3:      
      #---------------------------------------------------------------------------------------------------------------------------
      st.subheader('Estadia de Navios/Dia  ('+ month +')', divider='violet')
      df_estadia_carga = df_filtered.groupby('Carga principal').agg({'Horário chegada no porto':'mean','Horário desatracação':'mean'}).reset_index()
      df_estadia_carga['Estadia'] = df_estadia_carga['Horário chegada no porto'] - df_estadia_carga['Horário desatracação']
            
      st.dataframe(df_estadia_carga[['Carga principal','Estadia']],700,460,hide_index=True)

    with col5_tab3:
      #---------------------------------------------------------------------------------------------------------------------------
      st.subheader('Produtividade de Operador(tons/dia)  ('+ month +')', divider='violet')
      df_prod_op = df_filtered.groupby('Operador').agg({'Tempo Operando':'mean'}).reset_index()
            
      st.dataframe(df_prod_op,700,600,hide_index=True)
    
    with col6_tab3:
      #---------------------------------------------------------------------------------------------------------------------------
      st.subheader('Taxa de Ocupação por Berço  ('+ month +')', divider='violet')
      df_ocupa_berco = df_filtered.groupby('Berço').agg({'Tempo Atracado':'sum'}).reset_index()
      df_ocupa_berco['Tempo Atracado'] = df_ocupa_berco['Tempo Atracado'].apply(lambda x: x.days)
      df_ocupa_berco['Média %'] = df_ocupa_berco['Tempo Atracado'] / 31 *100
      df_ocupa_berco['Média %'] = df_ocupa_berco['Média %'].round(2)
      st.dataframe(df_ocupa_berco[['Berço','Média %']],700,460,hide_index=True)
