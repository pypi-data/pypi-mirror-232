## PyCribbage

PyCribbage is a Python application for playing a card game called Cribbage. It was created to demonstrate my ability to apply OOP concepts, follow a TDD process and apply SOLID coding principles.

An overview of the rules of the game and the terminology used can be found here : https://www.theukrules.co.uk/rules/children/games/cards/cribbage.html

## Installation

PyCribbage was created with Python 3.8.5, but it should work with Python 3+. 
There are no additional dependencies required so one should one be able to use this library with a standard Python 3.8.5 installation. 

```
mkdir cribbage
cd cribbage
git clone https://github.com/jotter91/PythonCribbage
```

To run the tests then there are some additional packages required, please see requirements_dev.txt. These can be installed as follows:

```
python -m venv .venv/
source .venv/bin/activate # Line to enter before any commands below
python -m pip install -r requirements_dev.txt
```



## Usage

To play an interactive game launch main.py and follow the on screen prompts

```
python pycribbage/main.py
```

The prompts will ask for information on which methods to use. The methods are split into the two parts of a cribbage game, The Show and The Play. Currently your opponent can use either a random choice during the game or a repeatable choice (useful for replaying the same game). 

If you would like to play a computer player then enter the information as follows: 
```
Enter the name for the 1 Player:
Human
Enter the method for this player's 'The Show'
[0] For Fixed index
[1] For Random
[2] For Human
2
Enter the method for this player's 'The Play'
[0] For Fixed index
[1] For Random
[2] For Human
2
Enter the name for the Second Player:
Bot
Enter the method for this player's 'The Show'
[0] For Fixed index
[1] For Random
[2] For Human
1
Enter the method for this player's 'The Play'
[0] For Fixed index
[1] For Random
[2] For Human
1
```

To run the tests : 

```
python -m pytest tests
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
