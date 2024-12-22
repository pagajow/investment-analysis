import numpy as np
import pandas as pd
from .utils import *

from fundamentals.consts import *

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

def fairValueDCF(futureCashFlows: list, shares: int, discountRate: float = 0.15, terminalGrowthRate: float = 0.025):
    """
    DCF (Discounted Cash Flow)
    :param futureCashFlows: List of projected cash flows for each year
    :param discountRate: Discount rate
    :param terminalGrowthRate: Terminal growth rate
    :return: Calculates the fair value of the company
    """
    if futureCashFlows is None or shares is None:
        valuePerShare = None
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
        valuePerShare = value / shares
        

    params = {
        "discount_rate": round(100 * discountRate,1),
        "terminal_growthRate": round(100 * terminalGrowthRate, 1),
        "years": None if futureCashFlows is None else len(futureCashFlows),
        "shares": shares,
        "future_fcf": futureCashFlows
    }
    return valuePerShare, params
