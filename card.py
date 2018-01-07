""" Unique cards within a deck with relevant attributes.

"""
import collections


class Card(collections.namedtuple('Card', ['name', 'value', 'alt_value'])):
  """Card."""


ACE = Card('Ace', 11, 1)
TWO = Card('Two', 2, 2)
THREE = Card('Three', 3, 3)
FOUR = Card('Four', 4, 4)
FIVE = Card('Five', 5, 5)
SIX = Card('Six', 6, 6)
SEVEN = Card('Seven', 7, 7)
EIGHT = Card('Eight', 8, 8)
NINE = Card('Nine', 9, 9)
FACE = Card('Face', 10, 10)
