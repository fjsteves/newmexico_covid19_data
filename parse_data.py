#!/usr/bin/python3

import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
import numpy as np
from lmfit.models import LorentzianModel

def readCaseData():
    path = r'./casedata' # use your path
    filename = os.path.join(os.getcwd(), path + "/nm-case-data-concat.csv")

    basedf = pd.read_csv(filename, index_col=None, header=0)

    return(basedf)

def plotData(df):

    fig, ax = plt.subplots(figsize=(10,6))

    filtered_df = df.query('county == "Bernalillo County"')
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    #print (filtered_df)

    #Total Bernco Cases
    sns.lineplot(x='date',y='case_count', data=filtered_df, label='Bernalillo Cases', ax=ax, lw=2)
    sns.lineplot(x='date',y='death_count', data=filtered_df, label='Bernalillo Deaths', ax=ax, lw=2)
    
    nm_df = df
    
    nm_df_casesums = (nm_df.groupby(['date'])['case_count'].sum()).reset_index()
    nm_df_deathsums = (nm_df.groupby(['date'])['death_count'].sum()).reset_index()

    nm_df_casesums['date'] = pd.to_datetime(nm_df_casesums['date'])
    nm_df_deathsums['date'] = pd.to_datetime(nm_df_deathsums['date'])

    nm_df_casesums = nm_df_casesums.set_index(pd.DatetimeIndex(nm_df_casesums['date']))
    
    #TODO: Create a LOG/EXPO curve.
    #startDate = '2020-03-11'
    #endDate = '2020-03-28'
    #index_hourly = pd.date_range(startDate, endDate, freq='12H')
    #nm_df_casesums_smooth = nm_df_casesums.reindex(index=index_hourly).interpolate('spline', order=4)

    #print (nm_df_casesums_smooth)

    #Total NM Cases
    #sns.lineplot(x='index' ,y='case_count', data=nm_df_casesums_smooth.reset_index(), label='New Mexico Cases', ax=ax, lw=2)
    #nm_casedates = np.array(list(range(0, 18)))

    #model = LorentzianModel()
    #params = model.guess(nm_df_casesums['case_count'], x=nm_casedates)
    #result = model.fit(nm_df_casesums['case_count'], params, x=nm_casedates)

    #print (result)
    sns.lineplot(x='date' ,y='case_count', data=nm_df_casesums, label='New Mexico Cases', ax=ax, lw=2)
    sns.lineplot(x='date',y='death_count', data=nm_df_deathsums, label='New Mexico Deaths', ax=ax, lw=2)

    plt.ylabel('Units', fontsize=14)
    plt.xlabel('Date', fontsize=14)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d'))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)
    plt.title('Covid-19 Trendlines', fontsize=16)
    plt.show()

plotData(readCaseData())
