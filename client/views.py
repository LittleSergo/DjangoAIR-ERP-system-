from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignupForm


def signup(request):
    """Signup page."""
    if request.method == 'GET':
        return render(request, 'client/signup.html', {
            'form': SignupForm
        })
    form = SignupForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(request.POST['password'])
        user.save()
        messages.success(request, 'Your account wes successfully created!')
        return redirect('client:signup')
    return render(request, 'client/signup.html', {
        'form': form
    })


def login_view(request):
    """Login page."""
    if request.method == 'GET':
        return render(request, 'client/login.html', {
            'form': AuthenticationForm
        })

    user = authenticate(request, username=request.POST['username'],
                        password=request.POST['password'])

    if user is None:
        messages.error(request, 'Username and password did not match.')
        return render(request, 'staff/login.html', {
            'form': AuthenticationForm(request.POST)
        })

    messages.success(request, f"Successfully logged in as {user.username}.")
    login(request, user)
    return redirect('client:login')


@login_required
def logout_user(request):
    """Log out user functionality.
    :param request:
    :return:
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Successfully logged out.')
        return redirect('client:login')
