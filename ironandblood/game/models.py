from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext as _

class ResourceList(models.Model):
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

  class Meta:
    abstract = True

class Player(ResourceList):
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

  delinquency = models.IntegerField(
    'Delinquent bonds',
    default=0,
    help_text=("Number of delinquent bonds as creditor. The rate of "
      "delinquency (delinquent bonds over total paid bonds) affects the "
      "credit quality of the player."))

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
    Charts |size| percent of the |territory|’s land area.
    * |leaser| must control |territory|
    * The sum of all charters in the |territory| cannot pass 100%
    * |member| cannot already have a charter in the territory.
    """
    # |size| in [1%, 100%]
    if size <= 0 or size > 100:
     raise ValidationError(
        _("Grant size of %(grant_size)d%% is not within the range 1%%–100%%."),
        params={
        'grant_size': size
        })
    # |leaser| controls |territory|
    if territory.owner != leaser:
      raise ValidationError(
        _("%(player)s does not currently control “%(territory)s”."),
        params={
        'player': leaser.username,
        'territory': territory.name
        })
    # |member| does not currently have a charter in |territory|
    if Charter.objects.filter(territory=territory, member=member):
      raise ValidationError(
        _("%(player)s already has a charter in “%(territory)s”."),
        params={
        'player': member.username,
        'territory': territory.name
        })
    # |territory| has space for this charter
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

class Bond(ResourceList):
  """Bond is a debt investment in which an |issuer| loans |resource| to a
  |creditor|.  The creditor agrees to pay the debt in up to |maturity_date|
  turns, except if the bond is a Perpetual Bond (|maturity_date| == 0).
  If not paid, |creditor| increases his delinquency."""
  PENDING = 'W'
  TRANSACTION_PHASE = 'M'
  PAID = 'P'
  FORGIVEN = 'F'
  DEBT_STATE = (
    (PENDING, 'Pending'),
    (PAID, 'Paid'),
    (FORGIVEN, 'Forgiven'),
  )
  # Creditor is the first lender (player) to own the debt
  creditor = models.ForeignKey(User, blank=False, related_name='creditor')
  # Issuer is the borrower of the bond
  issuer = models.ForeignKey(User, blank=False, related_name='issuer')
  # Maturity date and turns until maturity date
  # If not paid in time, the current creditor increases his delinquency.
  # Delinquency is reached when maturity_date == bond_age,
  # unless maturity_date == 0, which is a perpetual bond.
  maturity_date = models.IntegerField(default=0)
  bond_age = models.IntegerField(default=0)
  # Debt state
  state = models.CharField(max_length=1, choices=DEBT_STATE, default=PENDING)

class Exchange(ResourceList):
  """Logging of the Exchange Trading System"""
  WAITING = 'W'
  ACCEPTED = 'A'
  REJECTED = 'R'
  NEGOTIATION_STATE = (
    (WAITING, 'Waiting'),
    (ACCEPTED, 'Accepted'),
    (REJECTED, 'Rejected'),
  )
  # Oferor information
  offeror = models.ForeignKey(User, related_name='offeror')
  # Offeree information
  offeree = models.ForeignKey(User, related_name='offeree')
  # Current exchange state
  state = models.CharField(max_length=1, choices=NEGOTIATION_STATE,
    default=WAITING)
