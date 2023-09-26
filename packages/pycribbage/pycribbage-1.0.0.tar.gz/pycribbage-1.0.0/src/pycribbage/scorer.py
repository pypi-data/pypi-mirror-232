from copy import deepcopy
#TODO: make some parts protected
#TODO: make some parts static
#TODO: breakdown into components of score 
#TODO: func to return the score 
#TODO: __repr__ and __str__
class ScoreTheShow():
    """
    A class used to score the show phase of Cribbage
    
    ...

    Attributes
    ----------
    hand : Hand 
        a Hand object that represents the hand to be scored
    is_crib : bool
        flag to check if the hand being scored is a crib, 
        as this changes the 'calculate_flush' rules
    check_nobs : bool
        flag to check if 'nobs' for Jacks should be checked    
    check_suits : bool
        flag to check for flushes
    score : int
        the resultant score of the hand  
        
    Methods
    -------
    calculate_15s()
        Check and score 15s 
    calculate_pairs_etc()
        Check and Score pairs, three of kind and four of kind 
    calculate_runs()
        Check and score runs    
    calculate_flush()
        Check and score flushes 
    calculate_nobs()
        Check and score nobs  
    create_15_sets()
        Create sets for finding 15s
    """
    def __init__(self,hand,is_crib=False,check_suits=True,check_nobs=True):
        """
        Parameters
        ----------
        hand : Hand 
            a Hand object that represents the hand to be scored.
            Note that the cut card must be the last card in the hand
        is_crib : bool
            flag to check if the hand being scored is a crib, 
            as this changes the 'calculate_flush' rules
            Note that the cut card must be the last card in the crib
        check_suits : bool
            flag to check for flushes    
        check_nobs : bool
            flag to check if 'nobs' for Jacks should be checked    
        """
        self.hand = deepcopy(hand) # deepcopy to avoid changing
        
        self.is_crib=is_crib 
        self.check_suits= check_suits
        self.check_nobs=check_nobs
        self.score= 0
        
        
        self.hand.count() 
        self.calculate_15s() 
        self.calculate_pairs_etc()
        self.calculate_runs()
        
        if check_suits==True:
            self.calculate_flush() 
        if check_nobs ==True:
            self.calculate_nobs()
    
    def calculate_flush(self):
        """ Check and score flushes - different behaviour if crib"""
        
        if self.is_crib is False:
            if self.hand.cards[0].suit == self.hand.cards[1].suit == self.hand.cards[2].suit == self.hand.cards[3].suit:
                self.score = self.score + 4
                if self.hand.cards[3].suit == self.hand.cards[4].suit:
                    self.score = self.score + 1
        
        if self.is_crib is True:
            if self.hand.cards[0].suit == self.hand.cards[1].suit == self.hand.cards[2].suit == self.hand.cards[3].suit == self.hand.cards[4].suit:
                self.score = self.score + 5
                
    #does this function need to be in class?
    #TODO make static 
    def create_15_sets(self):  
        """ Create sets for finding 15s"""
        sets = []
        sets.append([0, 1])
        sets.append([0, 2])
        sets.append([0, 3])
        sets.append([0, 4])
        sets.append([1, 2])
        sets.append([1, 3])
        sets.append([1, 4])
        sets.append([2, 3])
        sets.append([2, 4])
        sets.append([3, 4])
        sets.append([0, 1, 2])
        sets.append([0, 1, 3])
        sets.append([0, 2, 3])
        sets.append([1, 2, 3])
        sets.append([0, 1, 4])
        sets.append([0, 2, 4])
        sets.append([1, 2, 4])
        sets.append([0, 3, 4])
        sets.append([1, 3, 4])
        sets.append([2, 3, 4])
        sets.append([0, 1, 2, 3])
        sets.append([0, 1, 2, 4])
        sets.append([0, 1, 3, 4])
        sets.append([0, 2, 3, 4])
        sets.append([1, 2, 3, 4])
        sets.append([0, 1, 2, 3, 4])
    
        return sets


    def calculate_15s(self):
        """ Check and Score 15s"""
        
        sets_15 = self.create_15_sets()
        
        for set in sets_15:
            sum = 0
            for index in set:
                sum = sum + self.hand.cards[index].face_value
            if sum == 15:
                self.score= self.score +2
 
    def calculate_runs(self):  
        """Check and score runs """
        c=self.hand.hand_count
        for i in range(5, 14):
            if c[str(i)] == c[str(i - 1)] == c[str(i - 2)] == c[str(i - 3)] == c[str(i - 4)] == 1:
                p = c[str(i)] * c[str(i - 1)] * c[str(i - 2)] * c[str(i - 3)] * c[str(i - 4)]
                s = p * (i - (i - 4) + 1)
                self.score = self.score +s
                return 
        for i in range(4, 14):
            if c[str(i)] >= 1 and c[str(i - 1)] >= 1 and c[str(i - 2)] >= 1 and c[str(i - 3)] >= 1:
                p = c[str(i)] * c[str(i - 1)] * c[str(i - 2)] * c[str(i - 3)]
                s = p * (i - (i - 3) + 1)
                self.score = self.score +s
                return 
        for i in range(3, 14):
            if c[str(i)] >= 1 and c[str(i - 1)] >= 1 and c[str(i - 2)] >= 1:
                p = c[str(i)] * c[str(i - 1)] * c[str(i - 2)]
                s = p * (i - (i - 2) + 1)
                self.score = self.score +s
                return 

    def calculate_pairs_etc(self):
        """ Check and Score pairs, three of kind and four of kind"""
        for i in range(1, 14):
            if self.hand.hand_count[str(i)] == 4:
                self.score = self.score + 12
            if self.hand.hand_count[str(i)] == 3:
                self.score = self.score + 6
            if self.hand.hand_count[str(i)] == 2:
                self.score = self.score + 2
    
    def calculate_nobs(self):
        """Check and score nobs  """
        
        if self.hand.hand_count['11'] > 0:
            for card in self.hand.cards[0:4]:
                if card.rank == 11 and card.suit == self.hand.cards[4].suit:
                    self.score = self.score + 1

