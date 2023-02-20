import discord
from utils import generate_random_id

from typing import List
import random

from constants import *

class Card:
    def __init__(self, element, value, color):
        self.element = element
        self.value = value
        self.color = color

    def colorAsString(self):
        return COLORS[self.color]

    def elementAsString(self):
        return ELEMENTS[self.element]

    def __str__(self) -> str:
        return f"{self.colorAsString()} {self.elementAsString()} card with a value of {self.value}"

class Hand:
    def __init__(self):
        self.hand: List[Card] = []

    def add_card(self, card: Card):
        self.hand.append(card)

    def get_card(self, element: int, value: int):
        card = None
        for i in range(len(self.hand)):
            _card = self.hand[i]
            if _card.element == element and _card.value == value:
                card = [_card, i]
                break

        return card

    def use_card(self, element: int, value: int):
        card = self.get_card(element, value)
        # print(element, value)
        if card is None:
            return None
        self.hand.pop(card[1])
        return card

    def __str__(self) -> str:
        string = ""
        for i in range(len(self.hand)):
            card = self.hand[i]
            if i == len(self.hand) - 1:
                string += "and a "

            string += f"{str(card)}{', ' if i != len(self.hand) - 1 else '.'}"
        
        return string

class Deck:
    def __init__(self):
        self.deck: List[Card] = []

    def init_cards(self):
        for value in range(2, 12):
            for element in range(FIRE, SNOW):
                color = random.randint(RED, PURPLE)
                card = Card(element, value, color)
                self.deck.append(card)

        self.shuffle()
    
    def shuffle(self):
        self.deck = random.sample(self.deck, len(self.deck))

    def deal(self):
        card = self.deck.pop(0)
        if len(self.deck) == 0:
            self.init_cards()
        return card

class Bank:
    def __init__(self):
        self.bank: List[List[int]] = [[], [], []]
        self.winningElement = None
        self.winningColors = []

    def addCard(self, card: Card):
        if not self.containsColor(card):
            self.bank[card.element].append(card.color)

    def containsColor(self, card: Card):
        return_val = False
        for i in range(len(self.bank[card.element])):
            if self.bank[card.element][i] == card.color:
                return_val = True
        return return_val

    def hasWon(self):
        won = False
        for i in range(len(self.bank)):
            if len(self.bank[i]) >= 3:
                self.winningElement = i
                self.winningColors = self.bank[i]
                won = True
        if won:
            return True

        won = False
        for fire in range(len(self.bank[0])):
            for water in range(len(self.bank[1])):
                for ice in range(len(self.bank[2])):
                    if not won:
                        # Long if statement time
                        if self.bank[0][fire] != self.bank[1][water] and self.bank[1][water] != self.bank[2][ice] and self.bank[2][ice] != self.bank[0][fire]:
                            self.winningElement = MIXED
                            self.winningColors.append(self.bank[0][fire])
                            self.winningColors.append(self.bank[1][water])
                            self.winningColors.append(self.bank[2][ice])
                            won = True
        
        return won
    
class Match():
    def __init__(self, player_one: discord.Member, player_two: discord.Member):
        self.player_one = player_one
        self.player_two = player_two
        self.id = generate_random_id()

        self.player_one_hand = Hand()
        self.player_two_hand = Hand()

        self.player_one_bank = Bank()
        self.player_two_bank = Bank()

        self.deck = Deck()
        self.deck.init_cards()

        self.create_hand(self.player_one_hand)
        self.create_hand(self.player_two_hand)

        self.winner = None
        self.ended = False

    def create_hand(self, hand: Hand):
        for i in range(MAX_HAND):
            hand.add_card(self.deck.deal())

    def end(self):
        self.ended = True

    def setWinner(self, winner: discord.Member):
        if winner.name in [self.player_one.name, self.player_two.name]:
            self.winner = winner
            self.end()
        else:
            raise Exception("Player not in match")
