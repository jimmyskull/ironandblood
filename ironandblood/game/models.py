from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext as _

class Resources(models.Model):
  currency = models.IntegerField('Currency', default=0)
  wood1 = models.IntegerField('Wood I', default=0)
  wood2 = models.IntegerField('Wood II', default=0)
  wood3 = models.IntegerField('Wood III', default=0)
  stone1 = models.IntegerField('Stone I', default=0)
  stone2 = models.IntegerField('Stone II', default=0)
  gems = models.IntegerField('Gems', default=0)
  spices = models.IntegerField('Spices', default=0)
  coffee = models.IntegerField('Coffee', default=0)
  yerba_mate = models.IntegerField('Yerba mate', default=0)
  alcohol = models.IntegerField('Alcohol', default=0)
  salt = models.IntegerField('Salt', default=0)
  opium = models.IntegerField('Opium', default=0)
  tea = models.IntegerField('Tea', default=0)
  pearls = models.IntegerField('Pearls', default=0)
  perfumery = models.IntegerField('Perfumery', default=0)
  textilesI = models.IntegerField('Textiles I', default=0)
  textilesII = models.IntegerField('Textiles II', default=0)
  craft = models.IntegerField('Craft', default=0)
  ore = models.IntegerField('Ore', default=0)
  coal = models.IntegerField('Coal', default=0)
  metal1 = models.IntegerField('Metal', default=0)
  metal2 = models.IntegerField('Precious Metal', default=0)
  food = models.IntegerField('Food', default=0)
  fibre = models.IntegerField('Fibre', default=0)
  guano = models.IntegerField('Guano', default=0)
  saltpetre = models.IntegerField('Saltpetre', default=0)
  sulfur = models.IntegerField('Sulfur', default=0)
  gunpowder = models.IntegerField('Gunpowder', default=0)

  def covers(self, other):
    """
    True if `self` has at least the same amount of resources in `other`.
    """
    return self.currency >= other.currency and \
      self.wood1 >= other.wood1 and \
      self.wood2 >= other.wood2 and \
      self.wood3 >= other.wood3 and \
      self.stone1 >= other.stone1 and \
      self.stone2 >= other.stone2 and \
      self.gems >= other.gems and \
      self.spices >= other.spices and \
      self.coffee >= other.coffee and \
      self.yerba_mate >= other.yerba_mate and \
      self.alcohol >= other.alcohol and \
      self.salt >= other.salt and \
      self.opium >= other.opium and \
      self.tea >= other.tea and \
      self.pearls >= other.pearls and \
      self.perfumery >= other.perfumery and \
      self.textilesI >= other.textilesI and \
      self.textilesII >= other.textilesII and \
      self.craft >= other.craft and \
      self.ore >= other.ore and \
      self.coal >= other.coal and \
      self.metal1 >= other.metal1 and \
      self.metal2 >= other.metal2 and \
      self.food >= other.food and \
      self.fibre >= other.fibre and \
      self.guano >= other.guano and \
      self.saltpetre >= other.saltpetre and \
      self.sulfur >= other.sulfur and \
      self.gunpowder >= other.gunpowder

  def subtract(self, other):
    """
    Changes `self` by subtracting values from `other`.
    """
    self.currency -= other.currency
    self.wood1 -= other.wood1
    self.wood2 -= other.wood2
    self.wood3 -= other.wood3
    self.stone1 -= other.stone1
    self.stone2 -= other.stone2
    self.gems -= other.gems
    self.spices -= other.spices
    self.coffee -= other.coffee
    self.yerba_mate -= other.yerba_mate
    self.alcohol -= other.alcohol
    self.salt -= other.salt
    self.opium -= other.opium
    self.tea -= other.tea
    self.pearls -= other.pearls
    self.perfumery -= other.perfumery
    self.textilesI -= other.textilesI
    self.textilesII -= other.textilesII
    self.craft -= other.craft
    self.ore -= other.ore
    self.coal -= other.coal
    self.metal1 -= other.metal1
    self.metal2 -= other.metal2
    self.food -= other.food
    self.fibre -= other.fibre
    self.guano -= other.guano
    self.saltpetre -= other.saltpetre
    self.sulfur -= other.sulfur
    self.gunpowder -= other.gunpowder

  def add(self, other):
    """
    Changes `self` by adding values from `other`.
    """
    self.currency += other.currency
    self.wood1 += other.wood1
    self.wood2 += other.wood2
    self.wood3 += other.wood3
    self.stone1 += other.stone1
    self.stone2 += other.stone2
    self.gems += other.gems
    self.spices += other.spices
    self.coffee += other.coffee
    self.yerba_mate += other.yerba_mate
    self.alcohol += other.alcohol
    self.salt += other.salt
    self.opium += other.opium
    self.tea += other.tea
    self.pearls += other.pearls
    self.perfumery += other.perfumery
    self.textilesI += other.textilesI
    self.textilesII += other.textilesII
    self.craft += other.craft
    self.ore += other.ore
    self.coal += other.coal
    self.metal1 += other.metal1
    self.metal2 += other.metal2
    self.food += other.food
    self.fibre += other.fibre
    self.guano += other.guano
    self.saltpetre += other.saltpetre
    self.sulfur += other.sulfur
    self.gunpowder += other.gunpowder

  def is_empty(self):
    """Return if all values are zero"""
    return self.currency == 0 and \
      self.wood1 == 0 and \
      self.wood2 == 0 and \
      self.wood3 == 0 and \
      self.stone1 == 0 and \
      self.stone2 == 0 and \
      self.gems == 0 and \
      self.spices == 0 and \
      self.coffee == 0 and \
      self.yerba_mate == 0 and \
      self.alcohol == 0 and \
      self.salt == 0 and \
      self.opium == 0 and \
      self.tea == 0 and \
      self.pearls == 0 and \
      self.perfumery == 0 and \
      self.textilesI == 0 and \
      self.textilesII == 0 and \
      self.craft == 0 and \
      self.ore == 0 and \
      self.coal == 0 and \
      self.metal1 == 0 and \
      self.metal2 == 0 and \
      self.food == 0 and \
      self.fibre == 0 and \
      self.guano == 0 and \
      self.saltpetre == 0 and \
      self.sulfur == 0 and \
      self.gunpowder == 0

