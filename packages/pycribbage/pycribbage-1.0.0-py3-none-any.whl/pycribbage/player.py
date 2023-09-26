from .deck_tools import Hand
from .cribbage_tools import GameOver


class Player():
    """
    A class used to represent a player in the game of Cribbage
    
    This should be the only class that moves cards - as in the physical game 
    only the player moves/touches cards.
    
    In a similar way, this is the only class should change the score. As in the
    physical game only the player touches their own scoring peg 
    ...

    Attributes
    ----------
    name : str
        the player's name
    score : int
        the player's score
    is_dealer : bool
        flag to set dealer status for this player (only one player can be dealer at a time)
    discard_method : Discard
        a Discard object that defines the method used to choose discards in the show
    the_play_method : ThePlayMethod 
        a ThePlayMethod object that defines the method used to choose cards in the play
    hand : Hand 
        a Hand object that represents the player's hand 
    played_cards : Hand 
        a Hand object that represents the cards the player has played in 'the play' 
        
    Methods
    -------
    move_to_table()
        Move cards from player's hand to the table
    move_to_crib()
        Move cards from player's hand to the crib 
    set_dealer()
        set the dealer status for the player    
    update_score()
        update player's score 
    update_hand()
        update player's hand    
    """
    def __init__(self,name,discard_method,the_play_method):
    
        """
        Parameters
        ----------
        name : str
            the player's name
        discard_method : Discard
            a Discard object that defines the method used to choose discards in the show
        the_play_method : ThePlayMethod 
            a ThePlayMethod object that defines the method used to choose cards in the play
        """
        
        self.name = name
        self.score=0
        self.is_dealer= False
        self.discard_method=discard_method
        self.the_play_method=the_play_method
        self.hand = Hand()
    
    def move_to_table(self,to_table,table):
        """
        Move cards from player's hand to the table
        
        Parameters
        ----------
        to_table : int
            index of the card from Hand to move to the table 
        table : Hand
            hand object to represent the cards on the table
        """    
        card = self.hand.cards[to_table]
        table.add_card(card)
        self.hand.pop(to_table)
        
    def move_to_crib(self,to_discard,crib):
        """
        Move cards from player's hand to the crib
        Parameters
        ----------
        to_discard : list
            two element list with the indices of the cards from Hand to move to the crib
        crib : Hand
            hand object to represent the crib
        """   
        
        #loop over discard choices and move to crib, store in list
        to_remove=[]
        for i in to_discard:
            card = self.hand.cards[i]
            crib.add_card(card)
            to_remove.append(card)
        
        #need to be careful as pop will change the index so loop over the list and check index 
        for card_to_move in to_remove:
            for i,card in enumerate(self.hand.cards):
                if card == card_to_move:
                    self.hand.pop_card(i)

    def set_dealer(self,to_deal):
        """set the dealer status for the player
        
        Parameters
        ----------
        to_deal : bool
            dealer status for this player (only one player can be dealer at a time)
        """
        if to_deal==True:
            self.is_dealer=True
        else:
            self.is_dealer=False
    
    def update_score(self,increment):
        """
        update player's score
        
        Parameters
        ----------
        increment : int
            amount to increment score by
            
        Raises
        ----------
        GameOver
            If a player's score is greater than or equal to 121
            then the game is finished and this player wins 
        """
        
        old_score =self.score
        setattr(self,'score',old_score+increment)
        
        if self.score >=121:
            raise GameOver

    def update_hand(self,hand):
        """update player's hand
        
        Parameters
        ----------
        hand : Hand
            new hand object for player's hand 
        """
        self.hand = hand
