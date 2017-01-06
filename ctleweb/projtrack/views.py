from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect

from .forms import LoginForm

# Create your views here.

def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/home/')
            else:
                return HttpResponse("No.")
    else:
        form = LoginForm()
    return render(request, 'projtrack/index.html', {'form': form})

def home(request):
    if request.user.is_authenticated:
        return render(request, 'projtrack/home.html')
    else:
        return HttpResponseRedirect('/not_logged_in/')

def my_projects(request):
    if request.user.is_authenticated:
        return render(request, 'projtrack/my_projects.html')
    else:
        return HttpResponseRedirect('/not_logged_in/')

def all_projects(request):
    if request.user.is_authenticated:
        return render(request, 'projtrack/all_projects.html')
    else:
        return HttpResponseRedirect('/not_logged_in/')

def add_project(request):
    if request.user.is_authenticated:
        return render(request, 'projtrack/add_project.html')
    else:
        return HttpResponseRedirect('/not_logged_in/')

def not_logged_in(request):
    return render(request, 'projtrack/not_logged_in.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/index/')
