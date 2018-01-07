import card
import shoe
import unittest

class ShoeTest(unittest.TestCase):
  def setUp(self):
    self.shoe = shoe.Shoe(num_decks=4)

  def test_reset(self):
    # Test vars
    decks = 4
    num_burn_cards = 2

    self.shoe = shoe.Shoe(decks)

    # Initial state.
    self.assertEqual(self.shoe.GetNumCardsPlayed(), decks)

    # Play round.
    self.shoe.BurnCards(num_burn_cards)

    # Final state.
    self.assertEqual(self.shoe.GetNumCardsPlayed(), decks + num_burn_cards)

    # Reset state should equal initial state.
    self.shoe.Reset()
    self.assertEqual(self.shoe.GetNumCardsPlayed(), decks)

  def test_add_card_new_deck(self):
    #self.assertRaises(self.shoe.AddCard(card.ACE), shoe.ShoeException)
    pass


if __name__ == '__main__':
  unittest.main()
