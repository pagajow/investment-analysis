# Register your models here.
from django.contrib import admin
from .models import Company, FinDataA, AnalystUser, AssetNote, AssetAIReport, AssetFilter
 

@admin.register(AnalystUser)
class AnalystUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_verified') 

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'ticker', 'country', 'price', 'price_updated', 'created', 'updated', 'favorite')  
    search_fields = ('name', 'ticker', 'favorite')  

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
    
@admin.register(AssetNote)
class AssetNoteAdmin(admin.ModelAdmin):
    list_display = (
        'company', 
        'title', 
        'content', 
        'created', 
        'updated',
        'favorite'
    )
    search_fields = ('company__name', 'title', 'created','favorite')  

@admin.register(AssetAIReport)
class AssetAIReportAdmin(admin.ModelAdmin):
    list_display = (
        'company', 
        'content', 
        'created', 
    )
    search_fields = ('company__name', 'created')  

@admin.register(AssetFilter)
class AssetFilterAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'data',
        'function', 
        'periods', 
        'check_type', 
        'value1', 
        'value2', 
        'weight',
    )
    search_fields = ('user__username', 'data')  