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

    #Build a filtered DataFrame for Bernalillo County
    filtered_df = df.query('county == "Bernalillo County"')
    
    #Ensure the axis is in datetime format
    filtered_df.loc[:, ('date')] = pd.to_datetime(filtered_df.loc[:, ('date')])

    #Plot total Bernalillo cases
    sns.lineplot(x='date', y='case_count', data=filtered_df, label='Bernalillo Cases', ax=ax, lw=2)
    sns.lineplot(x='date', y='death_count', data=filtered_df, label='Bernalillo Deaths', ax=ax, lw=2)

    #Group cases and deaths by date and sum them
    #TODO: This is going to be deprecated in pandas.  
    #FutureWarning: Indexing with multiple keys (implicitly converted to a tuple of keys) will be deprecated, use a list instead.
    nm_df_casesums = (df.groupby(['date'])['case_count','death_count'].sum()).reset_index()

    #Ensure the axis is in datetime format
    nm_df_casesums.loc[:, ('date')] = pd.to_datetime(nm_df_casesums.loc[:, ('date')])

    #Plot total New Mexico cases
    sns.lineplot(x='date', y='case_count', data=nm_df_casesums, label='New Mexico Cases', ax=ax, lw=2)
    sns.lineplot(x='date', y='death_count', data=nm_df_casesums, label='New Mexico Deaths', ax=ax, lw=2)

# Function to curve fit to the data
def curve_function(x, a, b, c, d, curvetype="lnexpo"):
    #Expoential curve based on a K of 0.23, or ln(2)/(3.0) [3.0 days to double]
    if curvetype == "3poly":
        return a * (x ** 3) + b * (x ** 2) + c * x + d
    else:
        return a*np.exp(x*0.23) + b

def curve_fitter(filtered_df):

    #Extrapolate by 30 days! NOTE: This doesn't take anything else into account, like #socialdistancing
    extend = 30
    filtered_df = filtered_df.set_index(pd.DatetimeIndex(filtered_df.loc[:, ('date')]))
    df_extr = pd.DataFrame(
    data=filtered_df,
    index=pd.date_range(
        start=filtered_df.index[0],
        periods=len(filtered_df.index) + extend,
        freq=filtered_df.index.freq
    ))
    
    #Lets clean up the dataframe, since we really don't need this data.  There's probably a better way?
    if 'county' in df_extr:
        del df_extr['county']
    
    if 'date' in df_extr:
        del df_extr['date']

    #Interpolate NaN's
    df_extr.interpolate(method='nearest', xis=0, inplace=True)

    #df_extr = curve_fitter(df_extr)
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
        params = curve_fit(curve_function, x, y, guess)
        # Store optimized parameters
        col_params[col] = params[0]

    # Extrapolate each column
    for col in df_extr.columns:
        # Get the index values for NaNs in the column
        x = df_extr[pd.isnull(df_extr[col])].index.astype(float).values
        # Extrapolate those points with the fitted function
        df_extr[col][x] = curve_function(x, *col_params[col])
    
    # Put date index back
    df_extr.index = di_extr
    return (df_extr)

def plotCountyExtrapolatedData(df, county='Bernalillo County'):

    #Build a filtered DataFrame for Bernalillo County
    filtered_df = df.query('county == "' + county +'"')
    #filtered_df = df.loc([df.county == county])

    #Ensure the axis is in datetime format
    filtered_df.loc[:, ('date')] = pd.to_datetime(filtered_df.loc[:, ('date')])
    
    #Extrapolate and curve fit for exponential growth
    df_extr = curve_fitter(filtered_df)

    #Plot total Bernalillo cases
    sns.lineplot(x='index',y='case_count', data=df_extr.reset_index(), label=county + ' Cases', ax=ax, lw=2, legend=False)
    #sns.lineplot(x='index',y='death_count', data=df_extr.reset_index(), label=county + ' Deaths', ax=ax, lw=2)


def plotStateExtrapolatedData(df):

    #Group cases and deaths by date and sum them
    nm_df_casesums = (df.groupby(['date'])['case_count','death_count'].sum()).reset_index()

    #Ensure the axis is in datetime format
    nm_df_casesums.loc[:, ('date')] = pd.to_datetime(nm_df_casesums.loc[:, ('date')])

    #Extrapolate and curve fit for exponential growth
    nm_df_casesums = curve_fitter(nm_df_casesums)

    #Plot total New Mexico cases
    sns.lineplot(x='index', y='case_count', data=nm_df_casesums.reset_index(), label='New Mexico Cases', ax=ax, lw=2)
    #sns.lineplot(x='index', y='death_count', data=nm_df_casesums.reset_index(), label='New Mexico Deaths', ax=ax, lw=2)

fig, ax = plt.subplots(figsize=(14,8))

#Plot lines in seaborn for all of the counties in the Dataframe
for county in readCaseData().county.unique():
    plotCountyExtrapolatedData(readCaseData(), county)

plotStateExtrapolatedData(readCaseData())

plt.ylabel('Count (People)', fontsize=14)
plt.xlabel('Date', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=10, loc='best', ncol=2)
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d'))
plt.show()