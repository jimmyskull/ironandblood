from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Exchange, Resources, Territory, Bond
from .widgets import KnobInput

class ExchangeForm(forms.Form):
  offeror_as_bond = forms.BooleanField(label = 'As Bond?',
    initial = False, required = False,
    widget = forms.CheckboxInput(attrs = {
      'data-size': 'mini',
      'data-on-text': 'Yes',
      'data-on-color': 'warning',
      'data-off-text': 'No',
    }))
  offeree_as_bond = forms.BooleanField(initial = False, required = False,
    widget = forms.CheckboxInput(attrs = {
      'data-size': 'mini',
      'data-on-text': 'Yes',
      'data-on-color': 'warning',
      'data-off-text': 'No',
    }))

  offeror_currency = forms.IntegerField(label = 'Currency',
    widget = KnobInput(color = Resources.color('currency')))
  offeree_currency = forms.IntegerField(
    widget = KnobInput(color = Resources.color('currency')))

  offeror_manufactured = forms.IntegerField(label = 'Manufactured Goods',
    widget = KnobInput(color = Resources.color('manufactured')))
  offeree_manufactured = forms.IntegerField(
    widget = KnobInput(color = Resources.color('manufactured')))

  offeror_agricultural = forms.IntegerField(label = 'Agricultural Goods',
    widget = KnobInput(color = Resources.color('agricultural')))
  offeree_agricultural = forms.IntegerField(
    widget = KnobInput(color = Resources.color('agricultural')))

  offeror_bond = forms.IntegerField(label = 'Negotiate Bond #', required=False)
  offeree_bond = forms.IntegerField(required=False)

  def __init__(self, offeror, offeree, *args, **kwargs):
    super(forms.Form, self).__init__(*args, **kwargs)

    resource = lambda u, name: getattr(u.player.resources, name)

    self.update('offeror_currency', 'data-max',
      max(resource(offeror, 'currency'), 10) * 10)
    self.update('offeree_currency', 'data-max', resource(offeree, 'currency'))

    self.update('offeror_manufactured', 'data-max',
      max(resource(offeror, 'manufactured'), 10) * 10)
    self.update('offeree_manufactured', 'data-max',
      max(resource(offeree, 'manufactured'), 10) * 10)

    self.update('offeror_agricultural', 'data-max',
      max(resource(offeror, 'agricultural'), 10) * 10)
    self.update('offeree_agricultural', 'data-max',
      max(resource(offeree, 'agricultural'), 10) * 10)

  def update(self, field_name, attr, value):
    self.fields[field_name].widget.attrs[attr] = value

  def build_and_offer(self, offeror, offeree, id_offeror_territory,
    id_offeree_territory):
    offeror_res = Resources(
        currency = self.cleaned_data['offeror_currency'],
        agricultural = self.cleaned_data['offeror_agricultural'],
        manufactured = self.cleaned_data['offeror_manufactured'])
    offeror_res.save()
    offeree_res = Resources(
        currency = self.cleaned_data['offeree_currency'],
        agricultural = self.cleaned_data['offeree_agricultural'],
        manufactured = self.cleaned_data['offeree_manufactured'])
    offeree_res.save()

    offeror_territory = None
    if id_offeror_territory:
      offeror_territory = Territory.objects.get(name = id_offeror_territory.split(' (')[0])

    offeree_territory = None
    if id_offeree_territory:
      offeree_territory = Territory.objects.get(name = id_offeree_territory.split(' (')[0])

    offeror_bond = None
    if self.cleaned_data['offeror_bond']:
      try:
        offeror_bond = Bond.objects.get(pk=self.cleaned_data['offeror_bond'])
      except Bond.DoesNotExist:
        raise ValidationError(_("Invalid Bond number."))

    offeree_bond = None
    if self.cleaned_data['offeree_bond']:
      try:
        offeree_bond = Bond.objects.get(pk=self.cleaned_data['offeree_bond'])
      except Bond.DoesNotExist:
        raise ValidationError(_("Invalid Bond number."))

    try:
      exch = Exchange(
        offeror = offeror,
        offeror_resources = offeror_res,
        offeror_territory = offeror_territory,
        offeror_bond = offeror_bond,
        offeror_as_bond = self.cleaned_data['offeror_as_bond'],
        offeror_as_bond_maturity = 0,
        offeree = offeree,
        offeree_resources = offeree_res,
        offeree_territory = offeree_territory,
        offeree_bond = offeree_bond,
        offeree_as_bond = self.cleaned_data['offeree_as_bond'],
        offeree_as_bond_maturity = 0
        )
      exch.offer(user = offeror)
    except Exception as e:
      offeror_res.delete()
      offeree_res.delete()
      raise e
