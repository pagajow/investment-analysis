# Register your models here.
from django.contrib import admin
from .models import Company
from .models import FinDataA

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ticker', 'country', 'price', 'price_updated', 'created', 'updated')  
    search_fields = ('name', 'ticker')  


@admin.register(FinDataA)
class FinDataAAdmin(admin.ModelAdmin):
    list_display = (
        'company', 
        'year', 
        'revenue', 
        'net_income', 
        'cash', 
        'cur_assets', 
        'ncur_assets', 
        'total_assets', 
        'equity', 
        'cur_liabilities', 
        'ncur_liabilities', 
        'total_liabilities', 
        'dividends', 
        'buybacks', 
        'shares', 
        'price'
    )
    search_fields = ('company__name', 'year')  