class Player(models.Model):
  """
  Player information

  Roles
  =====

  * **Privateer** Player with no territories or charters

  * **Chartered company** Player with charters

  * **Head of State** Player that owns one or more territories

  Credit Quality
  ==============

  The player’s delinquency rate affects some macroeconomic factors:

  * economic output

  * unemployment

  * inflation

  * investments (by gaming dynamics, since credit quality is public).

  Note: in real life, the credit quality is determined by the other way around,
  and here we use the performance of a player to determine those features.
  """
  user = models.OneToOneField(User, on_delete=models.CASCADE)

  resources = models.OneToOneField(Resources, on_delete=models.CASCADE)

  delinquency = models.IntegerField(
    'Delinquent bonds',
    default=0,
    help_text=("Number of delinquent bonds as creditor. The rate of "
      "delinquency (delinquent bonds over total paid bonds) affects the "
      "credit quality of the player."))

  @classmethod
  def create_player(cls, user):
    res = Resources()
    res.save()
    return cls(user=user, resources=res)

  def territories(self):
    """List of territories controlled by the player"""
    return Territory.objects.filter(owner=self.user)

  def charter(self):
    """List of active charters to the player"""
    return Charter.objects.filter(member=self.user)

  def is_privateer(self):
    """True if the player is currently a Privateer"""
    return len(self.territories()) == 0 and len(self.charter()) == 0

  def is_chartered_company(self):
    """True if the player is currently a Chartered Company"""
    return len(self.territories()) == 0 and len(self.charter()) >= 1

  def is_head_of_state(self):
    """True if the player is currently a Head of State"""
    return len(self.territories()) >= 1

