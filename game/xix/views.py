from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

@login_required(login_url='login')
def index(request):
  return render(request, 'xix/main.html', {})

@login_required(login_url='login')
def logout_view(request):
  logout(request)
  return redirect('login')

def login_view(request):
  state = _("Please log in above.")
  alert_type = 'info'
  username = password = ''
  if request.POST:
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
      if user.is_active:
        login(request, user)
        state = _("You’re successfully logged in!")
        next = request.GET.get('next', '/')
        return redirect(next)
      else:
        state = _("Your account is not active, please contact the site admin.")
    else:
      alert_type = 'danger'
      state = _("Your username and/or password were incorrect.")
  context = {'alert_type': alert_type, 'state': state, 'username': username}
  return render_to_response('xix/auth.html', RequestContext(request, context))
