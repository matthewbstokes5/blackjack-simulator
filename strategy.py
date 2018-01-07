""" Betting strategy."""
import stats
import card

class BettingStrategyException(Exception):
  """Base exception."""


class BettingStrategy(object):
  """Base class for betting strategies. Does nothing."""

  def __init__(self):
    self.multiplier = 1
    self.multiplier_record = {}

  def GetBetAmount(self, **kwargs):
    raise BettingStratException('No betting strategy set')

  def ProcessWin(self, blackjack=False):
    if self.multiplier not in self.multiplier_record:
      if blackjack:
        self.multiplier_record[self.multiplier] = stats.WinLossTie(win=1, win_blackjack=1)
      else:
        self.multiplier_record[self.multiplier] = stats.WinLossTie(win=1)
    else:
      self.multiplier_record[self.multiplier].win += 1
      if blackjack:
        self.multiplier_record[self.multiplier].win_blackjack += 1

  def ProcessLoss(self):
    if self.multiplier not in self.multiplier_record:
      self.multiplier_record[self.multiplier] = stats.WinLossTie(loss=1)
    else:
      self.multiplier_record[self.multiplier].loss += 1

  def ProcessTie(self):
    if self.multiplier not in self.multiplier_record:
      self.multiplier_record[self.multiplier] = stats.WinLossTie(tie=1)
    else:
      self.multiplier_record[self.multiplier].tie += 1

  def Reset(self):
    """Reset multiplier and records."""
    self.multiplier = 1
    self.multiplier_record.clear()


class StrategyMock(object):
  """Mock instantiation for testing."""

  def GetBetAmount(self, **kwargs):
    return kwargs['mock_amount']


class StrategyBlackjackOptimized(BettingStrategy):
  """Increase bet amount propotionally to increased blackjack odds.
  
  Base blackjack odds are 4.76%.
  Highest seen thus far is ~18%.
  """
  def __init__(self):
    super(StrategyBlackjackOptimized, self).__init__()
    self.bj_percent_avg = 0
    self.num_hands = 0
    self.highest = 0

  def Reset(self):
    super(StrategyBlackjackOptimized, self).Reset()
    self.bj_percent_avg = 0
    self.num_hands = 0
    self.highest = 0

  def GetBetAmount(self, **kwargs):
    # Update number of hands the moving average is for.
    self.num_hands = kwargs['num_hands']

    # Get current blackjack percent.
    current_shoe = kwargs['shoe']
    bj_percent = current_shoe.GetBlackjackPercent()

    # Start sliding calculation to bet based on stdev.
    # TODO(matthewbstokes): Use gaussian instead of linear scale.
    self.multiplier = min(max(int((bj_percent - self.bj_percent_avg) * (5)), 1), 20)

    self._RecalculateAverage(bj_percent)
    self._UpdateHighLow(bj_percent)

    return self.multiplier

  def PrintStats(self, name, game_stats, money_units):
    print '====',
    print 'Wallet: %s' % name
    print 'Units: %0.1f' % money_units
    rate = float(money_units) / game_stats.num_hands
    if rate:
      print 'Rate:  ~%d    [hands/unit]' % (max(max((1/rate), -1 * (1/rate)), 1))
    print 'Rate:  %0.3f [units/hand]' % rate
    print 'Avg: %0.3f [%%]' % self.bj_percent_avg
    print 'Highest: %0.3f [%%]' % self.highest
    print '+/-: ',
    print sorted(self.multiplier_record.iteritems())

  def _UpdateHighLow(self, bj_percent):
    if bj_percent > self.highest:
      self.highest = bj_percent

  def _RecalculateAverage(self, bj_percent):
    """Move weighted average."""
    self.bj_percent_avg = (self.bj_percent_avg * (float(self.num_hands) / (self.num_hands + 1)) +
        (bj_percent * (1.0 / (self.num_hands + 1))))


class StrategyCount(BettingStrategy):
  CARD_COUNT = {
    card.ACE: 1,
    card.FACE: 1,
    card.NINE: 0,
    card.EIGHT: 0,
    card.SEVEN: 0,
    card.SIX: 0,
    card.FIVE: -1,
    card.FOUR: -1,
    card.THREE: -1,
    card.TWO: -1
  }

  def __init__(self, table_minimum, table_maximum):
    super(StrategyCount, self).__init__()
    self.table_minimum = table_minimum
    self.table_maximum = table_maximum

  def GetBetAmount(self, **kwargs):
    count = self._GetCount(kwargs['shoe'])
    decks_remaining = kwargs['shoe'].GetDecksRemaining()
    multiplier = max(1, -1 * (count / decks_remaining))
    self.multiplier = min(self.table_minimum * multiplier, self.table_maximum)
    return self.multiplier

  def _GetCount(self, current_shoe):
    count = 0
    for shoe_card, num_cards in current_shoe.cards_played.iteritems():
      count += (self.CARD_COUNT[shoe_card] * num_cards)
    return count

  def PrintStats(self, name, game_stats, money_units):
    print '====',
    print 'Wallet: %s' % name
    print 'Units: %0.1f' % money_units
    rate = float(money_units) / game_stats.num_hands
    if rate:
      print 'Rate:  ~%d    [hands/unit]' % (max(max((1/rate), -1 * (1/rate)), 1))
    print 'Rate:  %0.3f [units/hand]' % rate
    print '+/-: ',
    print sorted(self.multiplier_record.iteritems())


class StrategyTableMinimum(BettingStrategy):
  def __init__(self, table_minimum):
    super(StrategyTableMinimum, self).__init__()
    self.table_minimum = table_minimum

  def GetBetAmount(self, **kwargs):
    return self.table_minimum

  def PrintStats(self, name, game_stats, money_units):
    print '====',
    print 'Wallet: %s' % name
    print 'Units: %0.1f' % money_units
    rate = float(money_units) / game_stats.num_hands
    if rate:
      print 'Rate:  ~%d    [hands/unit]' % (max(max((1/rate), -1 * (1/rate)), 1))
    print 'Rate:  %0.3f [units/hand]' % rate


class StrategyProgressive(BettingStrategy):
  def __init__(self, table_minimum, table_max, reset_after_max=False):
    super(StrategyProgressive, self).__init__()
    self.table_minimum = table_minimum
    self.table_max = table_max
    self.reset_after_max = reset_after_max

  def GetBetAmount(self, **kwargs):
    return self.table_minimum * self.multiplier

  def ProcessWin(self, blackjack=False):
    super(StrategyProgressive, self).ProcessWin(blackjack)
    self.multiplier = 1

  def ProcessLoss(self):
    super(StrategyProgressive, self).ProcessLoss()

    self.multiplier *= 2
    # Max bet is capped by table.
    if self.multiplier > self.table_max:
      if self.reset_after_max:
        self.multiplier = self.table_minimum
      else:
        self.multiplier = self.table_max

  def PrintStats(self, name, game_stats, money_units):
    print '====',
    print 'Wallet: %s' % name
    print 'Units: %0.1f' % money_units
    rate = float(money_units) / game_stats.num_hands
    if rate and rate < 1.0:
      print 'Rate:  ~%d    [hands/unit]' % (max(max((1/rate), -1 * (1/rate)), 1))
    print 'Rate:  %0.3f [units/hand]' % rate
    print '+/-: ',
    print sorted(self.multiplier_record.iteritems())