#TODO : return score function? rather than accessing an attribute
class ScoreThePlay():
    """
    A class used to score the play phase of Cribbage
    Note that scoring 'go' is not included in this class, it is instead
    included in ThePlay class
    
    
    
    ...

    Attributes
    ----------
    on_table : Hand 
        a Hand object that represents the cards on the table to be scored
    score : int
        the resultant score of the hand  
    n : int
        the number of cards on the table
    over_31 : bool
        flag to determine if the sum of the table is over 31
        
    Methods
    -------
    calculate_sum()
        calculate sum of cards on the table -also check for 15s and 31s
    calculate_pairs()
        Check and Score pairs, three of kind and four of kind 
    calculate_runs()
        Check and score runs    
    """
    def __init__(self,on_table):
        """
        Parameters
        ----------
        on_table : Hand 
            a Hand object that represents the cards on the table to be scored
  
        """
        self.on_table = deepcopy(on_table)
        self.score=0
        self.n = len(self.on_table.cards)
        self.over_31= False
        
        self.on_table.count()
        self.calculate_sum()
        
        if self.over_31 is False:
            self.calculate_pairs()
            self.calculate_runs()
        else:
            self.score=-1
    
    def calculate_runs(self):
        """  Check and score runs   """
        
        lowest = 13
        highest = 1
        n=self.n
        for i in range(n, 0, -1):
            # pairs breaks run
            if self.on_table.hand_count[str(self.on_table.cards[i-1].rank)] > 1:
                return 
            else:
                if self.on_table.cards[i - 1].rank < lowest:
                    lowest = self.on_table.cards[i - 1].rank
                if self.on_table.cards[i - 1].rank > highest:
                    highest = self.on_table.cards[i - 1].rank
                if (highest - lowest) == (n - i):
                    run_score = highest - lowest + 1

        if run_score > 2:
           self.score = self.score + run_score 


    def calculate_pairs(self):
        """ Check and Score pairs, three of kind and four of kind """
        n=self.n
        
        if (self.on_table.cards[n - 1].rank == self.on_table.cards[n - 2].rank) and n > 1:
            self.score = self.score + 2
            
            if (self.on_table.cards[n - 2].rank == self.on_table.cards[n - 3].rank) and n > 2:
                self.score = self.score + 4
                
                if (self.on_table.cards[n - 3].rank == self.on_table.cards[n - 4].rank) and n > 3:
                    self.score = self.score + 6
    
    def calculate_sum(self):
        """ calculate sum of cards on the table """
        cards_sum = 0
        n=self.n
        for i in range(0, n):
            cards_sum = cards_sum + self.on_table.cards[i].face_value
        #TODO: this function is doing more than one thing!!    
        if cards_sum == 15:
            self.score = self.score + 2
        if cards_sum == 31:
            # one is given for a 31, the point for the go is then given in ThePlay class/function
            self.score = self.score + 1
        if cards_sum > 31:
            self.over_31 = True
            



    
