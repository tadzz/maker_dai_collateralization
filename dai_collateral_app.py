import numpy as np
import pandas as pd
import streamlit as st
import json
import requests
import plotly.express as px


@st.cache
def get_vaults_list():
    url = "https://beta.mcdstate.info/api/vaults_list"
    bearer_token = 'Cf9pZZzc?JAYQ>A'
    payload = {}
    headers = {'Authorization': 'Bearer '+ bearer_token}
    response = requests.request("GET", url, headers=headers, data = payload)
    raw_data = json.dumps(response.json()["message"]['vaults'])
    json_data = json.loads(raw_data)
    df = pd.DataFrame.from_dict(json_data)
    df['liquidation_ratio'] = df['osm_price'] / df['principal'] * 100
    df['principal_x_collateralization'] = df['principal'] * df['collateralization']
    
    df_ilk_mapping = pd.read_csv('vault_ilk - vault_ilk.csv')
    df_merged = pd.merge(df, df_ilk_mapping, 
    how="left", on=None, left_on='ilk', right_on='ilk', copy=False)
    return df_merged

@st.cache
def create_mapping():
    df_ilk_curr = df.groupby(['ilk', 'currency L1'], 
                         as_index=False).agg({'principal':sum,
                                              'osm_price':sum,
                                              'mkt_price':sum,
                                              'collateralization':'mean',
                                              'principal_x_collateralization':sum,
                                             })
    df_ilk_curr['percent'] = (df_ilk_curr['principal'] / df_ilk_curr['principal'].sum()) * 100
    df_ilk_curr['liquidation_ratio'] = df_ilk_curr['osm_price'] / df_ilk_curr['principal'] * 100
    df_ilk_curr = df_ilk_curr[df_ilk_curr['currency L1'].isin(column_show)]
    df_ilk_curr['wa_collateralization'] = df_ilk_curr['principal_x_collateralization'] / df_ilk_curr['principal']
    #df_ilk_curr['wa_collateralization'] = df_ilk_curr['wa_collateralization'].clip(upper=300)
    df_ilk_curr.sort_values(by='percent', ascending=False)
    return df_ilk_curr

column_show = ['AAVE', 
               'BAL', 
               'BAT', 
               'COMP', 
               'ETH', 
               'GUSD', 
               'KNC', 
               'LINK', 
               'LRC',
               'MANA', 
               'PAXUSD', 
               'USDC', 
               'RENBTC', 
               'TUSD', 
               'UNI', 
               'UNIV2DAIETH', 'UNIV2DAIUSDC', 'UNIV2ETHUSDT', 'UNIV2LINKETH', 'UNIV2UNIETH', 'UNIV2USDCETH', 'UNIV2WBTCETH', 
               'USDT', 
               'WBTC', 
               'YFI', 
               'ZRX'
              ]


# create df and display it
df = get_vaults_list()
st.dataframe(df.style.highlight_max(axis=0))

# create mapping and display it
df_ilk_curr = create_mapping()
st.dataframe(df_ilk_curr.style.highlight_max(axis=0))


# create sunburst chart
fig = px.sunburst(df_ilk_curr,
                  path = ['currency L1', 'ilk',], 
                  values = 'percent', 
                  title = 'DAI Collaterization',
                  #color ='wa_collateralization',
                  #color_continuous_scale = 'RdBu',
                  hover_data = {'wa_collateralization': ':,.2f',
                                'percent' : ':,.2f',
                               },
                  #range_color = [0,300]
                  #color_continuous_midpoint= 200,
                  #color_continuous_midpoint=np.average(df_ilk_curr['liquidation_ratio'], weights=df_ilk_curr['principal'])
                 )
st.plotly_chart(fig)