class Territory(models.Model):
  """Territory information"""
  owner = models.ForeignKey(User, null=True, blank=True)
  name = models.CharField(max_length=32, blank=False)
  land_area = models.IntegerField('Land area', default=100)

class Charter(models.Model):
  territory = models.ForeignKey(Territory, blank=False)
  member = models.ForeignKey(User, blank=False)
  size = models.IntegerField('Land area percentage', default=10)

  @classmethod
  def grant(cls, leaser, territory, member, size):
    """
    Charts `size` percent of the `territory`’s land area.
    * `leaser` must control `territory`
    * The sum of all charters in the `territory` cannot pass 100%
    * `member` cannot already have a charter in the territory.
    """
    # `size` in [1%, 100%]
    if size <= 0 or size > 100:
     raise ValidationError(
        _("Grant size of %(grant_size)d%% is not within the range 1%%–100%%."),
        params={
        'grant_size': size
        })
    # `leaser` controls `territory`
    if territory.owner != leaser:
      raise ValidationError(
        _("%(player)s does not currently control “%(territory)s”."),
        params={
        'player': leaser.username,
        'territory': territory.name
        })
    # `member` does not currently have a charter in `territory`
    if Charter.objects.filter(territory=territory, member=member):
      raise ValidationError(
        _("%(player)s already has a charter in “%(territory)s”."),
        params={
        'player': member.username,
        'territory': territory.name
        })
    # `territory` has space for this charter
    allotted = Charter.objects.filter(territory=territory).aggregate(Sum('size'))['size__sum']
    if allotted is None:
      allotted = 0
    free = 100 - allotted
    if free < size:
      raise ValidationError(
        _("“%(territory)s” has %(free)d%% of its land area available. "
          "Trying to grant %(grant_size)d%% of land."),
        params={
        'territory': territory.name,
        'free': free,
        'grant_size': size
        })
    # Create the charter, but do not save it yet
    return cls(territory=territory, member=member, size=size)

class Bond(models.Model):
  """Bond is a debt investment in which an `issuer` loans `resource` to a
  `creditor`.  The creditor agrees to pay the debt in up to `maturity_date`
  turns, except if the bond is a Perpetual Bond (`maturity_date` == 0).
  If not paid, `creditor` increases his delinquency."""
  PENDING = 'W'
  PAID = 'P'
  FORGIVEN = 'F'
  BOND_STATE = (
    (PENDING, 'Pending'),
    (PAID, 'Paid'),
    (FORGIVEN, 'Forgiven'),
  )
  # Creditor is the first lender (player) to own the debt
  creditor = models.ForeignKey(User, blank=False, related_name='+')
  creditor_resources = models.OneToOneField(Resources,
    on_delete=models.CASCADE, related_name='+')
  # Issuer is the borrower of the bond
  issuer = models.ForeignKey(User, blank=False, related_name='+')
  issuer_resources = models.ForeignKey(Resources,
    on_delete=models.CASCADE, related_name='+')
  # Maturity date and turns until maturity date
  # If not paid in time, the current creditor increases his delinquency.
  # Delinquency is reached when maturity_date == bond_age,
  # unless maturity_date == 0, which is a perpetual bond.
  maturity_date = models.IntegerField(default=0)
  bond_age = models.IntegerField(default=0)

  state = models.CharField(max_length=1, choices=BOND_STATE, default=PENDING)

