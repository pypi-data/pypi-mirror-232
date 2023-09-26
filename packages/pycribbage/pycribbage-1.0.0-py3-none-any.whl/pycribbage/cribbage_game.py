from pycribbage import player,scorer
from copy import deepcopy
from pycribbage.cribbage_tools import GameOver,cut_for_crib,switch_dealer,deal
from pycribbage import deck_tools
import os 
import json



class CribbageGame():
    """
    A class used to represent a game of Cribbage

    ...

    Attributes
    ----------
    set_game : dict
        a dictionary which contains the cards to played in each hand
    rounds : dict
        a dictionary which contains each CribbageRound object
    winner : str
        a string which represents the winner of the game 
    for_set_game : dict
        a dictionary which contains the cards which were dealt in each round
    player_1 : Player 
        a Player object to represent the first player
    player_2 : Player 
        a Player object to represent the second player
    pone : Player 
        a Player object to represent the non-dealer (pone) 
    dealer : Player 
        a Player object to represent the dealer 
    cut_player :str
        string to denote the cut player 
    batch_mode : bool 
        batch_mode = True will write the output to a log file 
    log_fd : _io.TextIOWrapper
        file object to be logged to 
    on_table : Hand
        a hand object to represent the cards currently active on the table 
    crib : Hand
        a hand object to represent the crib
    cut_card : Hand
        a hand object to represent cut card          
    table_sum : int
        sum of face values of the cards on the table 
    active_player_str : str
        string to say which player active    
    dealer_go : bool
        bool to represent if the dealer is able to play a card_to_play
        True means that the player has said 'go' and cannot go
    pone_go : bool
        bool to represent if pone is able to play a card_to_play
        True means that the player has said 'go' and cannot go
    go_added : bool
        bool to keep track is the point for a go has been added to the player's score  
    play_end : bool
        bool to represent if the play has finished 
    pone_hand_init : Hand 
        a Hand object that represents the cards dealt to pone player . 
        This is required as cards will be moved to the table and they need to be returned
        before the show 
    dealer_hand_init : Hand 
        a Hand object that represents the cards dealt to the dealer. 
        This is required as cards will be moved to the table and they need to be returned
        before the show  

        
    Methods
    -------
    play_game()
        Plays out the cribbage game - calls all other methods
    play_round()
        Plays out a round (deal,discard,the play, the show)        
    set_pone_dealer()
        allocate players as pone and dealer
    create_log_file()
        create a log file to write game details to
    logger()
        log to console (if not batch) and file
    close_log_file()
        close the log file
    deal_hands()
        Deal out hands and perform cut      
    discard()
        collect player's discard and move into crib
    update_crib()
        update the crib    
    update_cut_card()
        update the the cut card      
    the_show()
        A function used to represent the show phase of cribbage
    reset_table() 
        reset table to a pre-round state
    reset_crib_and_cut_card()
        set crib and cut card to empty Hand objs"
    the_play()
        A function used to represent 'the play' phase of cribbage 
    go()
       simulate the fact that active player can't play so says go
    switch_player()
        switch active player after a cards has been played or player says go
    return_cards()    
        move cards from the table back to player's hands
    """
    def __init__(self,players,set_game={},cut_player=None,batch_mode=False):
        """
        Parameters
        ----------
        players : list
            A list (two entries) which contains the two Player objects for the game
        set_game : dict , optional
            a dictionary which contains the cards to played in each hand.
            if not set then the cards to be dealt will be randomly generated
        set_game : dict , optional
            a dictionary which contains the cards to played in each hand.
            if not set then the cards to be dealt will be randomly generated
        cut_player :str,optional
            if a given player is to be the dealer then set this as 'player_1' or 'player_2'
        batch_mode : bool, optional 
            batch_mode = True will write the output to a log file     
        """
        
        self.set_game=set_game
        self.rounds ={}
        self.winner=''
        self.for_set_game={}
        self.player_1=None
        self.player_2=None
        self.cut_player=cut_player
        self.batch_mode = batch_mode
        self.on_table = deck_tools.Hand() 
        self.crib = deck_tools.Hand() 
        self.cut_card = deck_tools.Hand() 
        
        self.active_player_str='pone'
        self.create_log_file()
        
        self.dealer_go=False
        self.pone_go=False

        self.go_added = False
        self.play_end=False
        self.active_player_str ='pone'
        self.table_sum=0

        #TODO: move this out of this class - pass player_obj instead
        for i in [0,1]:
            player_obj = players[i]                          
            setattr(self,'player_%i'%(i+1),player_obj)
            
    def play_game(self):
        """Plays out the cribbage game"""

        self.logger('Game about to begin !')
        self.logger('Cut card to choose who is first dealer')
        
        #First choose which player should be the first dealer
        if self.cut_player ==None:
            cut_player,cut_string_ = cut_for_crib()
            cut_string = cut_string_.replace('P1',self.player_1.name).replace('P2',self.player_2.name)
        else:
            cut_player = self.cut_player
            cut_string ='%s will be dealer'%self.cut_player
        self.logger(cut_string)    
        if cut_player =='player_1':
            self.player_1.set_dealer(True)
            self.player_2.set_dealer(False)
            self.logger('%s is dealer'%self.player_1.name)

        elif cut_player =='player_2':
            self.player_1.set_dealer(False)
            self.player_2.set_dealer(True)
            self.logger('%s is dealer'%self.player_2.name)

        self.set_pone_dealer()
        
        self.for_set_game ={}
        i_round= 0
        
        #keep playing rounds until someone wins
        while True:
        
            try:
                self.play_round(i_round)
            except GameOver:
                
                #self.logger(play.__str__())
                #self.logger(show.__str__().replace('Pone',pone.name).replace('Dealer',dealer.name).replace('Crib',"%s's Crib"%dealer.name))
                self.logger('end of game scores')
                self.logger('%s %i %s %i'%(self.player_1.name,
                                     self.player_1.score,
                                     self.player_2.name,
                                     self.player_2.score))
                if self.player_1.score >=121:
                    self.winner = self.player_1.name
                else:
                    self.winner = self.player_2.name
                    
                self.close_log_file()
                break 
            i_round=i_round+1        
    
    def play_round(self,i_round):
        """ plays out a round of cribbage"""
        self.logger('start of round %i'%i_round)
                
        if len(self.set_game.keys()) ==0:
            self.for_set_game[i_round] = self.deal_hands()
        else:
            self.for_set_game[i_round] = self.deal_hands(self.set_game[i_round])
        self.discard()
        self.the_play()
        
        pone_score,dealer_hand_score,crib_score,dealer_score,out_string = self.the_show()
       
        self.pone.update_score(pone_score)
        self.dealer.update_score(dealer_score)
        self.save_state()  
       
        self.logger(out_string.replace('Pone',self.pone.name).replace('Dealer',self.dealer.name)\
                    .replace('Crib',"%s's Crib"%self.dealer.name))
        
        self.logger('='*30)
        self.logger('End of round %i'%i_round)
        self.logger('%s score : %i , %s score :%i\n'%(self.player_1.name,
                                                self.player_1.score,
                                                self.player_2.name,
                                                self.player_2.score))
        self.logger('='*30)
        #self.save_state('round_%i.json'%i_round)
        #clean up at the end of the round 
        switch_dealer(self.player_1,self.player_2)
        self.set_pone_dealer()
        self.reset_crib_and_cut_card() 
        self.reset_table()
        self.save_state()  
        
    def set_pone_dealer(self):
        """allocate players as pone and dealer"""
        
        if self.player_1.is_dealer ==True:
            self.pone=self.player_2
            self.dealer=self.player_1
        else:
            self.dealer=self.player_2
            self.pone=self.player_1
        
        
    def create_log_file(self,path=None):
        """create a log file to write game details to
        
        Parameters
        ----------
        path : str, optional 
            path where file is to be written
        """
        if path ==None:
            path=os.getcwd()
        
        i_log = 0
        while os.path.exists(os.path.join(path,"game%03d.log" % i_log)):
           i_log += 1
           
        fname_log = "game%03d.log" % i_log    
        
        fname = os.path.join(path,fname_log)
        f = open(fname,'w+')
 
        self.log_fd = f
        
    def logger(self,to_log):
        """ log to console (if not batch) and file"""
        
        if to_log.endswith('\n'):
            pass
        else:
            to_log = to_log +'\n'
        self.log_fd.write(to_log)
        
        if self.batch_mode == False:
            print(to_log)
            
    def close_log_file(self):
        """close the log file"""
        self.log_fd.close()
 
    def deal_hands(self,set_game={}):
        """
        Deal out hands and perform cut
        
        Parameters
        ----------
        set_game : dict, optional 
            dict of hands for each player , 
            default is an empty dict in which case new random hands are created
            

        Returns
        ----------
        for_set_game : dict
            dict of hands for each player, this is returned so that the 
            same hands can be replayed 
        """
        
        if len(set_game.keys()) ==0:
           pone_hand,dealer_hand,cut_card,deck  = deal()
        else:
           pone_hand =set_game['pone_hand']
           dealer_hand =set_game['dealer_hand']
           cut_card =set_game['cut_card']
           deck =set_game['deck']
       
        for_set_game ={'pone_hand' : deepcopy(pone_hand),
         'dealer_hand' : deepcopy(dealer_hand),
         'cut_card' : deepcopy(cut_card),
         'deck':deepcopy(deck)}
        self.pone.update_hand(pone_hand)
        self.dealer.update_hand(dealer_hand)
        self.cut_card = cut_card
        self.deck = deck
        
        return for_set_game
        
    def discard(self):
        """collect player's discard and move into crib""" 
        
        self.pone.discard_method.update_hand(self.pone.hand)
        self.save_state()        
        pone_to_discard = self.pone.discard_method.choose_discard() 
        self.save_state()             
        self.pone.move_to_crib(pone_to_discard,self.crib)
        self.save_state()     
        
        
        self.dealer.discard_method.update_hand(self.dealer.hand)
        self.save_state()   
        dealer_to_discard = self.dealer.discard_method.choose_discard()
        self.save_state()   
        self.dealer.move_to_crib(dealer_to_discard,self.crib)
        self.save_state()   

        
    def update_crib(self,crib):
        """update the crib
        
        Parameters
        ----------
        crib : Hand
            new hand object for player's hand 
        """
        self.crib = crib
    
    def update_cut_card(self,cut_card):
        """update cut card

        Parameters
        ----------
        cut_card : Hand
            new cut card for the table 
        """
        self.cut_card = cut_card
    
    def the_show(self):
        """
        A function used to represent the show phase of cribbage
     
        Returns
        --------
        pone_score, int
        dealer_hand_score, int
        crib_score, int 
        dealer_score, int
        out_string, str
        """
        #deepcopy to avoid altering the original
        pone_hand = deepcopy(self.pone.hand)
        dealer_hand = deepcopy(self.dealer.hand)
        crib = deepcopy(self.crib)
        cut_card = deepcopy(self.cut_card)

        #add the cut card to each hand for scoring - this is OK as it is a deepcopy 
        pone_hand.add_card(cut_card.cards[0])
        dealer_hand.add_card(cut_card.cards[0])
        crib.add_card(cut_card.cards[0])


        pone_score         = scorer.ScoreTheShow(pone_hand).score 
        dealer_hand_score  = scorer.ScoreTheShow(dealer_hand).score 
        crib_score         = scorer.ScoreTheShow(crib,is_crib=True).score 
        dealer_score       = dealer_hand_score + crib_score
        
        out_string='='*30 + "\n"
        
        out_string=out_string +'Pone Hand, Score : %i\n'%pone_score
        out_string=out_string +'='*30 + "\n"
        out_string=out_string + pone_hand.__str__() +'\n'
        out_string=out_string +'='*30 + "\n"
        
        out_string=out_string +'Dealer Hand, Score %i\n'%dealer_hand_score
        out_string=out_string +'='*30 + "\n"
        out_string=out_string + dealer_hand.__str__() +'\n'
        out_string=out_string +'='*30 + "\n"

        out_string=out_string +'Crib, Score : %i\n' %crib_score
        out_string=out_string +'='*30 + "\n"
        out_string=out_string + crib.__str__() +'\n'
        out_string=out_string +'='*30 + "\n"

        out_string = out_string +'Final Scores\n'
        out_string=out_string +'='*30 + "\n"
        out_string = out_string +'Pone : %i  Dealer : %i' %(pone_score,dealer_score)
        
        return pone_score,dealer_hand_score,crib_score,dealer_score,out_string
    
    def reset_table(self): 
        """ reset table to a pre-round state"""
    
        self.dealer_go=False
        self.pone_go=False

        self.go_added = False
        self.play_end=False
        self.active_player_str ='pone'

        self.on_table = deck_tools.Hand()

        self.table_sum=0
    
    def reset_crib_and_cut_card(self):
        """ set crib and cut card to empty Hand objs"""
        self.crib = deck_tools.Hand()
        self.cut_card = deck_tools.Hand()

    def the_play(self,):
        """
        A function used to represent 'the play' phase of cribbage 
                
        """    
        

        pone_score_init= self.pone.score
        dealer_score_init= self.dealer.score
        
        #TODO : add another method of storing these
        self.pone_hand_init = deepcopy(self.pone.hand)
        self.dealer_hand_init = deepcopy(self.dealer.hand)
   
        pone_the_play_score =0
        dealer_the_play_score =0
        
        out_string=''
        
        while self.play_end ==False: 
           
            if len(self.pone.hand.cards)==0 and len(self.dealer.hand.cards)==0:
                self.play_end=True 
            
            # when both go reset and carry on
            if self.dealer_go is True and self.pone_go is True:
                self.table_sum = 0
                self.on_table = deck_tools.Hand()
                self.pone_go = False
                self.dealer_go = False
                self.go_added = False

            active_player  = getattr(self, self.active_player_str)
           
            if len(active_player.hand.cards)>0:
            
                active_player.the_play_method.update_hand(active_player.hand)
                active_player.the_play_method.update_on_table(self.on_table)
                
                index_to_play = active_player.the_play_method.choose_play() 
                
                if index_to_play== None: 
                    self.go()
                else:
                    
                    card_to_play= active_player.hand.cards[index_to_play]
                    active_player.hand.remove_card(card_to_play)
                    self.on_table.add_card(card_to_play)
                    self.table_sum = self.table_sum + card_to_play.face_value
                    to_add = scorer.ScoreThePlay(self.on_table).score
                    active_player.update_score(to_add)
                    out_string='' 
                    out_string += '%s plays %s  Sum : %i.\nAdd %i for %s.\n%s score : %i %s  score :%i\n'%\
                            (active_player.name,
                             card_to_play,
                             self.table_sum,
                             to_add,
                             active_player.name,
                             self.pone.name,
                             self.pone.score,
                             self.dealer.name,
                             self.dealer.score)
                    out_string += 'On table :\n%s\n'%(self.on_table.__str__())
                    self.logger(out_string)
                    self.switch_player() 
                    self.save_state()  
                    
            else:
                self.go()
                
        self.return_cards()            
        #self.get_the_play_score()
        
    def go(self):
        """ simulate the fact that active player can't play so says go"""
        active_player  = getattr(self, self.active_player_str)
        self.logger('%s said go\n'%active_player.name)
        setattr(self,self.active_player_str +'_go',True)
       
        self.switch_player()
        active_player  = getattr(self, self.active_player_str)
        self.save_state()  
        if self.go_added == False:
            active_player.update_score(1)
            self.go_added = True
            
    def switch_player(self):
        """ switch active player after a cards has been played or player says go"""
        if self.active_player_str == 'pone':
            self.active_player_str = 'dealer'
        else:
            self.active_player_str = 'pone'
    #def get_the_play_score(self):
    #    """ calculate the scores accured in the play"""
    #    self.pone_the_play_score = self.pone.score - self.pone_score_init
    #    self.dealer_the_play_score = self.dealer.score - self.dealer_score_init
    #TODO: private?        
    
    def return_cards(self):
        """ move cards from the table back to player's hands"""
        self.pone.update_hand(self.pone_hand_init)
        self.dealer.update_hand(self.dealer_hand_init)
    
    def get_state(self):
        """ save the current state as json file"""

        #first add in the non-card related fields
        state={'p1_score' : self.player_1.score,
               'p2_score' : self.player_2.score,
               'p1_dealer' : +(self.player_1.is_dealer),
               'p2_dealer' : +(self.player_2.is_dealer),
               'active_player_str'  : self.active_player_str,
               'table_sum'  : self.table_sum,
               'p1_choice_0' : None,
               'p1_choice_1' : None,
               'p2_choice_0' : None,
               'p2_choice_1' : None,
                }
        #now add in the card related fields   - default is None 
        N_cards=(6,4,8,1)
        names=(['p1_hand','p2_hand'],['crib'],['on_table'],['cut_card'])
        
        
        zipped = zip(N_cards,names)
        for item in zipped:
            for i in range(0,item[0]):
                for p in item[1]:
                    for c in ['suit','rank']:
                        state['%s_%i_%s'%(p,i,c)]=None
        """  
        for i in range(0,6):
            for p in :
                for c in ['suit','rank']:
                    state['%s_hand_%i_%s'%(p,i,c)]=None
                  
        for i in range(0,5):
            for p in ['crib']:
                for c in ['suit','rank']:
                    state['%s_%i_%s'%(p,i,c)]=None            
        for i in range(0,8):
            for p in ['on_table']:
                for c in ['suit','rank']:
                    state['%s_%i_%s'%(p,i,c)]=None
        for i in [0]:
            for p in ['cut_card']:
                for c in ['suit','rank']:
                    state['%s_%i_%s'%(p,i,c)]=None 
        """      
        names =('p1_hand','p2_hand','on_table','crib','cut_card')
        cards =(self.player_1.hand.cards,self.player_2.hand.cards,self.on_table.cards,self.crib.cards,self.cut_card.cards)
        zipped = zip(names,cards)
        for item in zipped:
            for i,card in enumerate(item[1]):
                state['%s_%i_suit'%(item[0],i)] = card.suit
                state['%s_%i_rank'%(item[0],i)] = card.rank
        """
        #now add in the cards for the current state
        for i,card in enumerate(self.player_1.hand.cards):
            state['p1_hand_%i_suit'%i] = card.suit
            state['p1_hand_%i_rank'%i] = card.rank
            
        for i,card in enumerate(self.player_2.hand.cards):
            state['p2_hand_%i_suit'%i] = card.suit
            state['p2_hand_%i_rank'%i] = card.rank
            
        for i,card in enumerate(self.crib.cards):
            state['crib_%i_suit'%i] = card.suit
            state['crib_%i_rank'%i] = card.rank
            
        for i,card in enumerate(self.cut_card.cards):        
            state['cut_card_%i_suit'%i] = card.suit
            state['cut_card_%i_rank'%i] = card.rank   
        """    
        return state    

    def save_state(self,fname=None):
        """ save the current state as json file"""
        state = self.get_state()
        if fname ==None:
            fname='state.json'
        with open(fname,'w+') as f:
            json.dump(state,f)
           
