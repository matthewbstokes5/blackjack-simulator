"""An object representing a blackjack hand.

A hand can hold between 0-N cards.
A hand has a value based on the value of its cards.
A hand is active if it's value is below 22.
A hand has blackjack it has 2 cards and a value of 21.
A hand is splitable if it has a 2 card count with matching cards.
A hand is soft is it contains a card.ACE being used as card.ACE.value.
A bet is placed on a hand.
"""
import card


class HandException(Exception):
  """Base exception."""


class Hand(object):
  _BUST = 22

  def __init__(self, cards=None):
    """Constructor.

    Args:
      cards: [Cards], List of cards representing a hand.
    """
    if cards is None:
      self.cards = []
    else:
      self.cards = cards
    self.bets = []

  def AddBet(self, bet):
    """Add bet to hand.

    Args:
      bet: Bet, bet to add.
    """
    self.bets.append(bet)

  def AddCard(self, new_card):
    """Add a card to the hand.

    Args:
      card: Card, card to add.

    Raises:
      HandException: Invalid card.
    """
    if type(new_card) is not card.Card:
      raise HandException('Invalid type for card %s' % type(new_card))
    self.cards.append(new_card)

  def Split(self):
    """ Remove and return one of the duplicate cards.

    Returns:
      Card, card to be used in a new/second hand.

    Raises:
      HandException: Hand is not splitable.
    """
    if not self.IsSplitable():
      raise HandException('Cannot split hand: %s.' % ','.join(self.cards))
    return self.cards.pop()

  def AddCards(self, cards):
    """Add multiple cards to the hand.

    Args:
      cards: [Card], List of cards.

    Raises:
      HandException: Invalid card.
    """
    for new_card in cards:
      if type(new_card) is not card.Card:
        raise HandException('Invalid type for card %s' % type(new_card))
      self.cards.append(new_card)

  def IsActive(self):
    """Is the hand still in play.

    Returns:
      bool, True if hand is still active, else False.
    """
    return self.GetValue() < self._BUST

  def IsBlackjack(self):
    """If the hand has blackjack.

    Blackjack is two cards: card.ACE and card.FACE.
    
    Returns:
      bool, True if blackjack, else False.
    """
    return len(self.cards) == 2 and self.GetValue() == 21

  def IsSplitable(self):
    """If the hand is able to be split.
    
    Splits occur when a hand has two cards of the same value.

    Returns:
      bool, True if the hand can be split, else False.
    """
    # TODO(self): debug splitting.
    #return len(self.cards) == 2 and self.cards[0] == self.cards[1]
    return False

  def IsSoft(self, soft_value=None):
    """If the hand has a card.ACE which is being used as an 11.

    Args:
      soft_num: int, hand value in addition to being soft.

    Returns:
      bool. True if hand is soft, else False.
    """
    # Check if the soft value matches the hands value.
    if soft_value is not None and soft_value != self.GetValue():
      return False

    # No Ace, not soft.
    if card.ACE not in self.cards:
      return False

    # Check if card.ACE is being used as an 11.
    value = self.GetValue()
    alt_value = sum([hand_card.alt_value for hand_card in self.cards])
    return value != alt_value

  def GetValue(self):
    """Returns the value of the hand.
    
    Returns:
      int, value of the hand.
    """
    num_aces = sum([1 if hand_card == card.ACE else 0 for hand_card in self.cards])
    value = sum([hand_card.value for hand_card in self.cards])

    # No ace. Value is correct; nothing special to do.
    if num_aces == 0:
      return value

    # One ace. Use value, if this results in a bust then use alt value.
    elif num_aces == 1:
      if value < self._BUST:
        return value
      else:
        return sum([hand_card.alt_value for hand_card in self.cards])

    # Multiple aces. At most 1 ace can be used as value the rest must be
    # alt value. Get hand alt value, then try and use one ace as value.
    else:
      alt_value = sum([hand_card.alt_value for hand_card in self.cards])
      # Use one Ace as 11.
      high_value = alt_value + (card.ACE.value - card.ACE.alt_value)

      if high_value < self._BUST:
        return high_value
      else:
        return alt_value

