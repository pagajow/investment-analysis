from django.urls import path
import agentapp.views as views

app_name = "agentapp"

urlpatterns = [
    path('company/<int:company_id>/chat-ai/', views.AskAIView.as_view(), name='company_chat_ai'), 
    path('chat-ai/', views.AskAIView.as_view(), name='chat_ai'), 
    path('ai-research/', views.AIResearchView.as_view(), name='ai_research'),
    path('ai-research/company/<int:company_id>/', views.AIResearchView.as_view(), name='ai_research_company'),
] 

