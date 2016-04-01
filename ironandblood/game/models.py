from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
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

  items = [currency, wood1, wood2, wood3, stone1,
    stone2, gems, spices, coffee, yerba_mate,
    alcohol, salt, opium, tea, pearls, perfumery,
    textilesI, textilesII, craft, ore, coal,
    metal1, metal2, food, fibre, guano,
    saltpetre, sulfur, gunpowder]

  def __str__(self):
    nonzero = list()
    for it in self.items:
      quantity = getattr(self, it.name)
      if quantity != 0:
        nonzero.append('{}={}'.format(it.name, quantity))
    return ', '.join(nonzero)

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

  def __str__(self):
    return 'name={}, area={}'.format(self.name, self.land_area)

class Charter(models.Model):
  territory = models.ForeignKey(Territory, blank=False)
  member = models.ForeignKey(User, blank=False)
  size = models.IntegerField('Land area percentage', default=10)

  @staticmethod
  def _validate_size(size):
    if size <= 0 or size > 100:
     raise ValidationError(
        _("Grant size of %(grant_size)d%% is not within the range 1%%–100%%."),
        params={
        'grant_size': size
        })

  @staticmethod
  def _check_leaser_controls_territory(territory, leaser):
    if territory.owner != leaser:
      raise ValidationError(
        _("%(player)s does not currently control “%(territory)s”."),
        params={
        'player': leaser.username,
        'territory': territory.name
        })

  @staticmethod
  def _check_if_member_already_has_charter(territory, member):
    if Charter.objects.filter(territory=territory, member=member):
      raise ValidationError(
        _("%(player)s already has a charter in “%(territory)s”."),
        params={
        'player': member.username,
        'territory': territory.name
        })

  @staticmethod
  def _check_territory_not_full(territory, member, size):
    allotted = Charter.objects.filter(territory=territory)
    allotted = allotted.aggregate(Sum('size'))['size__sum']
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

  @classmethod
  def grant(cls, leaser, territory, member, size):
    """
    Grants `size` percent of the `territory`’s land area to `member`.
    * `leaser` must control `territory`
    * The sum of all charters in the `territory` cannot pass 100%
    * `member` cannot already have a charter in the territory.
    """
    cls._validate_size(size=size)
    cls._check_leaser_controls_territory(territory=territory, leaser=leaser)
    cls._check_if_member_already_has_charter(territory=territory, member=member)
    cls._check_territory_not_full(territory=territory, member=member, size=size)
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
  # Holder is the player that will receive the payment
  holder = models.ForeignKey(User, related_name='+')
  # Borrower is the player that can either pay to he holder or
  # exchange the bond with a third player.
  borrower = models.ForeignKey(User, related_name='+')

  resources = models.ForeignKey(Resources, null=True, blank=True,
    related_name='+')
  territory = models.ForeignKey(Territory, null=True, blank=True,
    related_name='+')

  maturity = models.IntegerField(default=0)

  state = models.CharField(max_length=1, choices=BOND_STATE, default=PENDING)

  def __str__(self):
    ret = ["pk={}, state={}, holder={}, borrower={}".format(self.pk,
      self.get_state_display(), self.holder, self.borrower)]
    if self.resources:
      ret.append(", resources=<{}>".format(self.resources))
    if self.territory:
      ret.append(", territory=<{}>").format(self.territory)
    return ''.join(ret)

  def _check_user_is_holder(self, user):
    if self.holder and user != self.holder:
      raise ValidationError(_("“%(player)s” is not the holder of this bond."),
        params={
        'player': user.username
        })

  def _check_user_is_borrower(self, user):
    if self.borrower and user != self.borrower:
      raise ValidationError(
        _("“%(player)s” is not the borrower of this bond."),
        params={
        'player': user.username
        })

  def _check_state_pending(self):
    if self.state != self.PENDING:
      raise ValidationError(_("This bond is not pending."))

  def forgive(self, user):
    self._check_user_is_holder(user=user)
    self._check_state_pending()
    self.state = self.FORGIVEN
    self.save()
    return True

  def pay(self, user):
    self._check_user_is_borrower(user=user)
    self._check_state_pending()
    exchange = Exchange(offeror=self.borrower,
                        offeror_resources=self.resources,
                        offeror_territory=self.territory,
                        offeree=self.holder)
    exchange.offer(user=user)
    exchange.accept(user=self.holder)
    self.state = self.PAID
    self.save()
    return True

