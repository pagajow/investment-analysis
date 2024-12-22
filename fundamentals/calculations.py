import pandas as pd
import numpy as np
from fundamentals.consts import *

def addROI(df: pd.DataFrame):
    s = 100*df[NET_INCOME] / (df[EQUITY] + df[NCUR_LIABILITIES] - df[CASH])
    df[ROI] = s

def addROE(df: pd.DataFrame):
    s = 100*df[NET_INCOME] / df[EQUITY]
    df[ROE] = s
    
def addROA(df: pd.DataFrame):
    s = 100*df[NET_INCOME] / df[TOTAL_ASSETS]
    df[ROA] = s
    
def addBVPS(df: pd.DataFrame):
    s = df[EQUITY] / df[SHARES]
    df[BVPS] = s
    
def addEPS(df: pd.DataFrame):
    s = df[NET_INCOME] / df[SHARES]
    df[EPS] = s
    
def addPayout(df: pd.DataFrame):
    s = df[DIVIDENDS] + df[BUYBACKS]
    df[PAYOUT] = s

def addCurrentRatio(df: pd.DataFrame):
    s = df[CUR_ASSETS] / df[CUR_LIABILITIES]
    df[CUR_RATIO] = s
    
def addDebtToEquity(df: pd.DataFrame):
    s = df[TOTAL_LIABILITIES] / df[EQUITY]
    df[DEBT_TO_EQUITY] = s

def addFCF(df:pd.DataFrame):
    fcf_values = []
    for i in range(1, len(df)):
        net_income = df.iloc[i][NET_INCOME]
        cash = df.iloc[i][CASH]
        capex = (df.iloc[i][CUR_ASSETS] - df.iloc[i-1][CUR_ASSETS]) + (df.iloc[i][NCUR_ASSETS] - df.iloc[i-1][NCUR_ASSETS])
        
        fcf = cash + net_income - capex
        fcf_values.append(fcf)
    
    df[FCF] = [None] + fcf_values
    return df
    
def addIndicators(df: pd.DataFrame):
    if df.empty:
        return
    addROI(df)
    addROE(df)
    addROA(df)
    addBVPS(df)
    addEPS(df)
    addFCF(df)
    addPayout(df)
    addCurrentRatio(df)
    addDebtToEquity(df)
    
def _returnValue(val):
    return None if val is np.nan else val
    
def getAvrROI(df: pd.DataFrame, recentPeriods=10):
    col = ROI
    if col not in df.columns or df[col].empty:
        return None
    return _returnValue(df[ROI][-recentPeriods:].mean())
def getAvrRevenueGrowth(df: pd.DataFrame, recentPeriods=10):
    col = REVENUE
    if col not in df.columns or df[col].empty:
        return None
    return _returnValue(df[col][-recentPeriods:].pct_change(fill_method=None).mean()*100)
def getAvrEPSGrowth(df: pd.DataFrame, recentPeriods=10):
    col = EPS
    if col not in df.columns or df[col].empty:
        return None
    return _returnValue(df[col][-recentPeriods:].pct_change(fill_method=None).mean()*100)
def getAvrBVPSGrowth(df: pd.DataFrame, recentPeriods=10):
    col = BVPS
    if col not in df.columns or df[col].empty:
        return None
    return _returnValue(df[col][-recentPeriods:].pct_change(fill_method=None).mean()*100)
def getAvrCashGrowth(df: pd.DataFrame, recentPeriods=10):
    col = CASH
    if col not in df.columns or df[col].empty:
        return None
    return _returnValue(df[col][-recentPeriods:].pct_change(fill_method=None).mean()*100)

def getLastCurrentRatio(df: pd.DataFrame):
    col = CUR_RATIO
    if col not in df.columns or df[col].empty:
        return None
    x = df[col].iloc[-1]
    return _returnValue(x)
def getLastDebtToEquity(df: pd.DataFrame):
    col = DEBT_TO_EQUITY
    if col not in df.columns or df[col].empty:
        return None
    x = df[col].iloc[-1]
    return _returnValue(x)
def getLastShares(df: pd.DataFrame):
    col = SHARES
    if col not in df.columns or df[col].empty:
        return None
    x = df[col].iloc[-1]
    return _returnValue(x)