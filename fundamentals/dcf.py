from typing import Dict, List, Union
import numpy as np
import pandas as pd
from .utils import *

from fundamentals.consts import *

from statsmodels.tsa.holtwinters import Holt
from statsmodels.tsa.arima.model import ARIMA

from numpy.polynomial.polynomial import polyfit, polyval
from sklearn.linear_model import LinearRegression


# MY PREDICTIONS: ---------------------------------
def getFutureCashFlows(df: pd.DataFrame, years=4):
        if df.empty or REVENUE not in df.columns or NET_INCOME not in df.columns or FCF not in df.columns:
            return None
        revenue = df[REVENUE]
        net_income = df[NET_INCOME]
        fcf = df[FCF]
        
        aver_net_income_margin = (net_income/revenue).mean()
        aver_net_income_to_fcf = (net_income/fcf).mean()
            
        # approximation 
        future_revenue = np.array(predict_linearreg(values=revenue.values, years=years))
        future_net_income = aver_net_income_margin * future_revenue
        future_fcf = future_net_income/aver_net_income_to_fcf  
        
        return None if np.isnan(future_fcf).any() else future_fcf 

def getFutureFCF_Gordon(df: pd.DataFrame, years=4):
    if df.empty or FCF not in df.columns:
        return None
    
    fcf_series = df[FCF].dropna()
    if len(fcf_series) < 2:
        return None

    growth_rates = fcf_series.pct_change().dropna()
    median_growth = np.median(growth_rates)
    
    last_fcf = fcf_series.iloc[-1]
    future_fcf = [last_fcf * (1 + median_growth) ** i for i in range(1, years + 1)]
    
    return np.array(future_fcf) if not np.isnan(future_fcf).any() else None


def getFutureFCF_Multivariate(df: pd.DataFrame, years=4):
    try:
        if df.empty or FCF not in df.columns or REVENUE not in df.columns or NET_INCOME not in df.columns:
            return None

        df_filtered = df.dropna(subset=[FCF, REVENUE, NET_INCOME])

        fcf_series = df_filtered[FCF]
        revenue_series = df_filtered[REVENUE]
        net_income_series = df_filtered[NET_INCOME]

        if len(fcf_series) < 2 or len(revenue_series) < 2 or len(net_income_series) < 2:
            return None

        X = np.column_stack([revenue_series.values, net_income_series.values])
        y = fcf_series.values

        model = LinearRegression()
        model.fit(X, y)

        future_revenue = np.array(predict_linearreg(values=revenue_series.values, years=years))
        future_net_income = np.array(predict_linearreg(values=net_income_series.values, years=years))
        future_X = np.column_stack([future_revenue, future_net_income])

        future_fcf = model.predict(future_X)

        return np.array(future_fcf) if not np.isnan(future_fcf).any() else None
    except Exception as e:
        print(str(e))
        return None

#-----------------------------------------------------------------------------
def fairValueDCF(futureCashFlows: list, 
                 shares: int, 
                 discountRate: float = 0.15, 
                 terminalGrowthRate: float = 0.025,
                 marginOfSafety:float=0.5) -> Dict[str, Union[float, List[float], None]]:
    """
    DCF (Discounted Cash Flow)
    :param futureCashFlows: List of projected cash flows for each year
    :param discountRate: Discount rate
    :param terminalGrowthRate: Terminal growth rate
    :return: Calculates the fair value of the company
    """
    if futureCashFlows is None or shares is None:
        return None
    else:
        # Variable to store the total value of discounted cash flows
        value = 0
        shares = int(shares)
        terminal_years = len(futureCashFlows)

        # Step 1: Calculate the future cash flows for each year
        for i in range(len(futureCashFlows)):
            # Cash flows are discounted to present value
            discounted_cash_flow = futureCashFlows[i] / ((1 + discountRate) ** (i + 1))
            value += discounted_cash_flow

        # Step 2: Calculate the terminal value (i.e., the value of cash flows beyond the forecast period)
        # The terminal value is calculated based on the last projected cash flow, the growth rate, and the discount rate.
        terminal_value = (futureCashFlows[-1] * (1 + terminalGrowthRate)) / (discountRate - terminalGrowthRate)

        # Step 3: Discount the terminal value to present value and add it to the total value
        # The terminal value is recalculated to today's value and then added to the discounted cash flows.
        discounted_terminal_value = terminal_value / ((1 + discountRate) ** terminal_years)
        value += discounted_terminal_value       
        fairPrice = value / shares
        buyPrice = fairPrice * marginOfSafety

    return {
        "fair_price": fairPrice,
        "buy_price": buyPrice,
        "discount_rate": round(100 * discountRate,1),
        "terminal_growth_rate": round(100 * terminalGrowthRate, 1),
        "years": None if futureCashFlows is None else len(futureCashFlows),
        "shares": shares,
        "future_fcf": futureCashFlows,
        "margin_of_safety": round(100 * marginOfSafety,1),
    }
