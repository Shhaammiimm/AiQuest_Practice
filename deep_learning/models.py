from django.db import models

# Create your models here.

class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class PaymentMethod(models.IntegerChoices):
        CASH = 1, 'Cash'
        BKASH = 2, 'bKash'

    payment_method = models.IntegerField(choices=PaymentMethod.choices, default=PaymentMethod.CASH)    
    def __str__(self):
        return self.name