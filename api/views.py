import json
import traceback
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from analysisapp.models import Company, FinDataA

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import CompanySerializer, FinDataASerializer

import pandas as pd
import numpy as np

from fundamentals.calculations import *
from fundamentals.consts import *
from fundamentals.dcf import *

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


# ViewSet dla modelu Company
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)

# ViewSet dla modelu FinDataA
class FinDataViewSet(viewsets.ModelViewSet):
    queryset = FinDataA.objects.all()
    serializer_class = FinDataASerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FinDataA.objects.filter(company__user=self.request.user)

class OverrideFinDataAView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def valueToNumber(self, value):
        if isinstance(value, str):
            if len(value.strip()) == 0 or value.strip().lower() in ["nan", "null", "none", "-"]:
                return None
            else:
                try:
                    return float(value)
                except:
                    return None
        else:
            return value
    
    
    def post(self, request, company_id):
        if not request.user.is_authenticated:
            return Response({'status': 'error', 'message': 'User not authenticated'}, status=403)
        
        data = request.data
        company = get_object_or_404(Company, id=company_id, user=request.user)
   
        try:
            valid_fields = {field.name for field in FinDataA._meta.fields if field.name != "id"}
            
            records = data.get('data', [])
            cleanRecords = []
            for record in records:
                if "year" not in record:
                    raise ValidationError("Record does not habe obligatory field 'year'!")
                cleanRecord = {k: self.valueToNumber(value=v) for k, v in record.items() if k in valid_fields}
                cleanRecord["company"] = company
                cleanRecords.append(cleanRecord)
            
            overwrite_all = bool(data.get('overwrite_all', False))
            if overwrite_all:
                FinDataA.objects.filter(company=company).delete()
            else:   
                years = [row["year"] for row in data.get('data', [])]
                FinDataA.objects.filter(company=company, year__in=years).delete()
            
            for cleanRecord in cleanRecords:
                FinDataA.objects.create(**cleanRecord)
        except Exception as e:
            Response({'status': 'error', 'message': str(e)})
        
        return Response({'status': 'success', 'redirect_url': f'/company/{company.id}/financial-data/'})

class AnalizeFinDataAView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, company_id):
        if not request.user.is_authenticated:
            return Response({'status': 'error', 'message': 'User not authenticated'}, status=403)

        try:
            company = get_object_or_404(Company, id=company_id, user=request.user)
            
            df = FinDataA.getDataframe(company_id=company_id, user=request.user, sortby="year")
            addIndicators(df)
            df_dict = df.replace({np.nan: None}).to_dict(orient='list')
    
            avr_roi = float(getAvrROI(df))
            avr_revenue_growth = float(getAvrRevenueGrowth(df))
            avr_eps_growth = float(getAvrEPSGrowth(df))
            avr_bvps_growth = float(getAvrBVPSGrowth(df))
            avr_cash_growth = float(getAvrCashGrowth(df))  
            
            curr_ratio = float(getLastCurrentRatio(df))
            debt_to_equity = float(getLastDebtToEquity(df))
            
            futureCashFlows=getFutureCashFlows(df)
            futureCashFlows = None if futureCashFlows is None else [None if value is np.nan else float(value) for value in futureCashFlows] 
         
            dcf_value, dcf_params = fairValueDCF(futureCashFlows=futureCashFlows, shares=getLastShares(df))
            
            analysis = {
                "big5": {
                    'avr_roi': {"value": avr_roi, "met": 0 if avr_roi is None else int(avr_roi > 10)},
                    'avr_revenue_growth': {"value": avr_revenue_growth, "met": 0 if avr_revenue_growth is None else int(avr_revenue_growth > 10)},
                    'avr_eps_growth': {"value": avr_eps_growth, "met": 0 if avr_eps_growth is None else int(avr_eps_growth > 10)},
                    'avr_bvps_growth': {"value": avr_bvps_growth, "met": 0 if avr_bvps_growth is None else int(avr_bvps_growth > 10)},
                    'avr_cash_growth': {"value": avr_cash_growth, "met": 0 if avr_cash_growth is None else int(avr_cash_growth > 10)},
                },
                "health": {
                    "curr_ratio": {"value": curr_ratio, "met": 0 if curr_ratio is None else int(curr_ratio > 1.5)},
                    "debt_to_equity": {"value": debt_to_equity, "met": 0 if debt_to_equity is None else int(debt_to_equity < 1)},
                },
                "dcf": {
                    "value": float(dcf_value),
                    "params": dcf_params,
                    "price": float(company.price) if company.price else None,
                    "price_updated": company.price_updated.strftime("%Y-%m-%d %H:%M:%S"),
                    "currency": company.currency,
                }
            }
            
            res = {
                'status': 'success', 
                'financial_data': df_dict,
                'analysis': analysis,
            }
            
            return Response(res, status=200)
        except Exception as e:
            res = {
                'status': 'error',
                'message': str(e),
                'details': traceback.format_exc()
            }
            return Response(res, status=500)



