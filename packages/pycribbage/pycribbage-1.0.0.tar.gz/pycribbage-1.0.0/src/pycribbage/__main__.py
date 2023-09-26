"""PyCribbage Main Script

Script to read the inputs for Cribbage game from the user

The user will input information for two players

    -Name : A string which will identify the player

    -TS_method : an integer which selects which Discard method to use.
                currently only two methods are supported
                0 - for the default fixed indices (see discard_methods module)
                1 - for a random indices  (see discard_methods module)
                2 - for a human choice  (see discard_methods module)

    -TP_method : an integer which selects which ThePlay method to use.
                currently only two methods are supported
                0 - for the default fixed index (see the_play_methods module)
                1 - for a random index  (see the_play_methods module)
"""
from pycribbage.cribbage_game import CribbageGame
from pycribbage.player import Player
import pycribbage.discard_methods as discard_methods
import pycribbage.the_play_methods as the_play_methods

def check_the_show_method(method):
    """Check to make sure the show method input is correct

    Parameters
    ----------
    method : str
         str which contains a number that corresponds to the method to be used

    Returns
    ------
    method : str
        A str which contains a number that corresponds to the method to be used
    """
    if method == '0' or method == '1' or method == '2':
        return method
    else:
        print('Error in TS input : Please Enter 0, 1 or 2\n')
        return -1


def check_the_play_method(method):
    """Check to make sure the play method input is correct

    Parameters
    ----------
    method : str
         str which contains a number that corresponds to the method to be used

    Returns
    ------
    method : str
        A str which contains a number that corresponds to the method to be used
    """

    if method == '0' or method == '1' or method == '2':
        return method
    else:
        print(method)
        print('Error in TP input : Please Enter 0 ,1 or 2\n')
        return -1


def check_player_name(name):
    """Check to make sure the player name is a string

    Parameters
    ----------
    name : str
         str which contains a the proposed name

    Returns
    ------
    name : str
        A str which contains the name
    """
    if isinstance(name, str):
        return name
    else:
        print('Player name should be a string')
        return -1


def read_players():
    """Reads in the information required to init the game's players

    Returns
    ------
    players : list
        A list containing two player objects for player 1 and 2 respectively
    """

    players = []
    for i, insert in ([0, 1], ['First', 'Second']):

        player_name = -1
        while player_name == -1:
            player_name = input('Enter the name for the %s Player: \n' % insert)
            player_name = check_player_name(player_name)

        TS_method = -1
        while TS_method == -1:
            TS_method = input("Enter the method for this player's 'The Show'\n"
                              + "[0] For Fixed index \n"
                              + "[1] For Random \n"
                              + "[2] For Human \n")
            TS_method = check_the_show_method(TS_method)

        TP_method = -1
        while TP_method == -1:
            TP_method = input("Enter the method for this player's 'The Play'\n"
                              + "[0] For Fixed index \n"
                              + "[1] For Random \n"
                              + "[2] For Human \n")
            TP_method = check_the_play_method(TP_method)

        if TS_method == '0':
            ts_method = discard_methods.Discard()
        elif TS_method == '1':
            ts_method = discard_methods.RandomDiscard()
        elif TS_method == '2':
            ts_method = discard_methods.HumanDiscard()

            # load in the play method
        if TP_method == '0':
            tp_method = the_play_methods.ThePlayMethod()
        elif TP_method == '1':
            tp_method = the_play_methods.RandomThePlay()
        elif TP_method == '2':
            tp_method = the_play_methods.HumanThePlay()


        player = Player(player_name, ts_method, tp_method)

        players.append(player)

    return players


def main():
    players = read_players()
    game = CribbageGame(players)
    game.play_game()


if __name__ == "__main__":
    main()