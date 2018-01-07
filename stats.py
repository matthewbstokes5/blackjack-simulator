"""Game stats."""

class Stats(object):
  """Base exception."""


class GameStats(Stats):
  """Overarching game stats."""

  def __init__(self):
    self.num_hands = 0
    self.num_shoes = 0

  def Reset(self):
    self.num_hands = 0
    self.num_shoes = 0


class ActionStats(object):
  """Stats tracking hand options."""

  def __init__(self, stand=0, hit=0, double=0, split=0, bust=0):
    """Constructor.

    Args:
      stand: int, Initial number of stand actions performed.
      hit: int, Initial number of hit actions performed.
      double: int, Initial number of double actions performed.
      split: int, Initial number of split actions performed.
      bust: int, Initial number of busts.
    """
    self.stand = stand
    self.hit = hit
    self.double = double
    self.split = split
    self.bust = bust

  def Reset(self):
    """Reset all stats."""
    self.stand = 0
    self.hit = 0
    self.double = 0
    self.split = 0
    self.bust = 0

class WinLossTie(object):
  """Object to hold win/loss/tie stats and print useful stats string."""

  def __init__(self, win=0, win_blackjack=0, loss=0, tie=0):
    """Constructor.

    Args:
      win: int, number of initial wins.
      win_blackjack: int, number of initial wins.
      loss: int, number of initial losses.
      tie: int, number of initial ties.
    """
    self.win = win
    self.win_blackjack = win_blackjack
    self.loss = loss
    self.tie = tie

  def __repr__(self):
    """Format: win/loss/tie win%/loss%/tie% win-loss"""
    return '%d/%d/%d %d%%/%d%%/%d%% %d/%.2f%% %d' % (
        self.win, self.loss, self.tie, self._GetWinPercent(),
        self._GetLossPercent(), self._GetTiePercent(),
        self.win_blackjack, self._GetWinBlackjackPercent(),
        self.win - self.loss)

  def Reset(self):
    self.win = 0
    self.loss = 0
    self.tie = 0
    self.win_blackjack = 0

  def _GetWinPercent(self):
    """Returns win percentage.

    Returns:
      int, win percentage.
    """
    return int(float(self.win) / max((self.win + self.loss + self.tie), 1) * 100)

  def _GetLossPercent(self):
    """Returns loss percentage.

    Returns:
      int, loss percentage.
    """
    return int(float(self.loss) / max((self.win + self.loss + self.tie), 1) * 100)

  def _GetTiePercent(self):
    """Returns tie percentage.

    Returns:
      int, tie percentage.
    """
    return int(float(self.tie) / max((self.win + self.loss + self.tie), 1) * 100)

  def _GetWinBlackjackPercent(self):
    """Returns tie percentage.

    Returns:
      int, tie percentage.
    """
    return float(self.win_blackjack) / max((self.win + self.loss + self.tie), 1) * 100