class Exchange(models.Model):
  """
  Exchange Trading System

  Exchange is the way to trade resources between two players.

  Events associated with an exchange
  ----------------------------------

  Offering
    An offeror prepares an exchange, setting resources to be
    sent and resources to be received from the offeree player.
    While not accepted/rejected, the resources to be sent to offeree is held
    to guarantee the exchange success in case of agreement.

  Waiting response
    The offeree player receives the exchange proposal.

  Offeree accepts
    Resources are finally exchanged and the negotiation ends.

  Offeree rejects
    Offeror resources are released and the exchange is canceled.

  Offeror cancels
    Offeror cancels the exchange proposal and his resources and released.
  """
  UNKNOWN = 'U'
  WAITING = 'W'
  ACCEPTED = 'A'
  REJECTED = 'R'
  CANCELED = 'C'
  NEGOTIATION_STATE = (
    (UNKNOWN, 'Unknown'),
    (WAITING, 'Waiting'),
    (ACCEPTED, 'Accepted'),
    (REJECTED, 'Rejected'),
    (CANCELED, 'Canceled'),
  )
  offeror = models.ForeignKey(User, related_name='+')
  offeror_resources = models.OneToOneField(Resources, null=True,
    on_delete=models.CASCADE, related_name='+')
  offeror_territory = models.ForeignKey(Territory, null=True, blank=True,
    related_name='+')
  #oferror_as_debt = models.BooleanField(default=False)

  offeree = models.ForeignKey(User, related_name='+')
  offeree_resources = models.OneToOneField(Resources, null=True,
    on_delete=models.CASCADE, related_name='+')
  offeree_territory = models.ForeignKey(Territory, null=True, blank=True,
    related_name='+')
  #offeree_as_debt = models.BooleanField(default=False)

  state = models.CharField(max_length=1, choices=NEGOTIATION_STATE,
    default=UNKNOWN)

  def save(self, *args, **kwargs):
    if self.offeror_resources:
      self.offeror_resources.save()
    if self.offeree_resources:
      self.offeree_resources.save()
    super(Exchange, self).save(*args, **kwargs)

  def _offeror_has_resources(self):
    return not (self.offeror_resources is None or \
      self.offeror_resources.is_empty())

  def _offeree_has_resources(self):
    return not (self.offeree_resources is None or \
      self.offeree_resources.is_empty())

  def offer(self):
    """
    Offeror sends the exchange proposal.
    Collect resources from `offeror` to prepare for transaction.
    We do not reserve resources of `offeree` because he is still not aware
    of this exchange.
    """
    if self.state != self.UNKNOWN:
      raise ValidationError(_("This exchange cannot be offered."))

    if self.offeror == self.offeree:
      raise ValidationError(_("Offeror and offeree cannot be the same."))

    if not self._offeror_has_resources() and \
      not self._offeree_has_resources() and \
      self.offeror_territory is None and \
      self.offeree_territory is None:
      raise ValidationError(_("Empty exchange."))

    if self._offeror_has_resources():
      if not self.offeror.player.resources.covers(self.offeror_resources):
        raise ValidationError(
          _("Offeror “%(player)s” lack resources to offer this exchange."),
          params={
          'player': self.offeror.username
          })
      self.offeror.player.resources.subtract(self.offeror_resources)

    self.state = self.WAITING
    self.save()
    return True

  def cancel(self):
    """
    Offeror cancels the exchange.
    """
    if self.state != self.WAITING:
      raise ValidationError(_("This exchange is not waiting for response."))
    if self._offeror_has_resources():
      self.offeror.player.resources.add(self.offeror_resources)
    self.state = self.CANCELED
    self.save()
    return True

  def accept(self):
    """
    Offeree accepts the exchange. Resources are finally exchanged.
    """
    if self.state != self.WAITING:
      raise ValidationError(_("This exchange is not waiting for response."))

    if self._offeree_has_resources():
      if not self.offeree.player.resources.covers(self.offeree_resources):
        raise ValidationError(
          _("Offeree “%(player)s” lack resources to accept this exchange."),
          params={
          'player': self.offeree.username
          })
      self.offeree.player.resources.subtract(self.offeree_resources)
      self.offeror.player.resources.add(self.offeree_resources)

    if self._offeror_has_resources():
      self.offeree.player.resources.add(self.offeror_resources)

    self.state = self.ACCEPTED
    self.save()
    return True

  def reject(self):
    """
    Offeree rejects the exchange.
    """
    if self.state != self.WAITING:
      raise ValidationError(_("This exchange is not waiting for response."))

    if self._offeror_has_resources():
      self.offeror.player.resources.add(self.offeror_resources)

    self.state = self.REJECTED
    self.save()
    return True
