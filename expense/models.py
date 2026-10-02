from django.db import models
import datetime

from django.conf import settings

class Item(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='items'
    )
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



class Lend(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lends'
    )
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    lend_date = models.DateField(default=datetime.date.today, blank=True)
    return_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-lend_date', '-created_at']
        indexes = [
            models.Index(fields=['lend_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.amount} - {self.lend_date}"
    

class Borrow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='borrows'
    )
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    borrow_date = models.DateField(default=datetime.date.today, blank=True)
    return_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-borrow_date', '-created_at']
        indexes = [
            models.Index(fields=['borrow_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.amount} - {self.borrow_date}"    