from typing import List
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import pandas as pd
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from .financial_checks import CHECKS_CONFIG

class AnalystUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_api_key = models.CharField(max_length=255, blank=True, null=True)
    google_cse_id = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.username} ({self.email})"
    
class VerificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"    


class Company(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE, 
        related_name='companies',
        blank=False
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    ticker = models.CharField(max_length=10, blank=False)
    description = models.TextField(null=True)
    currency = models.CharField(max_length=10, blank=False, default="USD")
    country = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    price_updated = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_company = models.BooleanField(default=True)
    favorite = models.BooleanField(default=False)
    
    
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
    def getDataframe(company_id, sortby="year", ascending=True, exclude_fields=["company"]) -> pd.DataFrame:
        fin_data = FinDataA.objects.filter(company_id=company_id)
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
    
class AssetNote(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notes', blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=False)
    content = models.TextField()
    favorite = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title}"

    @staticmethod
    def getNotes(company_id) -> list:
        notes = AssetNote.objects.filter(company_id=company_id).order_by('created').values('title', 'content', 'created')
        return [dict(note) for note in notes]

class FinReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE, 
        related_name='reports',
        blank=False
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, blank=False)
    content = models.TextField()
    favorite = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title}"


class AssetFilter(models.Model):
    CHECK_TYPE_CHOICES = [
        ('above', 'above'),
        ('below', 'below'),
        ('range', 'range'),
        ('beyond ', 'beyond '),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE, 
        related_name='assetfilters',
        blank=False,
        null=False
    )
    function = models.CharField(
        max_length=255, 
        null=False, 
        blank=False,
        choices=[(v,v.upper().replace("_", " ")) for v in CHECKS_CONFIG["function"]],
        default=CHECKS_CONFIG["function"][0],
        )
    data = models.CharField(
        max_length=255, 
        null=False, 
        blank=False,
        choices=[(v,v.upper().replace("_", " ")) for v in CHECKS_CONFIG["data"]],
        default=CHECKS_CONFIG["data"][0],
        )
    periods = models.IntegerField(
        null=False, 
        blank=False, 
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        )
    check_type = models.CharField(
        max_length=16, 
        choices=[(v,v.upper().replace("_", " ")) for v in CHECKS_CONFIG["check_type"]],
        blank=False,
        null=False,
        default=CHECKS_CONFIG["check_type"][0],
    )
    value1 = models.FloatField(null=False, blank=True, default=0)
    value2 = models.FloatField(null=False, blank=True, default=0)
    weight = models.IntegerField(
        null=False, 
        blank=False, 
        default=1,
        validators=[MinValueValidator(1)],
        )
    
    class Meta:
        unique_together = ('user', 'function', 'data')  
    
    def __str__(self):
        return f"{self.data} {self.function}"
    
    def clrearUnsupportedFunctions(functionNames: List[str]):
        AssetFilter.objects.exclude(function__in=functionNames).delete()
        
    def toDict(self):
        return {"function": self.function, 
                "data": self.data, 
                "periods": self.periods, 
                "check_type": self.check_type, 
                "value1": self.value1, 
                "value2": self.value2, 
                "weight": self.weight}
        
    @staticmethod
    def getUserFilters(user):
        return [af.toDict() for af in AssetFilter.objects.filter(user=user)]
    
        