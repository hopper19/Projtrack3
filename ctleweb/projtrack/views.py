from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from .report_generator import generate_report

from .forms import AddProjectForm, AddClientForm, AddDeptForm, AddTypeForm, GenerateReportForm
from .forms import LoginForm
from .models import Client, Project, Type, Department, User

from datetime import date, datetime

def issues(request):
    return redirect('https://github.com/cyclerdan/Projtrack3/issues')


def index(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password'])
            if user is not None:
                login(request, user)
                return redirect('/projtrack3/home')
            else:
                return render(request,
                              'projtrack/index.html',
                              {'error_message': "Invalid username or password.",
                               'form': form})
    else:
        form = LoginForm()
        return render(request, 'projtrack/index.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        return render(request, 'projtrack/home.html')
    else:
        return redirect('/projtrack3/not_logged_in')


def report_page(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = GenerateReportForm(request.POST)
            if form.is_valid():
                req = {
                    'start_date': request.POST['start_date'],
                    'end_date': request.POST['end_date'],
                    'semester': request.POST['semester'],
                    'user': request.POST['user'],
                    'client': request.POST['client'],
                    'department': request.POST['department'],
                    'proj_type': request.POST['proj_type'],
                    'sort_by_date': request.POST.get('sort_by_date')
                }
                report = generate_report(req)
                return render(request, 'projtrack/report_page.html',
                        {'report': report})
        else:
            form = GenerateReportForm()
            return render(request,
                    'projtrack/form_page.html',
                    {'title_text': 'Generate a Report',
                        'form': form,
                     'form_page': '/projtrack3/report_page/'})
    else:
        return redirect('/projtrack3/not_logged_in')


def my_projects(request):
    if request.user.is_authenticated:
        try:
            projects = []
            u = User.objects.get(username=request.user.username)
            query = Project.objects.all()
            for x in query:
                if x.users.username == u.username:
                    projects.append(x)
        except ObjectDoesNotExist:
            projects = ""
        return render(request, 'projtrack/my_projects.html',
                      {'title_text': 'My Projects',
                       'projects': projects})
    else:
        return redirect('/projtrack3/not_logged_in')


def all_projects(request):
    if request.user.is_authenticated:
        projects = Project.objects.all()
        return render(request, 'projtrack/all_projects.html',
                      {'title_text': "All Projects",
                       'list_view': projects})
    else:
        return redirect('/projtrack3/not_logged_in')


def add_project(request):
    error = ""
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddProjectForm(request.POST)
            if form.is_valid():
                # Project is added to the database here.
                t = form.save()
                t.save()
                form = AddProjectForm()
            else:
                error = "Form is invalid."
        else:
            form = AddProjectForm()
        return render(request, 'projtrack/form_page.html',
                      {'title_text': "Add Project", 'form': form,
                       'form_page': "/projtrack3/add_project/",
                       'error_message': error})
    else:
        return redirect('/projtrack3/not_logged_in')


def add_client(request):
    error = ""
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddClientForm(request.POST)
            if form.is_valid():
                t = form.save()
                t.save()
                form = AddClientForm()
                error = "Form is invalid."
        else:
            form = AddClientForm()
        return render(request, 'projtrack/form_page.html',
                      {'title_text': "Add Client", 'form': form,
                       'form_page': "/projtrack3/add_client/",
                       'error_message': error})
    else:
        return redirect('/projtrack3/not_logged_in')


def client_view(request):
    if request.user.is_authenticated:
        clients = Client.objects.all()
        return render(request, 'projtrack/list_view.html',
                      {'title_text': "All Clients",
                       'list_view': clients})
    else:
        return redirect('/projtrack3/not_logged_in')


def add_department(request):
    error = ""
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddDeptForm(request.POST)
            if form.is_valid():
                d = form.save()
                d.save()
                form = AddDeptForm()
                form = AddDeptForm()
            else:
                error = "Form is invalid."
        else:
            form = AddDeptForm()
        return render(request, 'projtrack/form_page.html',
                      {'title_text': "Add Department", 'form': form,
                       'form_page': "/projtrack3/add_department/",
                       'error_message': error})
    else:
        return redirect('/projtrack3/not_logged_in')


def add_type(request):
    error = ""
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AddTypeForm(request.POST)
            if form.is_valid():
                t = form.save()
                t.save()
                form = AddTypeForm()
            else:
                error = "Form is invalid."
        else:
            form = AddTypeForm()
        return render(request, 'projtrack/form_page.html',
                      {'title_text': "Add Type", 'form': form,
                       'form_page': "/projtrack3/add_type/"})
    else:
        return redirect('/projtrack3/not_logged_in')


def not_logged_in(request):
    return render(request, 'projtrack/not_logged_in.html')


def logout_view(request):
    logout(request)
    return redirect('/projtrack3/index')
