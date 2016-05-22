#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .hero import Hero
from constants import (CELL_MINE, CELL_OWN_MINE, CELL_VOID, CELL_WALL,
                       CELL_TAVERN, CELL_HERO_SPAWN)


class State:
    """The game object that gather
    all game state informations"""

    def __init__(self, state):
        self.mines = {}
        self.spawn_points = {}
        self.taverns = {}
        self.heroes = {}
        self.walls = {}
        self.board_map = []
        self.turn = None
        self.max_turns = None
        self.finished = None
        self.board_size = None
        self.void = {}
        self.hero = Hero(state['hero'])
        self.url = state['viewUrl']
        self.process_state(state["game"])

    def process_state(self, state):
        """Process the game data"""
        process = {'board': self.process_board, 'heroes': self.process_heroes}
        self.turn = state['turn']
        self.max_turns = state['maxTurns']
        self.finished = state['finished']
        self.process_board(state['board'])
        self.process_heroes(state['heroes'])

    def process_board(self, board):
        """Process the board datas
            - Retrieve walls locs, tavern locs
            - Converts tiles in a displayable form"""
        self.board_size = board['size']
        tiles = board['tiles']
        char = None
        for y in range(0, len(tiles), self.board_size * 2):
            line = tiles[y:y + self.board_size * 2]
            map_line = []
            for x in range(0, len(line), 2):
                tile = line[x:x + 2]
                tile_coords = (y / self.board_size / 2, x / 2)
                if tile[0] == " ":
                    # It's passable
                    map_line.append(CELL_VOID)
                    self.void[tile_coords] = True
                elif tile[0] == "#":
                    # It's a wall
                    map_line.append(CELL_WALL)
                    self.walls[tile_coords] = True
                elif tile[0] == "$":
                    # It's a mine
                    if tile[1] == str(self.hero.bot_id):
                        # This mine is belong to me:-)
                        self.hero.mines.append(tile_coords)
                        map_line.append(CELL_OWN_MINE)
                    else:
                        map_line.append(CELL_MINE)

                    self.mines[tile_coords] = tile[1]
                elif tile[0] == "[":
                    # It's a tavern
                    map_line.append(CELL_TAVERN)
                    self.taverns[tile_coords] = True
                elif tile[0] == "@":
                    # It's a hero, append their ID
                    map_line.append(int(tile[1]))
            self.board_map.append(map_line)

    def process_heroes(self, heroes):
        """Add heroes"""
        for hero in heroes:
            hero = Hero(hero)
            self.spawn_points[hero.spawn_pos] = hero.bot_id
            self.heroes[hero.bot_id] = hero

            # Add spawn points to map if there is not a hero on top of it
            x, y = hero.spawn_pos
            if self.board_map[x][y] not in range(1, 5):
                self.board_map[x][y] = CELL_HERO_SPAWN

    def __str__(self):

        def border():
            border = ""
            for i in range(len(self.board_map[0]) + 2):
                border += "#"
            return "{}\n".format(border)

        def str_map():
            str = ""
            mapper = {CELL_WALL: "#",
                      CELL_MINE: "$",
                      CELL_VOID: " ",
                      CELL_TAVERN: "T",
                      CELL_OWN_MINE: "%",
                      CELL_HERO_SPAWN: "X",
                      1: "1",
                      2: "2",
                      3: "3",
                      4: "4"}

            for line in self.board_map:
                str += "#{}#\n".format("".join([mapper[c] for c in line]))

            return str

        return "{}{}{}".format(border(), str_map(), border())