class Exchange(models.Model):
  """
  Exchange Trading System

  Exchange is the way to trade resources between two players.

  Exchange mechanism
  ------------------

  Exchange operations allow complex transactions with some level of guarantee
  for the two players.

  Barter
    Exchange of goods, without using money.

  Donation
    Send goods, money, or territories to the other player. Or ask for donation.

  Payment
    Offer goods for money.

  Bond (debts)
    Exchange bonds directly between players (pass responsibility of payment
    to the other player, keeping the original bond lender).

  Complex operations
    One can mix goods, money, territories and even a bond (debt) in a single
    exchange operation.

  Events associated with an exchange
  ----------------------------------

  Offering
    An offeror prepares an exchange, setting resources to be
    sent and resources to be received from the offeree player.
    While not accepted/rejected, the resources to be sent to offeree is held
    to guarantee the exchange success in case of agreement.

    **Note** Territories are not held while waiting for response.  That is,
    the player can offer the same territory to many users, and the first one
    to accept will get the ownership.

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
  offeror_resources = models.ForeignKey(Resources, null=True,
    related_name='+')
  offeror_territory = models.ForeignKey(Territory, null=True, blank=True,
    related_name='+')
  offeror_bond = models.ForeignKey(Bond, null=True, blank=True,
    related_name='+')
  offeror_as_bond = models.BooleanField(default=False)
  offeror_as_bond_maturity = models.IntegerField(default=0)

  offeree = models.ForeignKey(User, related_name='+')
  offeree_resources = models.ForeignKey(Resources, null=True,
    related_name='+')
  offeree_territory = models.ForeignKey(Territory, null=True, blank=True,
    related_name='+')
  offeree_bond = models.ForeignKey(Bond, null=True, blank=True,
    related_name='+')
  offeree_as_bond = models.BooleanField(default=False)
  offeree_as_bond_maturity = models.IntegerField(default=0)

  state = models.CharField(max_length=1, choices=NEGOTIATION_STATE,
    default=UNKNOWN)

  def __str__(self):
    ret = ["pk={}, state={}".format(self.pk, self.get_state_display())]
    if self.offeror:
      ret.append(", (offeror={}".format(self.offeror))
      if self.offeror_resources:
        ret.append(", resources=<{}>".format(self.offeror_resources))
      if self.offeror_territory:
        ret.append(", territory=<{}>".format(self.offeror_territory))
      if self.offeror_bond:
        ret.append(", bond=<{}>".format(self.offeror_bond))
      if self.offeror_as_bond:
        ret.append(", as_bond")
      ret.append(")")
    else:
      ret.append(", no offeror")
    if self.offeree:
      ret.append(", (offeree={}".format(self.offeree))
      if self.offeree_resources:
        ret.append(", resources=<{}>".format(self.offeree_resources))
      if self.offeree_territory:
        ret.append(", territory=<{}>".format(self.offeree_territory))
      if self.offeree_bond:
        ret.append(", bond=<{}>".format(self.offeree_bond))
      if self.offeree_as_bond:
        ret.append(", as_bond")
      ret.append(")")
    else:
      ret.append(", no offeree")
    return ''.join(ret)

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

  def _validate_bond(self):
    # We must refuse Bond exchanges with their holders, because currently
    # there is no way to perform a safe transaction.
    # Example: offeror Bond payment would be ok, but if offeree Bond, then
    # we would have to undo the first payment.
    if (self.offeror_bond is not None and self.offeror_as_bond) or \
      (self.offeree_bond is not None and self.offeree_as_bond):
      raise ValidationError(_("Cannot build a Bond of Bond."))

    if self.offeror_bond:
      if self.offeror_bond.borrower != self.offeror:
        raise ValidationError(
          _("“%(player)s” is not the borrower of this Bond."),
          params={
          'player': self.offeror.username
          })
      if self.offeror_bond.holder == self.offeree:
        raise ValidationError(
          _("Cannot exchange a Bond with its holder. "
            "To pay the bond, use the payment section."))
      if self.offeror_bond.state != self.offeror_bond.PENDING:
        raise ValidationError(_("This Bond is not pending."))

    if self.offeree_bond:
      if self.offeree_bond.borrower != self.offeree:
        raise ValidationError(
          _("“%(player)s” is not the holder of this Bond."),
          params={
          'player': self.offeree.username
          })
      if self.offeree_bond.holder == self.offeror:
        raise ValidationError(
          _("Cannot exchange a Bond with its holder."))
      if self.offeree_bond.state != self.offeree_bond.PENDING:
        raise ValidationError(_("This Bond is not pending."))

  def _validate_territory_ownership(self):
    """Applicable before accept"""
    if not self.offeror_as_bond and self.offeror_territory:
      if self.offeror_territory.owner != self.offeror:
        raise ValidationError(
          _("Offeror “%(player)s” does not control “%(territory)s”."),
          params={
          'player': self.offeror.username,
          'territory': self.offeror_territory.name
          })

    if not self.offeree_as_bond and self.offeree_territory:
      if self.offeree_territory.owner != self.offeree:
        raise ValidationError(
          _("Offeree “%(player)s” does not control “%(territory)s”."),
          params={
          'player': self.offeree.username,
          'territory': self.offeree_territory.name
          })

  def _validate_resource_sufficiency(self):
    if not self.offeree_as_bond and self._offeree_has_resources():
      if not self.offeree.player.resources.covers(self.offeree_resources):
        raise ValidationError(
          _("Offeree “%(player)s” lack resources to accept this exchange."),
          params={
          'player': self.offeree.username
          })

    if self.state == self.UNKNOWN:
      if not self.offeror_as_bond and self._offeror_has_resources():
        if not self.offeror.player.resources.covers(self.offeror_resources):
          raise ValidationError(
            _("Offeror “%(player)s” lack resources to offer this exchange."),
            params={
            'player': self.offeror.username
            })

  def _check_if_empty(self):
    if not self._offeror_has_resources() and \
      not self._offeree_has_resources() and \
      self.offeror_territory is None and \
      self.offeree_territory is None and \
      self.offeror_bond is None and \
      self.offeree_bond is None:
      raise ValidationError(_("Empty exchange."))

  def _validate_user_as_offeror(self, user):
    if self.offeror and user != self.offeror:
      raise ValidationError(
        _("“%(player)s” is not the offeror of this exchange."),
        params={
        'player': user.username
        })

  def _validate_user_as_offeree(self, user):
    if self.offeree and user != self.offeree:
      raise ValidationError(
        _("“%(player)s” is not the offeree of this exchange."),
        params={
        'player': user.username
        })

  def offer(self, user):
    """
    Offeror `user` sends the exchange proposal.
    Collect resources from `offeror` to prepare for transaction.
    We do not reserve resources of `offeree` because he is still not aware
    of this exchange.
    """
    self._validate_user_as_offeror(user=user)

    if self.state != self.UNKNOWN:
      raise ValidationError(_("This exchange cannot be offered."))

    if self.offeror == self.offeree:
      raise ValidationError(_("Offeror and offeree cannot be the same."))

    self._check_if_empty()
    self._validate_bond()
    self._validate_territory_ownership()
    self._validate_resource_sufficiency()

    if not self.offeror_as_bond and self._offeror_has_resources():
      self.offeror.player.resources.subtract(self.offeror_resources)

    self.state = self.WAITING
    self.save()
    return True

  @transaction.atomic
  def accept(self, user):
    """
    Offeree `user` accepts the exchange. Resources are finally exchanged.
    """
    self._validate_user_as_offeree(user=user)

    if self.state != self.WAITING:
      raise ValidationError(_("This exchange is not waiting for response."))

    self._validate_bond()
    self._validate_territory_ownership()
    self._validate_resource_sufficiency()

    # Execute transactions after checking everything
    if self.offeror_as_bond:
      bond = Bond(borrower=self.offeror, holder=self.offeree,
        resources=self.offeror_resources,
        territory=self.offeror_territory,
        maturity=self.offeror_as_bond_maturity)
      bond.save()
    else:
      if self._offeror_has_resources():
        self.offeree.player.resources.add(self.offeror_resources)

      if self.offeror_territory:
        self.offeror_territory.owner = self.offeree
        self.offeror_territory.save()

      if self.offeror_bond:
        self.offeror_bond.borrower = self.offeree
        self.offeror_bond.save()

    if self.offeree_as_bond:
      bond = Bond(borrower=self.offeree, holder=self.offeror,
        resources=self.offeree_resources,
        territory=self.offeree_territory,
        maturity=self.offeree_as_bond_maturity)
      bond.save()
    else:
      if self._offeree_has_resources():
        self.offeree.player.resources.subtract(self.offeree_resources)
        self.offeror.player.resources.add(self.offeree_resources)

      if self.offeree_territory:
        self.offeree_territory.owner = self.offeror
        self.offeree_territory.save()

      if self.offeree_bond:
        self.offeree_bond.borrower = self.offeror
        self.offeree_bond.save()

    self.offeree.player.resources.save()
    self.offeror.player.resources.save()
    self.state = self.ACCEPTED
    self.save()
    return True

  def _undo_offer(self):
    if self.state != self.WAITING:
      raise ValidationError(_("This exchange is not waiting for response."))

    if self._offeror_has_resources():
      self.offeror.player.resources.add(self.offeror_resources)

  def reject(self, user):
    """
    Offeree `user` rejects the exchange.
    """
    self._validate_user_as_offeree(user=user)
    self._undo_offer()
    self.state = self.REJECTED
    self.save()
    return True

  def cancel(self, user):
    """
    Offeror `user` cancels the exchange. Operation identical to rejection.
    """
    self._validate_user_as_offeror(user=user)
    self._undo_offer()
    self.state = self.CANCELED
    self.save()
    return True
