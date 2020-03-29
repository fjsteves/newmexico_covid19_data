#!/usr/bin/python3

import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
import numpy as np
from scipy.optimize import curve_fit

def readCaseData():
    path = r'./casedata' # use your path
    filename = os.path.join(os.getcwd(), path + "/nm-case-data-concat.csv")

    basedf = pd.read_csv(filename, index_col=None, header=0)

    return(basedf)

def plotData(df):

    fig, ax = plt.subplots(figsize=(10,8))

    #Build a filtered DataFrame for Bernalillo County
    filtered_df = df.query('county == "Bernalillo County"')
    
    #Ensure the axis is in datetime format
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])

    #Plot total Bernalillo cases
    sns.lineplot(x='date',y='case_count', data=filtered_df, label='Bernalillo Cases', ax=ax, lw=2)
    sns.lineplot(x='date',y='death_count', data=filtered_df, label='Bernalillo Deaths', ax=ax, lw=2)

    #Group cases and deaths by date and sum them
    nm_df_casesums = (df.groupby(['date'])['case_count'].sum()).reset_index()
    nm_df_deathsums = (df.groupby(['date'])['death_count'].sum()).reset_index()
    
    #Ensure the axis is in datetime format
    nm_df_casesums['date'] = pd.to_datetime(nm_df_casesums['date'])
    nm_df_deathsums['date'] = pd.to_datetime(nm_df_deathsums['date'])

    #Plot total New Mexico cases
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
# Function to curve fit to the data
def func(x, a, b, c, d):
    #This produces a 3 poly fit
    #return a * (x ** 3) + b * (x ** 2) + c * x + d
    #Expoential curve based on a K of 0.23, or ln(2)/(3.0) [3.0 days to double]
    return a*np.exp(x*0.23) + b


def plotExtrapolatedData(df):

    fig, ax = plt.subplots(figsize=(10,8))

    #Build a filtered DataFrame for Bernalillo County
    filtered_df = df.query('county == "Bernalillo County"')
    
    #Ensure the axis is in datetime format
    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
    
    #Extrapolate!

    extend = 25
    filtered_df = filtered_df.set_index(pd.DatetimeIndex(filtered_df['date']))
    df_extr = pd.DataFrame(
    data=filtered_df,
    index=pd.date_range(
        start=filtered_df.index[0],
        periods=len(filtered_df.index) + extend,
        freq=filtered_df.index.freq
    ))
    
    del df_extr['county']
    del df_extr['date']

    df_extr.interpolate(method='nearest', xis=0, inplace=True)

    #Record the index before we drop it for adding back later
    di_extr = df_extr.index
    df_extr = df_extr.reset_index().drop('index', 1)
    
    # Initial parameter guess, just to kick off the optimization
    guess = (0.5, 0.5, 0.5, 0.5)

    # Create copy of data to remove NaNs for curve fitting
    fit_df = df_extr.dropna()

    # Place to store function parameters for each column
    col_params = {}

    # Curve fit each column
    for col in fit_df.columns:
        # Get x & y
        x = fit_df.index.astype(float).values
        y = fit_df[col].values
        # Curve fit column and get curve parameters
        params = curve_fit(func, x, y, guess)
        # Store optimized parameters
        col_params[col] = params[0]

    # Extrapolate each column
    for col in df_extr.columns:
        # Get the index values for NaNs in the column
        x = df_extr[pd.isnull(df_extr[col])].index.astype(float).values
        # Extrapolate those points with the fitted function
        df_extr[col][x] = func(x, *col_params[col])
    
    # Put date index back
    df_extr.index = di_extr

    print (df_extr)

    #Plot total Bernalillo cases
    sns.lineplot(x='index',y='case_count', data=df_extr.reset_index(), label='Bernalillo Cases', ax=ax, lw=2)
    sns.lineplot(x='index',y='death_count', data=df_extr.reset_index(), label='Bernalillo Deaths', ax=ax, lw=2)

    plt.ylabel('Units', fontsize=14)
    plt.xlabel('Date', fontsize=14)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d'))
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)
    plt.title('Covid-19 Trendlines', fontsize=16)
    plt.show()

plotExtrapolatedData(readCaseData())
