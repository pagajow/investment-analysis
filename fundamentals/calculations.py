import pandas as pd
import numpy as np
from fundamentals.consts import *
from typing import Dict, Any, Tuple, Union, Callable

def addROI(df: pd.DataFrame):
    s = 100*df[NET_INCOME] / (df[EQUITY] + df[NCUR_LIABILITIES] - df[CASH])
    s.name = ROI
    df[ROI] = s
    return s

def addROE(df: pd.DataFrame):
    s = 100*df[NET_INCOME] / df[EQUITY]
    s.name = ROE
    df[ROE] = s
    return s
    
def addROA(df: pd.DataFrame):
    s = 100*df[NET_INCOME] / df[TOTAL_ASSETS]
    s.name = ROA
    df[ROA] = s
    return s
    
def addBVPS(df: pd.DataFrame):
    s = df[EQUITY] / df[SHARES]
    s.name = BVPS
    df[BVPS] = s
    return s
    
def addEPS(df: pd.DataFrame):
    s = df[NET_INCOME] / df[SHARES]
    s.name = EPS
    df[EPS] = s
    return s
    
def addPayout(df: pd.DataFrame):
    s = df[DIVIDENDS] + df[BUYBACKS]
    s.name = PAYOUT
    df[PAYOUT] = s
    return s

def addCurrentRatio(df: pd.DataFrame):
    s = df[CUR_ASSETS] / df[CUR_LIABILITIES]
    s.name = CUR_RATIO
    df[CUR_RATIO] = s
    return s
    
def addDebtToEquity(df: pd.DataFrame):
    s = df[TOTAL_LIABILITIES] / df[EQUITY]
    s.name = DEBT_TO_EQUITY
    df[DEBT_TO_EQUITY] = s
    return s

def addFCF(df:pd.DataFrame):
    fcf_values = []
    for i in range(1, len(df)):
        net_income = df.iloc[i][NET_INCOME]
        cash = df.iloc[i][CASH]
        capex = (df.iloc[i][CUR_ASSETS] - df.iloc[i-1][CUR_ASSETS]) + (df.iloc[i][NCUR_ASSETS] - df.iloc[i-1][NCUR_ASSETS])
        fcf = cash + net_income - capex
        fcf_values.append(fcf)
    
    fcf_values = [None] + fcf_values
    s = pd.Series(fcf_values, index=df.index, name=FCF)
    df[FCF] = s
    return s

def addNetProfitMargin(df: pd.DataFrame):
    s = df[NET_INCOME] / df[REVENUE]
    s.name = NET_PROFIT_MARGIN
    df[NET_PROFIT_MARGIN] = s
    return s
def addDebtRatio(df: pd.DataFrame):
    s = df[TOTAL_LIABILITIES] / df[TOTAL_ASSETS]
    s.name = DEBT_RATIO
    df[DEBT_RATIO] = s
    return s
def addEquityRatio(df: pd.DataFrame):
    s = df[EQUITY] / df[TOTAL_ASSETS]
    s.name = EQUITY_RATIO
    df[EQUITY_RATIO] = s
    return s
def addEquityRatio(df: pd.DataFrame):
    s = df[EQUITY] / df[TOTAL_ASSETS]
    s.name = EQUITY_RATIO
    df[EQUITY_RATIO] = s
    return s
def addCompanyTurnover(df: pd.DataFrame):
    s = df[REVENUE] / df[TOTAL_ASSETS]
    s.name = ASSET_TURNOVER
    df[ASSET_TURNOVER] = s
    return s

def addPE(df: pd.DataFrame):
    s = df[PRICE] * df[SHARES] / df[NET_INCOME]
    s.name = PE
    df[PE] = s
    return s
def addPB(df: pd.DataFrame):
    s = df[PRICE] * df[SHARES] / df[EQUITY]
    s.name = PB
    df[PB] = s
    return s
def addPS(df: pd.DataFrame):
    s = df[PRICE] * df[SHARES] / df[REVENUE]
    s.name = PS
    df[PS] = s
    return s
def addPFCF(df: pd.DataFrame):
    s = df[PRICE] * df[SHARES] / df[FCF]
    s.name = PS
    df[PFCF] = s
    return s

