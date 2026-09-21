from django import forms
from .models import Item, Lend


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


class LendForm(forms.ModelForm):
    class Meta:
        model = Lend
        fields = ['name', 'amount', 'lend_date', 'return_date', 'description']
        labels = {
            'name': 'Lender Name',
            'amount': 'Amount',
            'lend_date': 'Lend Date',
            'return_date': 'Return Date',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter lender name'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3}),
            'lend_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'return_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }        