from pycribbage import deck_tools
import pickle

def deal():
    """ Deals a hand for pone and dealer, then chooses a cut card
    
    Returns
    -------
    pone_hand : Hand
        a hand object containing six cards
    dealer_hand : Hand
        a hand object containing six cards    
    cut_card : Hand
        a hand object containing one cards
    deck : Deck 
        a deck object containing the remaining 39 cards 
    """

    deck = deck_tools.Deck()
    deck.shuffle()

    pone_hand = deck_tools.Hand()
    dealer_hand = deck_tools.Hand()
    cut_card = deck_tools.Hand() 

    #simulate dealing by alternating who gets a card
    for i in range(0, 6):
        deck.move_cards(pone_hand, 1)
        deck.move_cards(dealer_hand, 1)
        
    deck.move_cards(cut_card,1)
   
    return pone_hand,dealer_hand,cut_card,deck


def cut_for_crib():
    """ Randomly choose a player to be the first dealer
        this simulates the traditional process of cuting 
        and seeing which player has the higher value card
        ace high?
    
    Returns
    -------
    player_string : str
        a str to denote the dealer, 'player_1' or 'player_2'
    out_string : str
        a str to record what happened with the cuts
    """

    #TODO: check whether ace is high or low 
    deck = deck_tools.Deck()
    deck.shuffle()

    player_1_cut = deck_tools.Hand()
    player_2_cut = deck_tools.Hand()

    cut_again = True
    out_string =''
    while cut_again is True:

        deck.move_cards(player_1_cut, 1)
        deck.move_cards(player_2_cut, 1)

        out_string += 'P1 cut card was %s , P2 cut card was %s\n'%(player_1_cut.cards[0].__str__(),
                                                                 player_2_cut.cards[0].__str__(),)

        if player_1_cut.cards[0].rank > player_2_cut.cards[0].rank:
            out_string += 'P1 is dealer as their card was higher'
            return 'player_1',out_string
        if player_2_cut.cards[0].rank > player_1_cut.cards[0].rank:
            out_string += 'P2 is dealer as their card was higher'
            return 'player_2',out_string
        if player_1_cut.cards[0].rank == player_2_cut.cards[0].rank:
            deck = deck_tools.Deck()
            deck.shuffle()

            player_1_cut = deck_tools.Hand()
            player_2_cut = deck_tools.Hand()
            out_string += 'Cut cards had the same face value so cut again\n'
    return '',out_string
    
def switch_dealer(player_1,player_2):
    """Switches the dealer from one player to another
       No return as it acts on the player object directly

    Parameters
    ----------
    player_1 : Player object
        Player object for player 1
    player_2 : Player object
        Player object for player 2    
    """
    #TODO: should this be in Player class?  well, no because it requries two players      
    if player_1.is_dealer ==True:
        player_1.set_dealer(False)
        player_2.set_dealer(True)
    else:
        player_1.set_dealer(True)
        player_2.set_dealer(False)

def create_set_game(n_round):
    """ Create the cards to be dealt for multiple rounds of a Cribbage GameOver 
        This is called a set game i.e. the cards are not randomly chosen as 
        this can be used for a repeatable game
        
    Parameters
    ----------
    n_round : int
        Number of rounds to create
        
    Returns
    -------
    set_game : dict
        a dictionary containing the set game.
        the  key is an integer which corresponds to the round number
        set_game[key] then contains another dictionary which contains
        Hand objects for pone_hand,dealer_hand,cut_card and deck
    """
    #TODO : should this be a class?
    set_game ={}

    for i in range(n_round):
       pone_hand,dealer_hand,cut_card,deck  = deal()
       set_game[i] ={'pone_hand' : pone_hand,
                     'dealer_hand' : dealer_hand,
                     'cut_card' : cut_card,
                     'deck':deck}
    return set_game

def save_set_game(set_game,fname):
    """ Save a set game to a pickle file
        
    Parameters
    ----------
    set_game : dict
        Dictionary containing the set_game (see create_set_game for more info)
    fname : str
        string containing the file name to save the pickle file to save (this should end with .pickle)
        
    """
    with open(fname, 'wb') as handle:
        pickle.dump(set_game, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_set_game(fname):
    """ Load a set game from a pickle file
        
    Parameters
    ----------
    fname : str
        string containing the file name of the pickle file 
  
    Returns
    -------
    set_game : dict
        dictionary containing the set game (see create_set_game for more info)
    """
    with open(fname, 'rb') as handle:
            b = pickle.load(handle)
    return b

class GameOver(Exception): 
    """Exception to be raised when a player's score is over 121"""
    pass

if __name__=="__main__":
    save_set_game(create_set_game(20),'game_1.pickle')

