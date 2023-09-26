"""
Set of functions that can be used to simulate a deck of cards
"""

"""This module contains code from
Think Python by Allen B. Downey
http://thinkpython.com

Copyright 2012 Allen B. Downey
License: GNU GPLv3 http://www.gnu.org/licenses/gpl.html

"""

import random


class Card:
    """Represents a standard playing card.

    Attributes:
      suit: integer 0-3
      rank: integer 1-13
      face_value: integer 1-10
    """

    suit_names = ["Clubs", "Diamonds", "Hearts", "Spades"]
    rank_names = [None, "Ace", "2", "3", "4", "5", "6", "7",
                  "8", "9", "10", "Jack", "Queen", "King"]

    def __init__(self, suit=0, rank=2):
        self.suit = suit
        self.rank = rank
        self.get_face_value()

    def __str__(self):
        """Returns a human-readable string representation."""
        return '%s of %s' % (Card.rank_names[self.rank],
                             Card.suit_names[self.suit])

    def __eq__(self, other):
        """Compares if cards are equal
        """
        if self.rank==other.rank and self.suit== other.suit:
            return True
        else:
            False
    def get_face_value(self):
        """ Assigns an integer to the class corresponding to the face value of the card"""
        if self.rank <= 10:
            self.face_value = self.rank
        else:
            self.face_value = 10


class Deck:
    """Represents a deck of cards.

    Attributes:
      cards: list of Card objects.
      deck_count: dictionary of the card ranks which are present in the deck.
    """

    def __init__(self):
        self.cards = []
        self.deck_count = {}

        for suit in range(4):
            for rank in range(1, 14):
                card = Card(suit, rank)
                self.cards.append(card)
        self.count()

    def __str__(self):
        res = []
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    def add_card(self, card):
        """Adds a card to the deck."""
        self.cards.append(card)

    def remove_card(self, card):
        """Removes a card from the deck."""
        self.cards.remove(card)

    def pop_card(self, i=-1):
        """Removes and returns a card from the deck.

        i: index of the card to pop; by default, pops the last card.
        """
        return self.cards.pop(i)

    def shuffle(self):
        """Shuffles the cards in this deck."""
        random.shuffle(self.cards)

    def sort(self):
        """Sorts the cards in ascending order."""
        self.cards.sort()

    def move_cards(self, hand, num):
        """Moves the given number of cards from the deck into the Hand.

        hand: destination Hand object
        num: integer number of cards to move
        """
        for i in range(num):
            hand.add_card(self.pop_card())

    def count(self):
        """ Creates a dictionary of the card ranks which are present in the deck"""

        for i in range(1,14):
            self.deck_count[str(i)] = 0

        for card in self.cards:
            self.deck_count[str(card.rank)] = self.deck_count[str(card.rank)] + 1



class Hand(Deck):
    """Represents a hand of playing cards."""

    def __init__(self, label=''):
        # type: (object) -> object
        self.cards = []
        self.label = label
        self.hand_count = {}
        self.count()


    def count(self):
        """ Creates a dictionary of the card ranks which are present in the hand"""

        for i in range(1,14):
            self.hand_count[str(i)] = 0

        for card in self.cards:
            self.hand_count[str(card.rank)] = self.hand_count[str(card.rank)] + 1




def find_defining_class(obj, method_name):
    """Finds and returns the class object that will provide
    the definition of method_name (as a string) if it is
    invoked on obj.

    obj: any python object
    method_name: string method name
    """
    for ty in type(obj).mro():
        if method_name in ty.__dict__:
            return ty
    return None


