import json
import traceback
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from analysisapp.models import Company, FinDataA, AssetFilter

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
from analysisapp.financial_checks import get_agregation_results

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
            df = FinDataA.getDataframe(company_id=company_id, sortby="year")
            addIndicators(df)
            df_dict = df.replace({np.nan: None}).to_dict(orient='list')
       
            financial_filters = {
                "filters": []
            }
            filterDicts = AssetFilter.getUserFilters(request.user)
            
            totalScores = sum([f["weight"] for f in filterDicts])
            scores = 0
            for f in filterDicts:
                result, condition = get_agregation_results(function=f["function"],
                                                          column=f["data"],
                                                          df=df,
                                                          check_type=f["check_type"],
                                                          periods=f["periods"], 
                                                          value1=f["value1"],
                                                          value2=f["value2"],)
                f["result"] = result
                f["condition"] = condition
                financial_filters["filters"].append(f)
                if condition:
                    scores += f["weight"]
                
            financial_filters["total_scores"] = totalScores
            financial_filters["scores"] = scores
            
            res = {
                'status': 'success', 
                'financial_data': df_dict,
                'financial_filters': financial_filters,
                'company_price': company.price,
            }
            
            return Response(res, status=200)
        except Exception as e:
            res = {
                'status': 'error',
                'message': str(e),
                'details': traceback.format_exc()
            }
            return Response(res, status=500)


class DCFValuationView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def post(self, request, company_id):
        if not request.user.is_authenticated:
            return Response({'status': 'error', 'message': 'User not authenticated'}, status=403)
        try:
            df = FinDataA.getDataframe(company_id=company_id, sortby="year")
            addIndicators(df)
            
            data = request.data
            shares = int(data.get("shares", 1))
            discount_rate = float(data.get("discountRate", 0.15))
            terminal_growth_rate = float(data.get("terminalGrowthRate", 0.025))
            margin_of_safety = float(data.get("marginOfSafety", 0.5))
            future_fcf = data.get("futureCashFlows", None)
            years = data.get("years", 4)
  
            valuations_params = [
                {
                    "meta": {
                        "name": "Simple FCF Model",
                    },
                    "params": {
                        "futureCashFlows": getFutureCashFlows(df, years),
                        "shares": shares,
                        "discountRate": discount_rate,
                        "terminalGrowthRate": terminal_growth_rate,
                        "marginOfSafety": margin_of_safety,
                    },
                },
                {
                    "meta": {
                        "name": "Gordon Growth Model",
                    },
                    "params": {
                        "futureCashFlows": getFutureFCF_Gordon(df, years),
                        "shares": shares,
                        "discountRate": discount_rate,
                        "terminalGrowthRate": terminal_growth_rate,
                        "marginOfSafety": margin_of_safety,
                    },
                },
                {
                    "meta": {
                        "name": "Multivariate Model",
                    },
                    "params": {
                        "futureCashFlows": getFutureFCF_Multivariate(df, years),
                        "shares": shares,
                        "discountRate": discount_rate,
                        "terminalGrowthRate": terminal_growth_rate,
                        "marginOfSafety": margin_of_safety,
                    },
                },
            ]
            if future_fcf is not None:
                valuations_params.append(
                    {
                        "meta": {
                            "name": "Custom FCF Model",
                        },
                        "params":{
                            "futureCashFlows": future_fcf,
                            "shares": shares,
                            "discountRate": discount_rate,
                            "terminalGrowthRate": terminal_growth_rate,
                            "marginOfSafety": margin_of_safety,
                        },
                    }
                )
                
            valuations = [(fairValueDCF(**params["params"]), params["meta"] ) for params in valuations_params]
            valuations = [{**result_dict, **meta_dict} for result_dict, meta_dict in valuations if result_dict]
            
            res = {
                "status": "success",
                "company_id": company_id,
                "valuations": valuations,
            }
            
            return Response(res, status=200)
        except Exception as e:
            res = {
                'status': 'error',
                'message': str(e),
                'details': traceback.format_exc()
            }
            return Response(res, status=500)


class DownloadFinDataAView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(self, request, company_id):
        if not request.user.is_authenticated:
            return Response({'status': 'error', 'message': 'User not authenticated'}, status=403)

        try:
            company = get_object_or_404(Company, id=company_id, user=request.user)
            df = FinDataA.getDataframe(company_id=company_id, sortby="year")
            df.drop("id", axis=1, inplace=True)
            df_csv = df.to_csv(index=False)
            
            res = {
                'status': 'success', 
                'financial_data': df_csv,
            }
            return Response(res, status=200)
        except Exception as e:
            res = {
                'status': 'error',
                'message': str(e),
                'details': traceback.format_exc()
            }
            return Response(res, status=500)
        