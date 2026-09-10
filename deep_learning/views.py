
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'deep_learning/index.html')

def view(request):
    return render(request, 'deep_learning/view.html')
