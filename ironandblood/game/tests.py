# vim: ai ts=2 sts=2 et sw=2
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from game.models import Charter, Exchange, Player, Territory, Resources

def create_test_game():
  usernames = ['arthur', 'brian', 'blacknight', 'caesar', 'dickens', 'eric',
      'francesc', 'gumby', 'herbert', 'kigarthur', 'lancelot', 'patsy',
      'itsman','loony', 'nazifish', 'pepperpot']
  for name in usernames:
    user = User.objects.create_user(username=name)
    Player.create_player(user=user).save()

  territories = ['Aglax', 'Brierhiel', 'Cesta', 'Drucea', 'Efea', 'Froynia',
      'Gleol', 'Ova', 'Loflurg', 'Prainia', 'Qogrela', 'Smea', 'Uglia']
  for territory_name in territories:
    Territory.objects.create(name=territory_name, land_area=10)

class PlayerTestCase(TestCase):
  def setUp(self):
    create_test_game()
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')

    # Arthur owns Aglax
    aglax = Territory.objects.get(name='Aglax')
    aglax.owner = arthur
    aglax.save()

    # Arthur allows Dickens to work in 10% of the Aglax' land area
    Charter.objects.create(territory=aglax, member=dickens, size=10)

  def test_player_role(self):
    arthur = User.objects.get(username='arthur')
    self.assertFalse(arthur.player.is_privateer())
    self.assertFalse(arthur.player.is_chartered_company())
    self.assertTrue(arthur.player.is_head_of_state())

    brian = User.objects.get(username='brian')
    self.assertTrue(brian.player.is_privateer())
    self.assertFalse(brian.player.is_chartered_company())
    self.assertFalse(brian.player.is_head_of_state())

    dickens = User.objects.get(username='dickens')
    self.assertFalse(dickens.player.is_privateer())
    self.assertTrue(dickens.player.is_chartered_company())
    self.assertFalse(dickens.player.is_head_of_state())

class CharterTestCase(TestCase):
  def setUp(self):
    create_test_game()
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')

    # Arthur controls Aglax
    aglax = Territory.objects.get(name='Aglax')
    aglax.owner = arthur
    aglax.save()

  def test_charter_grant(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')
    lancelot = User.objects.get(username='lancelot')

    aglax = Territory.objects.get(name='Aglax')

    self.assertTrue(arthur.player.is_head_of_state())
    self.assertTrue(dickens.player.is_privateer())
    self.assertTrue(lancelot.player.is_privateer())

    with self.assertRaisesRegexp(ValidationError,
      "brian does not currently control “Aglax”\."):
      c = Charter.grant(leaser=brian, territory=aglax, member=dickens, size=10)
      c.save()

    Charter.grant(leaser=arthur, territory=aglax, member=dickens, size=10)
    self.assertEqual(len(dickens.player.charter()), 0)

    # Above has not been saved, thus, the next should be fine.
    c = Charter.grant(leaser=arthur, territory=aglax, member=dickens, size=10)
    self.assertEqual(len(dickens.player.charter()), 0)
    c.save()
    self.assertEqual(len(dickens.player.charter()), 1)
    with self.assertRaisesRegexp(ValidationError,
      "dickens already has a charter in “Aglax”\."):
      Charter.grant(leaser=arthur, territory=aglax, member=dickens, size=10)

    with self.assertRaisesRegexp(ValidationError,
      ("“Aglax” has 90% of its land area available. "
       "Trying to grant 100% of land.")):
      Charter.grant(leaser=arthur, territory=aglax, member=lancelot, size=100)

    with self.assertRaisesRegexp(ValidationError,
      "Grant size of 0% is not within the range 1%–100%\."):
      Charter.grant(leaser=arthur, territory=aglax, member=lancelot, size=0)

    with self.assertRaisesRegexp(ValidationError,
      "Grant size of 101% is not within the range 1%–100%\."):
      Charter.grant(leaser=arthur, territory=aglax, member=lancelot, size=101)

    self.assertTrue(arthur.player.is_head_of_state())
    self.assertTrue(dickens.player.is_chartered_company())
    self.assertTrue(lancelot.player.is_privateer())

class ExchangeTestCase(TestCase):
  def setUp(self):
    create_test_game()

  def test_simple_exchange(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')

    offeror_r = Resources(currency=100)
    offeror_r.save()

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(
      offeror=arthur,
      offeror_resources=offeror_r,
      offeree=brian,
      offeree_resources=offeree_r)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” lack resources to offer this exchange."):
      exchange.offer()

    arthur.player.resources.currency = 1000
    arthur.player.resources.save()

    exchange.offer()
    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(brian.player.resources.wood1, 0)

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” lack resources to accept this exchange."):
      exchange.accept()

    brian.player.resources.wood1 = 11
    brian.player.resources.save()

    # Before accepting
    self.assertEqual(exchange.state, exchange.WAITING)
    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 0)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

    self.assertTrue(exchange.accept())

    # After accepting
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    self.assertEqual(brian.player.resources.currency, 100)
    self.assertEqual(brian.player.resources.wood1, 1)

    # Exchange the other way around, but this time to reject

    offeror_r = Resources(currency=100)
    offeror_r.save()

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(
      offeror=brian,
      offeror_resources=offeror_r,
      offeree=arthur,
      offeree_resources=offeree_r)

    self.assertEqual(brian.player.resources.currency, 100)
    self.assertEqual(brian.player.resources.wood1, 1)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    self.assertEqual(exchange.state, exchange.UNKNOWN)
    exchange.offer()

    self.assertEqual(exchange.state, exchange.WAITING)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 1)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    self.assertTrue(exchange.reject())

    self.assertEqual(exchange.state, exchange.REJECTED)

    self.assertEqual(brian.player.resources.currency, 100)
    self.assertEqual(brian.player.resources.wood1, 1)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.accept()

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.reject()

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.cancel()

    # Offer and cancel

    offeror_r = Resources(currency=100)
    offeror_r.save()

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(
      offeror=brian,
      offeror_resources=offeror_r,
      offeree=arthur,
      offeree_resources=offeree_r)

    self.assertEqual(brian.player.resources.currency, 100)
    self.assertEqual(brian.player.resources.wood1, 1)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    exchange.offer()

    self.assertEqual(exchange.state, exchange.WAITING)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 1)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    self.assertTrue(exchange.cancel())

    self.assertEqual(exchange.state, exchange.CANCELED)

    self.assertEqual(brian.player.resources.currency, 100)
    self.assertEqual(brian.player.resources.wood1, 1)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.accept()

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.reject()

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.cancel()


  def test_empty_exchange(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=0)
    offeror_r.save()

    offeree_r = Resources(wood1=0)
    offeree_r.save()

    exchange = Exchange(
    offeror=arthur,
    offeror_resources=offeror_r,
    offeree=arthur,
    offeree_resources=offeree_r)

    with self.assertRaisesRegexp(ValidationError, "Empty exchange."):
      exchange.offer()

  def test_exchange_between_the_same_player(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    arthur.player.resources.currency = 1
    arthur.player.resources.save()
    brian.player.resources.wood1 = 1
    brian.player.resources.save()

    offeror_r = Resources(currency=1)
    offeror_r.save()

    offeree_r = Resources(wood1=1)
    offeree_r.save()

    exchange = Exchange(
    offeror=arthur,
    offeror_resources=offeror_r,
    offeree=arthur,
    offeree_resources=offeree_r)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror and offeree cannot be the same."):
      exchange.offer()
