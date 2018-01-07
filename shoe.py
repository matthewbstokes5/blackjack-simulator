""" The shoe is the collection of cards during a game of blackjack.

The shoe has a stop card which indicates the last hand before a re-shuffle.
"""
import card
import copy
import random

class ShoeException(Exception):
  """Base shoe exception."""


class Shoe(object):
  NUM_CARDS_PER_DECK = 52
  DECK_OF_CARDS = (
      [card.ACE] * 4 +
      [card.TWO] * 4 +
      [card.THREE] * 4 +
      [card.FOUR] * 4 +
      [card.FIVE] * 4 +
      [card.SIX] * 4 +
      [card.SEVEN] * 4 +
      [card.EIGHT] * 4 +
      [card.NINE] * 4 +
      [card.FACE] * 16)

  def __init__(self, num_decks):
    self.num_decks = num_decks
    self.cards = copy.deepcopy(self.DECK_OF_CARDS)
    self.cards *= self.num_decks
    random.shuffle(self.cards)  # Shuffle shoe at beginning then pop off cards.

    # Lookup table.
    self.cards_played = {}

    # Location of the stopper.
    self.stop_location = (self.NUM_CARDS_PER_DECK * self.num_decks) - 1

    # Start state of shoe.
    self.started = False
    self._Start()

  def GetNumCardsPlayed(self):
    """Returns the number of cards played.
    
    Returns:
      int, Number of cards of the shoe which have been played.
    """
    return (self.NUM_CARDS_PER_DECK * self.num_decks) - len(self.cards)

  def Reset(self):
    """Reset everything to state upon initilization."""
    self.cards = copy.deepcopy(self.DECK_OF_CARDS)
    self.cards *= self.num_decks
    random.shuffle(self.cards)  # Shuffle shoe at beginning then pop off cards.

    self.cards_played.clear()
    self._Start()

  def RemoveCard(self, remove_card):
    """Remove a specific card from the shoe.
    
    Args:
      remove_card: Card, card to remove from the shoe.
      
    Raises:
      ShoeException: Card not present in shoe.
    """
    if remove_card not in self.cards:
      raise ShoeException('Could not remove %s from the shoe.' % remove_card)
    self.cards.remove(remove_card)

    # Update cards available, and record card played.
    if remove_card in self.cards_played:
      self.cards_played[remove_card] += 1
    else:
      self.cards_played[remove_card] = 1

  def AddCard(self, old_card):
    """Re-add previously played card to the shoe.

    Args:
      old_card: Card, previously played card to re-add.

    Raises:
      ShoeException: Card was not priorly played.
    """
    if old_card not in self.cards_played:
      raise ShoeException('Cannot re-add. None played.')

    if self.cards_played[old_card] == 1:
      self.cards_played.pop(old_card)
    else:
      self.cards_played[old_card] -= 1

    self.cards.insert(random.randint(0, len(self.cards)), old_card)

  def GetCard(self):
    """Grab the next card in the shoe, record, and remove from shoe.
    
    Returns:
      Card, card returned from the shoe.
    
    Raises:
      ShoeException: Shoe has not been started.
    """
    # Check that the shoes been started.
    if not self.started:
      raise ShoeException('Shoe not started. Please start shoe.')

    # Update cards available, and record card played.
    new_card = self.cards.pop()
    if new_card in self.cards_played:
      self.cards_played[new_card] += 1
    else:
      self.cards_played[new_card] = 1

    return new_card

  def IsFinished(self):
    """If the stop card come out.
    
    Returns:
      bool, True if stop card has come out, else False.
    """
    return self.GetNumCardsPlayed() > self.stop_location

  def SaveState(self):
    """Save current shoe state."""
    # TODO(self): Add logic to save state.
    pass

  def RestoreState(self, state):
    """Restore a previously saved state."""
    # TODO(self): Add logic to restore state.
    pass

  def GetDecksRemaining(self):
    """Returns the number of decks remaining.
    
    Returns:
      float, number of decks remaining rounded to the nearest 0.5
    """
    num_decks = float(len(self.cards)) / (
                self.NUM_CARDS_PER_DECK * self.num_decks)
    return max(round(num_decks * 2) / 2, 0.5)

  def SetStop(self, shoe_percent=None):
    """Green stop card location indicating the end of a shoe.

    Remove difference between stop and num_cards_remaining from the deck.
    
    Args:
      stop_location: float, Percent through the shoe to cut out of play.
    """
    # Set default.
    if shoe_percent is None:
      shoe_percent = random.randint(60, 85)

    # Check in range.
    if 60 < shoe_percent > 85:
     raise ShoeException('Range [60, 85] inclusive. %.1f out of range', shoe_percent)

    # Set stop location.
    self.stop_location = int((float(shoe_percent)/100.0) * len(self.cards))

  def BurnCards(self, num_cards):
    """Remove cards from the shoe.
    
    Get cards but do nothing with them.
    
    Args:
      num_cards: int, number of cards to remove from the shoe.
    """
    self.GetCards(num_cards)

  def GetCards(self, num_cards):
    """Return cards from the shoe.

    Cards are removed from the shoe and considered played.

    Args:
      num_cards: int, number of cards to return.
    
    Raises:
      ShoeException if shoe has not been started.
    """
    # Check there's enough cards remaining.
    if num_cards > len(self.cards):
      raise ShoeException('%d Cards exceed num cards remaining: %d' % (
          num_cards, len(self.cards)))

    # Get cards from the shoe.
    cards = []
    for i in xrange(num_cards):
      cards.append(self.GetCard())

    return cards

  def _Start(self, shoe_percent=None):
    """Start the shoe.
    
    Args:
      shoe_percent: float, percent through deck to place the stop card.
      
    Raise:
      ShoeException if shoe_percent is not in range."""
    self.SetStop(shoe_percent)
    self.started = True
    self.BurnCards(self.num_decks)

  def GetBlackjackPercent(self):
    """Return the percent chance of getting a blackjack.
    
    Based on the cards remaining.

    Returns:
      float, percent chance of getting a blackjack.
    """
    face_remaining = (16 * self.num_decks) - self.cards_played.get(card.FACE, 0)
    ace_remaining =  (4 * self.num_decks) - self.cards_played.get(card.ACE, 0)
    percent_face_ace = ((float(face_remaining) / len(self.cards)) * 
        (float(ace_remaining) / (len(self.cards) - 1)))
    percent_ace_face = ((float(ace_remaining) / len(self.cards)) * 
        (float(face_remaining) / (len(self.cards) - 1)))
    return (percent_face_ace + percent_ace_face) * 100