def addDividentYield(df: pd.DataFrame):
    s = 100 * df[DIVIDENDS] / (df[SHARES] * df[PRICE] )
    s.name = DIVIDEND_YIELD
    df[DIVIDEND_YIELD] = s
    return s
def addDividentPayoutRatio(df: pd.DataFrame):
    s = 100 * (df[DIVIDENDS] + df[BUYBACKS]) / df[NET_INCOME]
    s.name = DIVIDEND_PAYOUT_RATIO
    df[DIVIDEND_PAYOUT_RATIO] = s
    return s

def addCashRatio(df: pd.DataFrame):
    s = df[CASH] / df[CUR_LIABILITIES] 
    s.name = CASH_RATIO
    df[CASH_RATIO] = s
    return s

def addPEGEarningsRatio(df: pd.DataFrame):
    s = df[PE] / (df[NET_INCOME].pct_change(fill_method=None) * 100)
    s.name = PEG_EARNINGS_RATIO
    df[PEG_EARNINGS_RATIO] = s
    return s
def addPEGRevenueRatio(df: pd.DataFrame):
    s = df[PE] /  (df[REVENUE].pct_change(fill_method=None) * 100)
    s.name = PEG_REVENUE_RATIO
    df[PEG_REVENUE_RATIO] = s
    return s
def addPEGEquityRatio(df: pd.DataFrame):
    s = df[PE] /  (df[EQUITY].pct_change(fill_method=None) * 100)
    s.name = PEG_EQUITY_RATIO
    df[PEG_EQUITY_RATIO] = s
    return s

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
    addNetProfitMargin(df)
    addDebtRatio(df)
    addEquityRatio(df)
    addCompanyTurnover(df)
    addPE(df)
    addPB(df)
    addPS(df)
    addPFCF(df)
    addDividentYield(df)
    addDividentPayoutRatio(df)
    addCashRatio(df)
    addPEGEarningsRatio(df)
    addPEGRevenueRatio(df)
    addPEGEquityRatio(df)
    
def get_series(column: str, df: pd.DataFrame, periods:int=10) -> Union[pd.Series, None]:
    if column not in df.columns or df[column].empty or periods < 1:
        return None
    return df[column][-periods:]

# AGREGATIONS FUNCTIONS ----------------------
def get_mean(s: Union[pd.Series, None]) -> Union[float, None]:
    return None if s is None else s.mean()
def get_median(s: Union[pd.Series, None]) -> Union[float, None]:
    return None if s is None else s.median()
def get_std(s: Union[pd.Series, None]) -> Union[float, None]:
    return None if s is None else s.std()
def get_mean_growth(s: Union[pd.Series, None]) -> Union[float, None]:
    return None if s is None else s.pct_change(fill_method=None).mean()*100
def get_median_growth(s: Union[pd.Series, None]) -> Union[float, None]:
    return None if s is None else s.pct_change(fill_method=None).median()*100
def get_std_growth(s: Union[pd.Series, None]) -> Union[float, None]:
    return None if s is None else s.pct_change(fill_method=None).std()*100

    
def cleanValue(val):
    return None if val is np.nan else val

def getAvr(df: pd.DataFrame, col: str, recentPeriods:int=10):
    if col not in df.columns or df[col].empty:
        return None
    return cleanValue(df[col][-recentPeriods:].mean())
def getAvrGrowth(df: pd.DataFrame, col: str, recentPeriods:int=10):
    if col not in df.columns or df[col].empty:
        return None
    return cleanValue(df[col][-recentPeriods:].pct_change(fill_method=None).mean()*100)
    
# ------------------------------------------------------------------

def getLastCurrentRatio(df: pd.DataFrame):
    col = CUR_RATIO
    if col not in df.columns or df[col].empty:
        return None
    x = df[col].iloc[-1]
    return cleanValue(x)
def getLastDebtToEquity(df: pd.DataFrame):
    col = DEBT_TO_EQUITY
    if col not in df.columns or df[col].empty:
        return None
    x = df[col].iloc[-1]
    return cleanValue(x)
def getLastShares(df: pd.DataFrame):
    col = SHARES
    if col not in df.columns or df[col].empty:
        return None
    x = df[col].iloc[-1]
    return cleanValue(x)