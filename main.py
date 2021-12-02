import time

import streamlit as st
import webbrowser
import pandas as pd
import numpy as np
import openpyxl
import plotly_express as px

st.set_page_config(page_title='Boards Built to Date',
                   page_icon=':bar_chart:',
                   layout='wide'
)

st.title('SS22 Surf Production')

df = pd.read_excel(r'S:\Purchasing\App\SS22 Built to Date.xlsx')
grades = [
    (df['Record Type'] == 'R1'),
    (df['Label'] == 'BGRADE'),
    (df['Record Type'] == 'R2') & (df['Label'] != 'BGRADE')
]
results = ['A', 'B', 'Kill']
df['Grade'] = np.select(grades, results)
df = df[df['Grade'] != 'Kill']


def load_fcst(df_fcst):
    df_fcst = pd.read_excel(r'S:\Purchasing\App\SS22 Forecast.xlsx')
    return df_fcst


df_fcst = load_fcst('df_fcst')

#df_fcst = pd.read_excel(r'S:\Purchasing\App\SS22 Forecast.xlsx')

total_built = int(df['Order Qty'].sum())
total_fcst = int(df_fcst['Global Fcst'].sum())
left_to_build = total_fcst - total_built

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader('Total Built All Models:')
    st.subheader(total_built)
    if st.checkbox('View Production Receipts:'):
        df_all = st.dataframe(df)
with middle_column:
    st.subheader('Total Forecast')
    st.subheader(total_fcst)
    if st.checkbox('View Forecast'):
        st.dataframe(df_fcst)
with right_column:
    st.subheader('Left to Build:')
    st.subheader(left_to_build)

latest_iteration = st.empty()
bar = st.progress(0)
num = 100
value = int(total_built/total_fcst*100)
for i in range(num):
    latest_iteration.text(f'{value} % Complete')
    bar.progress(total_built / total_fcst)

st.sidebar.header('Select a Model:')

model = st.sidebar.selectbox('Select Model:', df['Style Name'].unique())

df = df.loc[(df['Style Name'] == model)]
df_fcst = df_fcst.loc[(df_fcst['FW22-23 Description'] == model)]

dim = st.sidebar.selectbox("Select Size:", df['Dm/Pk'].unique())

df = df.loc[(df['Dm/Pk'] == dim)]
df_fcst = df_fcst.loc[(df_fcst['Dm/Pk'] == dim)]

built_by_model = int(df['Order Qty'].sum())
fcst_by_model = int(df_fcst['Global Fcst'].sum())
left_to_build_by_model = fcst_by_model - built_by_model

st.markdown('***')

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader('Total Built Selected Model:')
    st.subheader(built_by_model)
    if st.checkbox('View Production Receipts by Model'):
        st.dataframe(df)
with middle_column:
    st.subheader('Forecast by Model:')
    st.subheader(fcst_by_model)
    if st.checkbox('View Forecast by Model'):
        st.dataframe(df_fcst)
with right_column:
    st.subheader('Left to Build:')
    st.subheader(left_to_build_by_model)

latest_iteration = st.empty()
bar = st.progress(0)
num = 100
value = int(built_by_model/fcst_by_model*100)
for i in range(num):
    latest_iteration.text(f'{value} % Complete')
    bar.progress(built_by_model / fcst_by_model)

st.markdown('***')

total_built_graph = pd.read_excel(r'S:\Purchasing\App\SS22 Built to Date.xlsx')
total_built_graph = total_built_graph.groupby(by=['Style Name']).sum()[['Order Qty']]
total_fcst_graph = pd.read_excel(r'S:\Purchasing\App\SS22 Forecast.xlsx')
total_fcst_graph = total_fcst_graph.groupby(by=['FW22-23 Description']).sum()[['Global Fcst']]

left_column, right_column = st.columns(2)
with left_column:
    graph = px.bar(
        total_built_graph,
        x='Order Qty',
        y=total_built_graph.index,
        orientation='h',
        title='<b>Total Built by Model<b>',
        color_discrete_sequence=['#0083B8'] * len(total_built_graph),
        template='plotly_white',
        )
    graph.update_layout(height=800)
    st.plotly_chart(graph, height=800)
with right_column:
    graph2 = px.bar(
        total_fcst_graph,
        x='Global Fcst',
        y=total_fcst_graph.index,
        orientation='h',
        title='<b>Total Forecast by Model<b>',
        color_discrete_sequence=['#0083B8'] * len(total_built_graph),
        template='plotly_white',
        )
    graph2.update_layout(height=800)
    st.plotly_chart(graph2, height=800)

st.markdown('***')


@st.cache(allow_output_mutation=True)
def bom_load():
    df_bom2 = pd.read_excel(r'S:\Purchasing\App\SS22 BOM.xlsx')
    return df_bom2


df_bom = bom_load()
#df_bom = pd.read_excel(r'S:\Purchasing\App\SS22 BOM.xlsx')
key = ['Style', 'Color', 'Dm/Pk']
df_bom['Key'] = df_bom['Style'] + df_bom['Color'] + df_bom['Dm/Pk']
df_fcst = pd.read_excel(r'S:\Purchasing\App\SS22 Forecast.xlsx', usecols=['Key', 'Global Fcst'])
df_bom = df_bom.merge(df_fcst, on='Key')
built_to_date = pd.read_excel(r'S:\Purchasing\App\SS22 Built to Date.xlsx',
                              usecols=['Style', 'Color', 'Dm/Pk', 'Order Qty'])
built_to_date['Key'] = built_to_date['Style'] + built_to_date['Color'] + built_to_date['Dm/Pk']
built_to_date = built_to_date.drop(columns=['Style', 'Color', 'Dm/Pk'])
built_to_date = built_to_date.groupby(by=['Key']).sum()[['Order Qty']]
df_bom = df_bom.merge(built_to_date, on='Key')
df_bom['Left to Build'] = df_bom['Global Fcst'] - df_bom['Order Qty']
df_bom['Material Need'] = df_bom['Left to Build'] * df_bom['RM Usage']
df_bom = df_bom.groupby(by=['RM Style']).sum()[['Material Need']]
if st.checkbox('Select to view raw material demand for remainder of build:'):
    st.dataframe(df_bom)

