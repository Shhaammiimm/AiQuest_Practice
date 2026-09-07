
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return HttpResponse("Hello, this is the deep learning view.")

def say_hello(request):
    return HttpResponse("Hello from the deep learning app!")