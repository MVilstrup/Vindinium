#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bot import Bot
import sys
import select
import time
import os
import ast
from random import shuffle

TIMEOUT = 15


class Config:

    def __init__(self,
                 game_mode="training",
                 server_url="http://vindinium.org",
                 number_of_games=1,
                 number_of_turns=300,
                 map_name="m2",
                 key=None):
        self.game_mode = game_mode
        self.number_of_games = number_of_games
        self.number_of_turns = number_of_turns
        maps = ["m1", "m2", "m3", "m4", "m5", "m6"]
        shuffle(maps)
        self.map_name = maps.pop()
        self.server_url = server_url
        self.key = key


class Client:

    def __init__(self):
        self.start_time = None
        self.gui = None
        self.session = None
        self.state = None
        self.running = True
        self.game_url = None
        self.config = Config()
        self.bot = Bot()  # Our bot
        self.states = []
        self.delay = 0.5  # Delay in s between turns in replay mode
        self.victory = 0
        self.time_out = 0

    def pprint(self, *args, **kwargs):
        """Display args in the bot gui or
        print it if no gui is available
        For debugging purpose consider using self.gui.append_log()
        """
        printable = ""
        for arg in args:
            printable = printable + str(arg) + " "
        if kwargs and len(kwargs):
            a = 1
            coma = ""
            printable = printable + "["
            for k, v in kwargs.iteritems():
                if 1 < a < len(kwargs):
                    coma = ", "
                else:
                    coma = "]"
                printable = printable + str(k) + ": " + str(v) + coma
                a = a + 1
        if self.gui and self.gui.running:
            # bot has a gui so we add this entries to its log panel
            if self.gui.log_win:
                self.gui.append_log(printable)
                self.gui.refresh()
        else:
            print(printable)

    def play(self):
        """Play all games"""
        self.victory = 0
        self.time_out = 0
        for i in range(self.config.number_of_games):
            # start a new game
            if self.bot.running:
                self.start_game()
                gold = 0
                winner = ("Noone", -1)
                for player in self.bot.state.heroes.values():
                    print(player)
                    if int(player.gold) > gold:
                        winner = (player.name, player.bot_id)
                        gold = int(player.gold)
                if winner[1] == self.bot.state.hero.bot_id:
                    self.victory += 1
                self.pprint("* " + winner[0] + " wins. ******************")
                self.pprint("Game finished: " + str(i + 1) + "/" + str(
                    self.config.number_of_games))

    def start_game(self):
        """Starts a game with all the required parameters"""
        self.running = True
        # Delete prévious game states
        self.states = []
        # Restart game with brand new bot
        self.bot = Bot()
        # Default move is no move !
        direction = "Stay"
        # Create a requests session that will be used throughout the game
        self.pprint('Connecting...')
        self.session = requests.session()
        if self.config.game_mode == 'arena':
            self.pprint('Waiting for other players to join...')
        try:
            # Get the initial state
            # May raise error if self.get_new_state() returns
            # no data or inconsistent data (network problem)
            self.state = self.get_new_game_state()
            self.states.append(self.state)
            self.pprint("Playing at: " + self.state['viewUrl'])
        except (KeyError, TypeError) as e:
            # We can not play a game without a state
            self.pprint("Error: Please verify your settings.")
            self.pprint("Settings:", self.config.__dict__)
            self.running = False
            return
        for i in range(self.config.number_of_turns + 1):
            if self.running:
                # Choose a move
                self.start_time = time.time()
                while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = sys.stdin.read(1)
                    if line.strip() == "q":
                        self.running = False
                        self.bot.running = False
                        break
                if self.bot.running:
                    direction = self.bot.move(self.state)
                if not self.is_game_over():
                    # Send the move and receive the updated game state
                    self.game_url = self.state['playUrl']
                    self.state = self.send_move(direction)
                    self.states.append(self.state)

        # Clean up the session
        self.session.close()

    def get_new_game_state(self):
        """Get a JSON from the server containing the current state of the game"""
        if self.config.game_mode == 'training':
            # Don't pass the 'map' parameter if no map has been selected
            if len(self.config.map_name) > 0:
                params = {'key': self.config.key,
                          'turns': self.config.number_of_turns,
                          'map': self.config.map_name}
            else:
                params = {'key': self.config.key,
                          'turns': self.config.number_of_turns}
            api_endpoint = '/api/training'
        else:
            params = {'key': self.config.key}
            api_endpoint = '/api/arena'
        # Wait for 10 minutes
        try:
            r = self.session.post(self.config.server_url + api_endpoint,
                                  params,
                                  timeout=10 * 60)
            if r.status_code == 200:
                return r.json()
            else:
                self.pprint("Error when creating the game:", str(r.status_code))
                self.running = False
                self.pprint(r.text)
        except requests.ConnectionError as e:
            self.pprint("Error when creating the game:", e)
            self.running = False

    def is_game_over(self):
        """Return True if game defined by state is over"""
        try:
            return self.state['game']['finished']
        except (TypeError, KeyError):
            return True

    def send_move(self, direction):
        """Send a move to the server
        Moves can be one of: 'Stay', 'North', 'South', 'East', 'West'"""
        try:
            response = self.session.post(self.game_url,
                                         {'dir': direction},
                                         timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            else:
                self.pprint("Error HTTP ", str(response.status_code), ": ",
                            response.text)
                self.time_out += 1
                self.running = False
                return {'game': {'finished': True}}
        except requests.exceptions.RequestException as e:
            self.pprint("Error at client.move;", str(e))
            self.running = False
            return {'game': {'finished': True}}


if __name__ == "__main__":
    client = Client()
    # Go for interactive setup
    client.config.game_mode = "training"
    #client.config.game_mode = "arena"
    client.config.key = open("code.log", "r").readlines()[0].strip()
    client.config.number_of_games = 1
    client.config.number_of_turns = 50  # Ignored in arena mode
    client.play()
