from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import TodoForm
from .models import Todo


def home(request):
    template = 'todo/home.html'
    return render(request, template)


def signupuser(request):
    template = 'todo/signupuser.html'
    context = {
        'form': UserCreationForm(),
        'error': 'Password did not match',
    }
    if request.method == 'GET':
        return render(request, template, {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, template, {'form': UserCreationForm(), 'error': 'this user has already been created'})
        else:
            return render(request, template, context)


def loginuser(request):
    template = 'todo/loginuser.html'
    if request.method == 'GET':
        return render(request, template, {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, template, {'form': AuthenticationForm(), 'error': 'username or password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def currenttodos(request):
    template = 'todo/currenttodos.html'
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    context = {
        'todos': todos,
    }
    return render(request, template, context)


@login_required
def completedtodos(request):
    template = 'todo/completedtodos.html'
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    context = {
        'todos': todos,
    }
    return render(request, template, context)


@login_required
def createtodo(request):
    template = 'todo/createtodo.html'
    if request.method == 'GET':
        return render(request, template, {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, template, {'form': TodoForm(), 'error': 'VallueError'})


@login_required
def viewtodo(request, todo_pk):
    template = 'todo/viewtodo.html'
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    form = TodoForm(instance=todo)
    context = {
        'todo': todo,
        'form': form,
    }
    if request.method == 'GET':
        return render(request, template, context)
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, template, context)


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')

