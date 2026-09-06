from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def machine(request):
    return HttpResponse("Hello, this is the machine learning view.")