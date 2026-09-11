from django.http import HttpResponse
from django.shortcuts import render

from .models import MachineLearningModel

# Create your views here.

def index(request):
    course = "Machine Learning"
    days = 21
    students_info = {'name': ['A', 'B', 'C'], 'age': [20, 21, 22], 'city': ['X', 'Y', 'Z']}
    prepared_data = {
        'course': course,
        'days': days,
        'students_info': students_info
    }
    return render(request, 'machine_learning/index.html', context=prepared_data)

def view(request):
    return render(request, 'machine_learning/view.html')

def create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        MachineLearningModel.objects.create(name=name, description=description)
    machine_list = MachineLearningModel.objects.all()
    return render(request, 'machine_learning/create.html', {'machine_list': machine_list})