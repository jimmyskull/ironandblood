from django import forms
from django.forms import widgets

class KnobInput(forms.TextInput):
  def __init__(self, max_value = 100, color = '#34495E', *args, **kwargs):
    kwargs['attrs'] = {'class': 'knob',
      'data-width': '80',
      'data-height': '80',
      'data-min': '0',
      'data-max': str(max_value),
      'data-displayPrevious': 'true',
      'data-angleOffset': '-100',
      'data-angleArc': '360',
      'data-rotation': 'clockwise',
      'data-fgColor': color,
      'data-step': '1',
      'value': '0'
    }
    super(forms.TextInput, self).__init__(*args, **kwargs)

