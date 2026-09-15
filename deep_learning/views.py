
from django.http import HttpResponse
from django.shortcuts import redirect, render

from deep_learning.forms import ItemForm

# Create your views here.

def index(request):
    return render(request, 'deep_learning/index.html')

def view(request):
    return render(request, 'deep_learning/view.html')

def add(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/deep/view')  # Redirect to the view page after successful submission
    else:
        form = ItemForm()
    return render(request, 'deep_learning/add.html', {'form': form})
