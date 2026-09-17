from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'price', 'quantity', 'location', 'date', 'description']
        labels = {
            'name': 'Item Name',
            'price': 'Price',
            'quantity': 'Quantity',
            'location': 'Purchase Location',
            'date': 'Expense Date',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_price'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 1, 'id': 'id_quantity'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter purchase location'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }