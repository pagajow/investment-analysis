from datetime import datetime
from .models import Company
from django.dispatch import receiver
from django.db.models.signals import pre_save 

# Function to update the price_updated field if the price has changed
@receiver(pre_save, sender=Company)
def update_price_updated(sender, instance, **kwargs):
    try:
        previous_instance = sender.objects.get(pk=instance.pk)  
        if previous_instance.price != instance.price:  
            instance.price_updated = datetime.now() 
    except sender.DoesNotExist:
        instance.price_updated = datetime.now() 