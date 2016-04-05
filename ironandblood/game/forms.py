from django import forms

from .models import Exchange, Resources, Territory
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

  def __init__(self, offeror, offeree, *args, **kwargs):
    super(forms.Form, self).__init__(*args, **kwargs)

    resource = lambda u, name: getattr(u.player.resources, name)

    self.update('offeror_currency', 'data-max', resource(offeror, 'currency'))
    self.update('offeree_currency', 'data-max', resource(offeree, 'currency'))

    self.update('offeror_manufactured', 'data-max',
      resource(offeror, 'manufactured'))
    self.update('offeree_manufactured', 'data-max',
      resource(offeree, 'manufactured'))

    self.update('offeror_agricultural', 'data-max',
      resource(offeror, 'agricultural'))
    self.update('offeree_agricultural', 'data-max',
      resource(offeree, 'agricultural'))

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
    print(id_offeror_territory)
    if id_offeror_territory:
      print("name", id_offeror_territory.split(' (')[0])
      offeror_territory = Territory.objects.get(name = id_offeror_territory.split(' (')[0])

    offeree_territory = None
    if id_offeree_territory:
      offeree_territory = Territory.objects.get(name = id_offeree_territory.split(' (')[0])

    try:
      exch = Exchange(
        offeror = offeror,
        offeror_resources = offeror_res,
        offeror_territory = offeror_territory,
        offeror_bond = None,
        offeror_as_bond = False,
        offeror_as_bond_maturity = 0,
        offeree = offeree,
        offeree_resources = offeree_res,
        offeree_territory = offeree_territory,
        offeree_bond = None,
        offeree_as_bond = False,
        offeree_as_bond_maturity = 0
        )
      exch.offer(user = offeror)
    except Exception as e:
      offeror_res.delete()
      offeree_res.delete()
      raise e
