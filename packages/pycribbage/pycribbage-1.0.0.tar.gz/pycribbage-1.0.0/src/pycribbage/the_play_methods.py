from copy import deepcopy
from pycribbage import deck_tools
import random 

class ThePlayMethod():
    """
    A class used to choose which cards to play in 'the play' phase of a cribbage game

    ...

    Attributes
    ----------
    hand : Hand object
        a Hand of cards from which to play  from
    on_table : Hand object
        the cards on the table 
    table_sum : int
        sum of face values of the cards on the table     
        
    Methods
    -------
    update_hand()
        Copy of the player's hand 
    update_on_table()
        Update which cards are on the table   
    get_table_sum()
        sum the cards on the table 
    assess_validity()
        assess which cards can legally be added to the table
    """
    def __init__(self):
        """no parameters or return values """
        self.hand=deck_tools.Hand()
        self.on_table=deck_tools.Hand()
        self.table_sum =0 

    def update_hand(self,hand):
        """ Copy of the player's hand """
        self.hand =deepcopy(hand)
    
    def update_on_table(self,on_table):
        """ Update which cards are on the table """

        self.on_table =deepcopy(on_table)
        self.get_table_sum() 
    #TODO : private?
    def get_table_sum(self):
        """ sum the cards on the table """
        self.table_sum=0
        for card in self.on_table.cards:
            self.table_sum = self.table_sum + card.face_value 
    #TODO : private?
    def assess_validity(self):
        """ assess which cards can legally be added to the table 
            the criteria being if it would push the table sum over 31
        Returns
        ----------
        valid_index, list 
            a list of indices which correspond to the cards in hand which 
            can be played.
            An empty list means to cards can be played 
        """    
        valid_index=[]
        
        
        for i,card in enumerate(self.hand.cards):
            new_sum = self.table_sum + card.face_value
            if new_sum <=31:
                valid_index.append(i)
                
        return valid_index 

    def choose_play(self):
        """ choose which card to add to table 
         
        Returns
        ----------
        choose_index, int (or None)  
            the index of the card in hand to be played 
            None returned if no card can be played 
        """   
        valid_index = self.assess_validity()
        
        if len(valid_index)==0:
            return None
        else:
            return valid_index[0]
    def print_out(self,to_print):
        print(to_print)


class RandomThePlay(ThePlayMethod):
    __doc__ = ThePlayMethod.__doc__ + '\n A ThePlayMethod subclass used to allow a random choice of card to play'
    
    def __init__(self):
        ThePlayMethod.__init__(self)
        
    def choose_play(self):     
    
        #choose a random entry from valid_index
        valid_index = self.assess_validity()
        len_valid = len(valid_index)
        
        if len_valid ==0:
            return None
        elif len_valid==1:
            return valid_index[0]
        else:    
            to_choose=random.randrange(len_valid)
            return valid_index[to_choose]


class HumanThePlay(ThePlayMethod):
    __doc__ = ThePlayMethod.__doc__ + '\n A ThePlayMethod subclass used to allow a human choice of card to play'

    def __init__(self):
        ThePlayMethod.__init__(self)

    def is_input_ok(self, from_input, valid_index):
        """check that human inputs are correct i.e. an int between 0 and 5

        Parameters
        -----------
        from_input, int
        valid_index,list
            list (elements are ints) of valid choices
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

        if new_int not in valid_index:
            self.print_out(('input is not valid, choices are : ' + str(valid_index)))
            self.print_out('please enter again')
            return status
        else:
            status = True
            return status

    def choose_play(self):
        """human method to choose play"""

        print('Waiting for your choice')
        print('cards on the table:')

        for card in self.on_table.cards:
            print('%s ' % (card))

        self.get_table_sum()
        print('table sum is %i' % self.table_sum)

        valid_index = self.assess_validity()
        print('Your hand:')
        for i, card in enumerate(self.hand.cards):
            print('%i : %s ' % (i, card))

        if len(valid_index) > 1:
            input_valid = False
            while input_valid == False:
                choice = input('Choose index of card to play')
                input_valid = self.is_input_ok(choice, valid_index)
            return int(choice)

        elif len(valid_index) == 1:
            print('only one valid choice')
            input('you will play %i, press a key to continue ' % valid_index[0])
            return valid_index[0]

        elif len(valid_index) == 0:
            print('no valid choices so you must say go')
            input('Say go, press a key to continue')
            return None