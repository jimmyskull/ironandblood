# vim: ai ts=2 sts=2 et sw=2
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from game.models import Bond, Charter, Exchange, Player, Territory, Resources

def create_test_game():
  usernames = ['arthur', 'brian', 'blacknight', 'caesar', 'dickens', 'eric',
      'francesc', 'gumby', 'herbert', 'king', 'lancelot', 'patsy',
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
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    arthur.player.resources.currency = 1000
    arthur.player.resources.save()

    brian.player.resources.wood1 = 11
    brian.player.resources.save()

    aglax = Territory.objects.get(name='Aglax')
    aglax.owner = arthur
    aglax.save()

    efea = Territory.objects.get(name='Efea')
    efea.owner = brian
    efea.save()

  def test_simple_exchange_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')

    offeror_r = Resources(currency=100)
    offeror_r.save()

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_resources=offeree_r)

    arthur.player.resources.currency = 5
    arthur.player.resources.save()

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” lack resources to offer this exchange."):
      exchange.offer(user=arthur)

    arthur.player.resources.currency = 1000
    arthur.player.resources.save()

    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 900)

    brian.player.resources.wood1 = 3
    brian.player.resources.save()

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” lack resources to accept this exchange."):
      exchange.accept(user=brian)

    brian.player.resources.wood1 = 11
    brian.player.resources.save()

    self.assertEqual(exchange.state, exchange.WAITING)
    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 0)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

    self.assertTrue(exchange.accept(user=brian))
    self.assertEqual(exchange.state, exchange.ACCEPTED)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 10)

    self.assertEqual(brian.player.resources.currency, 100)
    self.assertEqual(brian.player.resources.wood1, 1)

  def test_simple_exchange_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')

    offeror_r = Resources(currency=100)
    offeror_r.save()

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_resources=offeree_r)

    arthur.player.resources.currency = 0
    arthur.player.resources.save()

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” lack resources to offer this exchange."):
      exchange.offer(user=arthur)

    arthur.player.resources.currency = 1000
    arthur.player.resources.save()

    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(brian.player.resources.wood1, 11)

    brian.player.resources.wood1 = 0
    brian.player.resources.save()

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” lack resources to accept this exchange."):
      exchange.accept(user=brian)

    brian.player.resources.wood1 = 11
    brian.player.resources.save()

    self.assertEqual(exchange.state, exchange.WAITING)
    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 0)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

    self.assertTrue(exchange.reject(user=brian))
    self.assertEqual(exchange.state, exchange.REJECTED)

    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.wood1, 0)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.accept(user=brian)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.reject(user=brian)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.cancel(user=arthur)

  def test_simple_exchange_cancel(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')

    offeror_r = Resources(currency=100)
    offeror_r.save()

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_resources=offeree_r)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.wood1, 0)

    exchange.offer(user=arthur)
    self.assertEqual(exchange.state, exchange.WAITING)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

    self.assertEqual(arthur.player.resources.currency, 900)
    self.assertEqual(arthur.player.resources.wood1, 0)

    self.assertTrue(exchange.cancel(user=arthur))

    self.assertEqual(exchange.state, exchange.CANCELED)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.wood1, 0)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.accept(user=brian)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.reject(user=brian)

    with self.assertRaisesRegexp(ValidationError,
      "This exchange is not waiting for response."):
      exchange.cancel(user=arthur)

  def test_exchange_invalid_user(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    dickens = User.objects.get(username='dickens')

    offeror_r = Resources(currency=100)
    offeror_r.save()

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_resources=offeree_r)

    with self.assertRaisesRegexp(ValidationError,
      "“brian” is not the offeror of this exchange."):
      exchange.offer(user=brian)

    exchange.offer(user=arthur)

    with self.assertRaisesRegexp(ValidationError,
      "“arthur” is not the offeree of this exchange."):
      exchange.accept(user=arthur)

    with self.assertRaisesRegexp(ValidationError,
      "“arthur” is not the offeree of this exchange."):
      exchange.reject(user=arthur)

    with self.assertRaisesRegexp(ValidationError,
      "“brian” is not the offeror of this exchange."):
      exchange.cancel(user=brian)

    self.assertEqual(exchange.state, exchange.WAITING)

  def test_empty_exchange(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=0)
    offeror_r.save()

    offeree_r = Resources(wood1=0)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_resources=offeree_r)

    with self.assertRaisesRegexp(ValidationError, "Empty exchange."):
      exchange.offer(user=arthur)

  def test_exchange_between_the_same_player(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=1)
    offeror_r.save()

    offeree_r = Resources(wood1=1)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=arthur, offeree_resources=offeree_r)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror and offeree cannot be the same."):
      exchange.offer(user=arthur)

  def test_simple_donation_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=1)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian)

    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 999)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(arthur.player.resources.currency, 999)
    self.assertEqual(brian.player.resources.currency, 1)

  def test_simple_donation_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=1)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian)

    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 999)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)

  def test_simple_donation_cancel(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=1)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian)

    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 999)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.cancel(user=arthur)
    self.assertEqual(exchange.state, exchange.CANCELED)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)


  def test_simple_ask_for_donation_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeree_r = Resources(wood1=1)
    offeree_r.save()

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_resources=offeree_r)

    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(arthur.player.resources.wood1, 1)
    self.assertEqual(brian.player.resources.wood1, 10)

  def test_simple_ask_for_donation_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeree_r = Resources(wood1=1)
    offeree_r.save()

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_resources=offeree_r)

    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

  def test_simple_ask_for_donation_cancel(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeree_r = Resources(wood1=1)
    offeree_r.save()

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_resources=offeree_r)

    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.cancel(user=arthur)
    self.assertEqual(exchange.state, exchange.CANCELED)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

  def test_territory_exchange_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur, offeror_territory=efea,
                        offeree=brian,  offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” does not control “Efea”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” does not control “Aglax”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    exchange.offer(user=arthur)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(aglax.owner, brian)
    self.assertEqual(efea.owner, arthur)

  def test_territory_exchange_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur, offeror_territory=efea,
                        offeree=brian,  offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” does not control “Efea”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” does not control “Aglax”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    exchange.offer(user=arthur)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)

  def test_territory_exchange_canceled(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur, offeror_territory=efea,
                        offeree=brian,  offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” does not control “Efea”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” does not control “Aglax”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    exchange.offer(user=arthur)
    exchange.cancel(user=arthur)
    self.assertEqual(exchange.state, exchange.CANCELED)
    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)

  def test_territory_donation_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur, offeror_territory=efea,
                        offeree=brian)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” does not control “Efea”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian)

    self.assertEqual(aglax.owner, arthur)
    exchange.offer(user=arthur)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(aglax.owner, brian)

  def test_territory_donation_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur, offeror_territory=efea,
                        offeree=brian)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” does not control “Efea”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian)

    self.assertEqual(aglax.owner, arthur)
    exchange.offer(user=arthur)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(aglax.owner, arthur)

  def test_territory_donation_canceled(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur, offeror_territory=efea,
                        offeree=brian)

    with self.assertRaisesRegexp(ValidationError,
      "Offeror “arthur” does not control “Efea”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian)

    self.assertEqual(aglax.owner, arthur)
    exchange.offer(user=arthur)
    exchange.cancel(user=arthur)
    self.assertEqual(exchange.state, exchange.CANCELED)
    self.assertEqual(aglax.owner, arthur)

  def test_territory_ask_donation_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” does not control “Aglax”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_territory=efea)

    self.assertEqual(efea.owner, brian)
    exchange.offer(user=arthur)
    exchange.accept(user=brian)
    self.assertEqual(efea.owner, arthur)

  def test_territory_ask_donation_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_territory=aglax)

    with self.assertRaisesRegexp(ValidationError,
      "Offeree “brian” does not control “Aglax”."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_territory=efea)

    self.assertEqual(efea.owner, brian)
    exchange.offer(user=arthur)
    exchange.reject(user=brian)
    self.assertEqual(efea.owner, brian)

  def test_territory_buy_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_resources=offeree_r)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(aglax.owner, brian)
    self.assertEqual(arthur.player.resources.wood1, 10)
    self.assertEqual(brian.player.resources.wood1, 1)

  def test_territory_buy_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    offeree_r = Resources(wood1=10)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                        offeree=brian,  offeree_resources=offeree_r)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(arthur.player.resources.wood1, 0)
    self.assertEqual(brian.player.resources.wood1, 11)

  def test_territory_sell_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    offeror_r = Resources(currency=499)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 501)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(efea.owner, arthur)
    self.assertEqual(arthur.player.resources.currency, 501)
    self.assertEqual(brian.player.resources.currency, 499)

  def test_territory_sell_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    offeror_r = Resources(currency=499)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 501)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)

  def test_territory_exchange_with_resources_accept(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    offeror_r = Resources(currency=499)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                                        offeror_resources=offeror_r,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 501)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(aglax.owner, brian)
    self.assertEqual(efea.owner, arthur)
    self.assertEqual(arthur.player.resources.currency, 501)
    self.assertEqual(brian.player.resources.currency, 499)

  def test_territory_exchange_with_resources_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    offeror_r = Resources(currency=499)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                                        offeror_resources=offeror_r,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 501)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)

  def test_territory_exchange_with_resources_canceled(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    aglax = Territory.objects.get(name='Aglax')
    efea = Territory.objects.get(name='Efea')

    offeror_r = Resources(currency=499)
    offeror_r.save()

    exchange = Exchange(offeror=arthur, offeror_territory=aglax,
                                        offeror_resources=offeror_r,
                        offeree=brian,  offeree_territory=efea)

    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.offer(user=arthur)
    self.assertEqual(arthur.player.resources.currency, 501)
    self.assertEqual(brian.player.resources.currency, 0)
    exchange.reject(user=brian)
    self.assertEqual(exchange.state, exchange.REJECTED)
    self.assertEqual(aglax.owner, arthur)
    self.assertEqual(efea.owner, brian)
    self.assertEqual(arthur.player.resources.currency, 1000)
    self.assertEqual(brian.player.resources.currency, 0)

  def test_public_exchange_offering_accept_reject(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    patsy = User.objects.get(username='patsy')

    offeror_r = Resources(currency=499)
    offeror_r.save()

    offeree_r = Resources(wood1=1)
    offeree_r.save()

    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                                        offeree_resources=offeree_r)

  def test_fail_bond_of_bond(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=499)
    offeror_r.save()

    bond = Bond(holder=arthur, borrower=brian)
    bond.save()

    exchange = Exchange(offeror=arthur, offeror_bond=bond, offeror_as_bond=True,
                        offeree=brian)

    with self.assertRaisesRegexp(ValidationError,
     "Cannot build a Bond of Bond."):
      exchange.offer(user=arthur)

    exchange = Exchange(offeror=arthur,
                        offeree=brian, offeree_bond=bond, offeree_as_bond=True)

    with self.assertRaisesRegexp(ValidationError,
      "Cannot build a Bond of Bond."):
      exchange.offer(user=arthur)

  def test_bond_lending(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=2000)
    offeror_r.save()

    offeree_r = Resources(currency=1000)
    offeree_r.save()

    # Arthur offers: $2000 as Bond in up to 2 turns in exchange of Brian
    # sending $1000.
    exchange = Exchange(offeror=brian, offeror_resources=offeror_r,
                                        offeror_as_bond=True,
                                        offeror_as_bond_maturity=2,
                        offeree=arthur,  offeree_resources=offeree_r)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(arthur.player.resources.currency, 1000)
    exchange.offer(user=brian)
    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(arthur.player.resources.currency, 1000)
    exchange.accept(user=arthur)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 0)

    bond = Bond.objects.filter(borrower=brian)[0]
    self.assertEqual(bond.state, bond.PENDING)

    with self.assertRaisesRegexp(ValidationError,
     "“arthur” is not the borrower of this bond."):
      bond.pay(user=arthur)

    with self.assertRaisesRegexp(ValidationError,
     "Offeror “brian” lack resources to offer this exchange."):
      bond.pay(user=brian)

    brian.player.resources.currency = 2000
    brian.player.resources.save()

    # Need to request Bond again, to get updated Brian information
    bond = Bond.objects.filter(borrower=brian)[0]
    self.assertEqual(bond.state, bond.PENDING)
    bond.pay(user=brian)
    self.assertEqual(bond.state, bond.PAID)

    with self.assertRaisesRegexp(ValidationError, "This bond is not pending."):
      bond.pay(user=brian)

  def test_bond_borrowing(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    offeror_r = Resources(currency=1000)
    offeror_r.save()

    offeree_r = Resources(currency=2000)
    offeree_r.save()

    # Arthur offers: $2000 as Bond in up to 2 turns in exchange of Brian
    # sending $1000.
    exchange = Exchange(offeror=arthur, offeror_resources=offeror_r,
                        offeree=brian,  offeree_resources=offeree_r,
                                        offeree_as_bond=True,
                                        offeree_as_bond_maturity=2)

    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(arthur.player.resources.currency, 1000)
    exchange.offer(user=arthur)
    self.assertEqual(brian.player.resources.currency, 0)
    self.assertEqual(arthur.player.resources.currency, 0)
    exchange.accept(user=brian)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 0)

    bond = Bond.objects.filter(borrower=brian)[0]
    self.assertEqual(bond.state, bond.PENDING)

    with self.assertRaisesRegexp(ValidationError,
     "Offeror “brian” lack resources to offer this exchange."):
      bond.pay(user=brian)

    brian.player.resources.currency = 2000
    brian.player.resources.save()

    # Need to request Bond again, to get updated Brian information
    bond = Bond.objects.filter(borrower=brian)[0]
    self.assertEqual(bond.state, bond.PENDING)
    bond.pay(user=brian)
    self.assertEqual(bond.state, bond.PAID)

  def test_bond_payment(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    brian.player.resources.currency = 1000
    brian.player.resources.save()

    offeror_r = Resources(currency=450)
    offeror_r.save()

    offeree_r = Resources(currency=311)
    offeree_r.save()

    # Arthur offers: $2000 as Bond in up to 2 turns in exchange of Brian
    # sending $1000.
    exchange = Exchange(offeror=brian,  offeror_resources=offeror_r,
                                        offeror_as_bond=True,
                                        offeror_as_bond_maturity=2,
                        offeree=arthur, offeree_resources=offeree_r,
                                        offeree_as_bond=True,
                                        offeree_as_bond_maturity=2)

    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 1000)
    exchange.offer(user=brian)
    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 1000)
    exchange.accept(user=arthur)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 1000)

    brian_bond = Bond.objects.filter(borrower=brian)[0]
    self.assertEqual(brian_bond.state, brian_bond.PENDING)

    arthur_bond = Bond.objects.filter(borrower=arthur)[0]
    self.assertEqual(arthur_bond.state, arthur_bond.PENDING)

    brian_bond.pay(user=brian)
    arthur_bond.pay(user=arthur)

    self.assertEqual(brian_bond.state, brian_bond.PAID)
    self.assertEqual(arthur_bond.state, arthur_bond.PAID)

    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    self.assertEqual(brian.player.resources.currency, 1000 - 450 + 311)
    self.assertEqual(arthur.player.resources.currency, 1000 - 311 + 450)

  def test_bond_payment(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    gumby = User.objects.get(username='gumby')

    brian.player.resources.currency = 1000
    brian.player.resources.save()

    offeror_r = Resources(currency=450)
    offeror_r.save()

    offeree_r = Resources(currency=311)
    offeree_r.save()

    exchange = Exchange(offeror=brian,  offeror_resources=offeror_r,
                                        offeror_as_bond=True,
                                        offeror_as_bond_maturity=2,
                        offeree=arthur, offeree_resources=offeree_r,
                                        offeree_as_bond=True,
                                        offeree_as_bond_maturity=2)

    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 1000)
    exchange.offer(user=brian)
    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 1000)
    exchange.accept(user=arthur)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(brian.player.resources.currency, 1000)
    self.assertEqual(arthur.player.resources.currency, 1000)

    brian_bond = Bond.objects.filter(borrower=brian)[0]
    self.assertEqual(brian_bond.state, brian_bond.PENDING)

    arthur_bond = Bond.objects.filter(borrower=arthur)[0]
    self.assertEqual(arthur_bond.state, arthur_bond.PENDING)

    exchange = Exchange(offeror=brian, offeror_bond=brian_bond, offeree=arthur)
    with self.assertRaisesRegexp(ValidationError,
     ("Cannot exchange a Bond with its holder. "
      "To pay the bond, use the payment section.")):
      exchange.offer(user=brian)

    exchange = Exchange(offeror=brian, offeror_bond=arthur_bond, offeree=arthur)
    with self.assertRaisesRegexp(ValidationError,
     ("“brian” is not the borrower of this Bond.")):
      exchange.offer(user=brian)

    exchange = Exchange(offeror=brian, offeree=arthur, offeree_bond=brian_bond)
    with self.assertRaisesRegexp(ValidationError,
     "“arthur” is not the holder of this Bond."):
      exchange.offer(user=brian)

    exchange = Exchange(offeror=brian, offeree=arthur, offeree_bond=arthur_bond)
    with self.assertRaisesRegexp(ValidationError,
     "Cannot exchange a Bond with its holder."):
      exchange.offer(user=brian)

    brian_bond.pay(user=brian)
    arthur_bond.pay(user=arthur)

    exchange = Exchange(offeror=gumby, offeree=arthur, offeree_bond=arthur_bond)
    with self.assertRaisesRegexp(ValidationError,
     "This Bond is not pending."):
      exchange.offer(user=gumby)

    exchange = Exchange(offeror=arthur, offeror_bond=arthur_bond, offeree=gumby)
    with self.assertRaisesRegexp(ValidationError,
     "This Bond is not pending."):
      exchange.offer(user=arthur)

    self.assertEqual(brian_bond.state, brian_bond.PAID)
    self.assertEqual(arthur_bond.state, arthur_bond.PAID)

    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    self.assertEqual(brian.player.resources.currency, 1000 - 450 + 311)
    self.assertEqual(arthur.player.resources.currency, 1000 - 311 + 450)

  def test_bond_payment_while_offering(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    gumby = User.objects.get(username='gumby')

    brian.player.resources.currency = 1000
    brian.player.resources.save()

    gumby.player.resources.currency = 455
    gumby.player.resources.save()

    offeror_r = Resources(currency=450)
    offeror_r.save()

    offeree_r = Resources(currency=311)
    offeree_r.save()

    exchange = Exchange(offeror=brian,  offeror_resources=offeror_r,
                                        offeror_as_bond=True,
                                        offeror_as_bond_maturity=2,
                        offeree=arthur, offeree_resources=offeree_r,
                                        offeree_as_bond=True,
                                        offeree_as_bond_maturity=2)
    exchange.offer(user=brian)
    exchange.accept(user=arthur)

    brian_bond = Bond.objects.filter(borrower=brian)[0]
    self.assertEqual(brian_bond.holder, arthur)
    self.assertEqual(brian_bond.borrower, brian)
    self.assertEqual(brian_bond.state, brian_bond.PENDING)

    arthur_bond = Bond.objects.filter(borrower=arthur)[0]
    self.assertEqual(arthur_bond.holder, brian)
    self.assertEqual(arthur_bond.borrower, arthur)
    self.assertEqual(arthur_bond.state, arthur_bond.PENDING)

    exchange = Exchange(offeror=gumby, offeree=arthur, offeree_bond=arthur_bond)
    exchange.offer(user=gumby)
    self.assertEqual(exchange.state, exchange.WAITING)
    self.assertEqual(arthur_bond.holder, brian)
    self.assertEqual(arthur_bond.borrower, arthur)
    arthur_bond.pay(user=arthur)
    brian = User.objects.get(username='brian')
    arthur = User.objects.get(username='arthur')
    gumby = User.objects.get(username='gumby')
    self.assertEqual(brian.player.resources.currency, 1000 + 311)
    self.assertEqual(arthur.player.resources.currency, 1000 - 311)
    self.assertEqual(gumby.player.resources.currency, 455)
    with self.assertRaisesRegexp(ValidationError,
     "This Bond is not pending."):
      exchange.accept(user=arthur)

    exchange = Exchange(offeror=gumby, offeree=brian, offeree_bond=brian_bond)
    exchange.offer(user=gumby)
    exchange.accept(user=brian)
    # Now brian's Bond became Gumby's Bond
    gumby_bond = Bond.objects.filter(borrower=gumby)[0]
    self.assertEqual(gumby_bond.holder, arthur)
    self.assertEqual(gumby_bond.borrower, gumby)
    gumby_bond.pay(user=gumby)

    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')
    gumby = User.objects.get(username='gumby')
    self.assertEqual(brian.player.resources.currency, 1000 + 311)
    self.assertEqual(arthur.player.resources.currency, 1000 - 311 + 450)
    self.assertEqual(gumby.player.resources.currency, 5)

  def test_bond_territory_debt_offeror(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    gleol = Territory.objects.get(name='Gleol')

    exchange = Exchange(offeror=brian, offeror_territory=gleol,
                                       offeror_as_bond=True,
                        offeree=arthur)

    self.assertEqual(gleol.owner, None)
    exchange.offer(user=brian)
    self.assertEqual(gleol.owner, None)
    exchange.accept(user=arthur)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(gleol.owner, None)

    bond = Bond.objects.filter(borrower=brian)[0]

    with self.assertRaisesRegexp(ValidationError,
     "Offeror “brian” does not control “Gleol”."):
      bond.pay(user=brian)

    gleol.owner = brian
    gleol.save()
    bond = Bond.objects.filter(borrower=brian)[0]

    self.assertEqual(bond.state, bond.PENDING)
    bond.pay(user=brian)
    self.assertEqual(bond.state, bond.PAID)

    self.assertEqual(gleol.owner, brian)

  def test_bond_territory_debt_offeree(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    gleol = Territory.objects.get(name='Gleol')

    exchange = Exchange(offeror=brian,
                        offeree=arthur, offeree_territory=gleol,
                                        offeree_as_bond=True)

    self.assertEqual(gleol.owner, None)
    exchange.offer(user=brian)
    self.assertEqual(gleol.owner, None)
    exchange.accept(user=arthur)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(gleol.owner, None)

    bond = Bond.objects.filter(borrower=arthur)[0]

    with self.assertRaisesRegexp(ValidationError,
     "Offeror “arthur” does not control “Gleol”."):
      bond.pay(user=arthur)

    gleol.owner = arthur
    gleol.save()
    bond = Bond.objects.filter(borrower=arthur)[0]

    self.assertEqual(bond.state, bond.PENDING)
    bond.pay(user=arthur)
    self.assertEqual(bond.state, bond.PAID)

    self.assertEqual(gleol.owner, arthur)

  def test_bond_territory_debt_forgive(self):
    arthur = User.objects.get(username='arthur')
    brian = User.objects.get(username='brian')

    gleol = Territory.objects.get(name='Gleol')

    exchange = Exchange(offeror=brian, offeror_territory=gleol,
                                       offeror_as_bond=True,
                        offeree=arthur)

    self.assertEqual(gleol.owner, None)
    exchange.offer(user=brian)
    self.assertEqual(gleol.owner, None)
    exchange.accept(user=arthur)
    self.assertEqual(exchange.state, exchange.ACCEPTED)
    self.assertEqual(gleol.owner, None)

    bond = Bond.objects.filter(borrower=brian)[0]

    with self.assertRaisesRegexp(ValidationError,
     "“brian” is not the holder of this bond."):
      bond.forgive(user=brian)

    self.assertEqual(bond.state, bond.PENDING)
    bond.forgive(user=arthur)
    self.assertEqual(bond.state, bond.FORGIVEN)
