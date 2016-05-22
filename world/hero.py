class Hero:
    """The Hero object"""

    def __init__(self, hero):
        try:
            # Training bots have no elo or userId
            self.elo = hero['elo']
            self.user_id = hero['userId']
            self.bot_last_move = hero['lastDir']
        except KeyError:
            self.elo = 0
            self.user_id = 0
            self.last_move = None

        self.bot_id = hero['id']
        self.life = hero['life']
        self.gold = hero['gold']
        self.pos = (hero['pos']['x'], hero['pos']['y'])
        self.spawn_pos = (hero['spawnPos']['x'], hero['spawnPos']['y'])
        self.crashed = hero['crashed']
        self.mine_count = hero['mineCount']
        self.mines = []
        self.name = hero['name'].encode("utf-8")

    def life_amount(self):
        return self.life / 100

    def stronger(self, other):
        if not isinstance(other, Hero):
            raise ValueError("Comparison needs another hero")

        return self.life > other.life

    def value(self):
        return self.mine_count

    def __str__(self):
        return '''
        Hero:
            Name: {}
            ID: {}
            Life: {}
            Gold: {}
            Mines: {}
        '''.format(self.name, self.bot_id, self.life, self.gold, self.mine_count)
