from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import pandas as pd

class AnalystUser(AbstractUser):
    
    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

class Company(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE, 
        related_name='companies',
        blank=False
    )
    name = models.CharField(max_length=255, blank=False)
    ticker = models.CharField(max_length=10, blank=False)
    currency = models.CharField(max_length=10, blank=False, default="USD")
    country = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    price_updated = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = (('user', 'name'), ('user', 'ticker'))
    
    def __str__(self) -> str:
        return self.name

class FinDataA(models.Model):
    '''
        YEAR "Year",
        REVENUE: "Revenue",
        NET_INCOME: "Net income",
        CASH: "cash and equivalent",
        CUR_ASSETS: "Current assets",
        NCUR_ASSETS: "Noncurrent assets",
        TOTAL_ASSETS: "Total assets",
        EQUITY: "equity",
        CUR_LIABILITIES: "Current Liabilities",
        NCUR_LIABILITIES = "Noncurrent Liabilities"
        LIABILITIES = "Total Liabilities"
        DIVIDENDS: "dividends",
        BUYBACKS: "buybacks",
        SHARES: "shares",
        PRICE: "price",
        
        ROIC = 100*(NET_INCOME/(EQUITY + NCUR_LIABILITIES))
        ROIC = 100*(EBIT/(EQUITY + LONGTERM_DEBT)) # more accurate
    '''
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='financial_data', blank=False)
    year = models.PositiveIntegerField(blank=False)
    revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    net_income = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cash = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cur_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    ncur_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    equity = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cur_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    ncur_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    dividends = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    buybacks = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    shares = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    
    class Meta:
        unique_together = ('company', 'year')  

    def __str__(self):
        return f"Financial Data for Year {self.year}"

    @staticmethod
    def getDataframe(company_id, user, sortby="year", ascending=True, exclude_fields=["company"]):
        fin_data = FinDataA.objects.filter(company_id=company_id, company__user=user)
        data_list = []
        for record in fin_data:
            data = {}
            for field in record._meta.fields:
                field_name = field.name
                if field_name not in exclude_fields:
                    field_value = getattr(record, field_name)
                    if isinstance(field, (models.DecimalField, models.IntegerField)):
                        data[field_name] = field_value if field_value is not None else None
                    else:
                        data[field_name] = field_value
            data_list.append(data)
        
        df = pd.DataFrame(data_list)
        if df.empty:
            return df
        
        df = df.sort_values(by=sortby, ascending=ascending) 

        numeric_columns = df.select_dtypes(include=['object']).columns
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        return df