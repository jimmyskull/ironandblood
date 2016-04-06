from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from .models import Player, Resources, Territory, Exchange, Bond

from .forms import ExchangeForm

def build_context(request, context = {}):
  """
  Build a context dictionary with information for the base html page.
  """
  ctx = {
    'waiting_exchanges': Exchange.objects.filter(offeree = request.user,
      state = Exchange.WAITING),
    'pending_bonds': Bond.objects.filter(borrower = request.user,
      state = Bond.PENDING),
  }
  ctx.update(context)
  return ctx

@login_required(login_url='game:login')
@csrf_protect
def bonds(request, state=Bond.PENDING):
  rb = Bond.objects.filter(holder = request.user).order_by('-pk')
  sb = Bond.objects.filter(borrower = request.user).order_by('-pk')

  states = list(state)
  rb = rb.filter(state__in = states)
  sb = sb.filter(state__in = states)

  return render(request, 'game/bonds.html', build_context(request, {
    'users': User.objects.all(),
    'as_holder_bonds': rb,
    'as_borrower_bonds': sb,
    'states': states
  }))

@login_required(login_url='game:login')
def update_bond(request, bond_pk):
  if request.POST:
    pay = 'pay' in request.POST
    forgive = 'forgive' in request.POST
    valid = pay ^ forgive
    if valid:
      try:
        bond = Bond.objects.get(pk = bond_pk)
        if pay:
          bond.pay(user=request.user)
          messages.success(request, _('Bond paid!'))
        elif forgive:
          bond.forgive(user=request.user)
          messages.info(request, _('Bond forgiven.'))
        else:
          raise ValidationError(_('Unknown operation.'))
      except ValidationError as e:
        if e.params:
          messages.error(request, e.message % e.params)
        else:
          messages.error(request, e.message)
  return HttpResponseRedirect(reverse('game:bonds'))

@login_required(login_url='game:login')
def bond_by_user(request, username, state=Bond.PENDING):
  user = User.objects.get(username = username)
  users = [request.user, user]
  bonds_history = Bond.objects.filter(holder__in = users,
    borrower__in = users)

  states = list(state)
  bonds_history = bonds_history.filter(state__in = states)

  return render(request, 'game/bond_by_user.html', build_context(request, {
    'user': user,
    'bonds_history': bonds_history,
    'states': states
    }))

@login_required(login_url='game:login')
@csrf_protect
def exchanges(request, state=Exchange.WAITING):
  re = Exchange.objects.filter(offeree = request.user).order_by('-offer_date')
  se = Exchange.objects.filter(offeror = request.user).order_by('-offer_date')

  states = list(state)
  re = re.filter(state__in = states)
  se = se.filter(state__in = states)

  return render(request, 'game/exchanges.html', build_context(request, {
    'users': User.objects.all(),
    'received_exchanges': re,
    'sent_exchanges': se,
    'states': states
  }))

@login_required(login_url='game:login')
def update_exchange(request, exchange_pk):
  if request.POST:
    accept = 'accept' in request.POST
    reject = 'reject' in request.POST
    cancel = 'cancel' in request.POST
    valid = accept ^ reject ^ cancel
    if valid:
      try:
        exch = Exchange.objects.get(pk = exchange_pk)
        if accept:
          exch.accept(user=request.user)
          messages.success(request, _('Exchange accepted!'))
        elif reject:
          exch.reject(user=request.user)
          messages.info(request, _('Exchange rejected.'))
        elif cancel:
          exch.cancel(user=request.user)
          messages.info(request, _('Exchange canceled.'))
        else:
          raise ValidationError(_('Unknown operation.'))
      except ValidationError as e:
        if e.params:
          messages.error(request, e.message % e.params)
        else:
          messages.error(request, e.message)
  return HttpResponseRedirect(reverse('game:exchanges'))

@login_required(login_url='game:login')
def new_exchange(request, offeree, state=Exchange.WAITING):
  offeree_obj = User.objects.get(username = offeree)
  form = ExchangeForm(request.user, offeree_obj, request.POST or None)
  error_message = None
  if form.is_valid():
    try:
      id_offeror_territory = request.POST['id_offeror_territory']
      id_offeree_territory = request.POST['id_offeree_territory']
      resource = form.build_and_offer(request.user, offeree_obj,
        id_offeror_territory = id_offeror_territory,
        id_offeree_territory = id_offeree_territory)
    except ValidationError as e:
      if e.params:
        messages.error(request, e.message % e.params)
      else:
        messages.error(request, e.message)
    else:
      messages.success(request, _('Exchange offer sent!'))
      return HttpResponseRedirect(reverse('game:exchanges'))
  users = [request.user, offeree_obj]
  exchange_history = Exchange.objects.filter(offeror__in = users,
    offeree__in = users)

  states = list(state)
  exchange_history = exchange_history.filter(state__in = states)

  return render(request, 'game/new_exchange.html', build_context(request, {
    'form': form,
    'offeree': offeree_obj,
    'territories': Territory.objects.all(),
    'exchange_history': exchange_history,
    'states': states
    }))

@login_required(login_url='game:login')
def home(request):
  territories = Territory.objects.all()
  users = User.objects.all()
  colors = ['#659BA3', '#725E54', '#FFEBB5', '#996982', '#01704B']
  dct = dict()
  for t in territories:
    dct[t.code] = colors[t.owner.pk % len(colors)]
  user_legend = dict()
  for u in users:
    user_legend[u.username] = colors[u.pk % len(colors)]
  return render(request, 'game/home.html', build_context(request, {
    'colors': dct,
    'colors_legend': user_legend
  }))

@login_required(login_url='game:login')
def logout_view(request):
  logout(request)
  return redirect(reverse('game:login'))

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
        return redirect(request.GET.get('next', '/'))
      else:
        alert_type = 'danger'
        state = _("Your account is not active, please contact the site admin.")
    else:
      alert_type = 'danger'
      state = _("Your username and/or password were incorrect.")
  context = {'alert_type': alert_type, 'state': state, 'username': username}
  return render_to_response('game/login.html', RequestContext(request, context))

@login_required(login_url='game:login')
def profile(request):
  return render(request, 'game/home.html', {})

