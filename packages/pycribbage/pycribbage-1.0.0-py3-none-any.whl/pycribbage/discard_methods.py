from copy import deepcopy
from pycribbage import deck_tools
import random


class Discard():
    """
    A class used to choose which cards to discarding to the crib in a 
    game of Cribbage

    ...

    Attributes
    ----------
    to_discard : list
        the indices of the cards from the hand to discard
    hand : Hand object
        a Hand of cards from which to discard from
    sets : list ,
        a list of the possible discard sets
    Methods
    -------
    update_hand()
        Copy of the player's hand 
    choose_discard()
        choose which cards to discard to the crib    
    create_discard_sets()
        Function to create discard combinations        
    """
    
    def __init__(self):
        self.to_discard=[]
        self.hand =deck_tools.Hand()
        self.sets = self.create_discard_sets()
    def update_hand(self,hand):
        """Copy the player's hand for processing """
        
        #deepcopy as don't want to alter the original
        self.hand=deepcopy(hand)
    def choose_discard(self):
        """choose which cards to discard to the crib
        Returns
        ----------
        to_discard : list
            the indices of the cards from the hand to discard
        """
        
        #this is default class so it discards the first two cards in deck 
        to_discard=[0,1]
        
        return to_discard
    #TODO: move to a static method of discard_methods
    def create_discard_sets(self): 
        """Function to create discard combinations
        Returns
        --------
        sets, list 
            a list of multiple 2 element lists which correspond to the 
            possible cards to discard from a 6 card hand 
        """
        sets = []
        sets.append([0, 1])
        sets.append([0, 2])
        sets.append([0, 3])
        sets.append([0, 4])
        sets.append([0, 5])
        sets.append([1, 2])
        sets.append([1, 3])
        sets.append([1, 4])
        sets.append([1, 5])
        sets.append([2, 3])
        sets.append([2, 4])
        sets.append([2, 5])
        sets.append([3, 4])
        sets.append([3, 5])
        sets.append([4, 5])

        return sets
    def print_out(self,to_print):
        print(to_print)
    

        

class RandomDiscard(Discard):
    __doc__ = Discard.__doc__ + '\n A Discard subclass used randomly choose which cards to discard\n'
    
    
    
    def __init__(self):
        
        Discard.__init__(self)
        
    def choose_discard(self): 
        __doc__ = Discard.__doc__ +'\n this subclass overrides default func to randomly choose which cards to discard'
        
        
        return self.sets[random.randrange(14)]


class HumanDiscard(Discard):
    __doc__ = Discard.__doc__ + '\n A Discard subclass used to allow a human player to choose which cards to discard'

    def __init__(self):
        Discard.__init__(self)

    # static
    def is_input_ok(self, from_input):
        """check that human inputs are correct i.e. an int between 0 and 5
        Parameters
        -----------
        from_input, int
        Returns
        ----------
        status, bool
        """
        status = False

        try:
            new_int = int(from_input)
        except ValueError:
            self.print_out('input is not a valid integer,please enter again')
            return status

        if new_int < 0 or new_int > 5:
            self.print_out('input is not in the range of 0 and 5, please enter again')
            return status
        else:
            status = True
            return status

    # static
    def are_inputs_unique(self, to_move):
        """check that human inputs are unique
        Parameters
        -----------
        to_move, list
            two element list of ints
        Returns
        ----------
        status, bool
        """
        status = False
        if to_move[0] == to_move[1]:
            self.print_out('inputs are not unique, please enter again')
            return status
        else:
            status = True
            return status

    def choose_discard(self):
        __doc__ = Discard.__doc__ + '\n this subclass overrides default func to allow a human to choose which cards to discard'

        print('Choose cards to discard')
        for i, card in enumerate(self.hand.cards):
            print('%i : %s ' % (i, card))

        to_discard = []

        input_valid = False
        inputs_unique = False

        while inputs_unique == False:

            while input_valid == False:
                first_index = input('Choose first card to discard :')
                input_valid = self.is_input_ok(first_index)

            input_valid = False

            while input_valid == False:
                second_index = input('Choose second card to discard :')
                input_valid = self.is_input_ok(second_index)

            inputs_unique = self.are_inputs_unique([first_index, second_index])

        to_discard = [int(first_index), int(second_index)]

        return to_discard
