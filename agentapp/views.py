
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView, View,  CreateView, UpdateView

from agentapp.agent import CompanyResearchAgent
from analysisapp.models import Company, FinDataA, VerificationToken, AssetAIReport
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, StreamingHttpResponse

import json
import bleach
import html
import time
import pandas as pd


class AIResearchView(LoginRequiredMixin, View):
    template_name = 'agentapp/airesearch.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        user_companies = user.companies.all()
        preselected_company_id = kwargs.get('company_id')
        return render(request, self.template_name, {
            'user_companies': user_companies,
            'preselected_company_id': preselected_company_id
        })


    def post(self, request, *args, **kwargs):
        company_id = request.POST.get("company_id")
        query = request.POST.get("query")
        user = request.user

        if not company_id:
            return JsonResponse({"error": "No company selected."}, status=400)

        uploaded_files = request.FILES.getlist("file")
        if len(uploaded_files) > 10:
            return JsonResponse({"error": "You can upload up to 10 files."}, status=400)

        agent = CompanyResearchAgent(user, company_id, query, uploaded_files)
        results = agent.generateReport()
        report_content = results.get("report")
        errors = results.get("errors", [])

        if results.get("success", False):
            report = AssetAIReport.objects.create(
                company_id=company_id,
                content=report_content,
            )
            report_url = reverse("assetaireport_detail", kwargs={"company_id": company_id, "pk": report.pk})
            
            return JsonResponse({"redirect": report_url, "results": results})
        else:
            return JsonResponse({"error": results.get("\n\n".join(errors), "Processing failed"), "status": "failed", "results": results})


        
# Create your views here.
class AskAIView(LoginRequiredMixin, View):
    template_name = 'agentapp/askai.html'
    
    def get(self, request, *args, **kwargs):  
        user = request.user     
        
        company_id = kwargs.get('company_id')
        if company_id:
            company = get_object_or_404(Company, id=company_id, user=user)  
        else:
            company = None
            
        context = {
            'company': company, 
            'user': user,
            "is_openai_api_key": bool(user.openai_api_key),
            "is_google_api_key": bool(user.google_api_key),
            "is_google_cse_id": bool(user.google_cse_id),
        }
        return render(request, self.template_name, context)
  