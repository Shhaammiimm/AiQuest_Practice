from django.db import models
import datetime

class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=datetime.date.today, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
        ]

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.name} - {self.date}"