from constants import (CELL_MINE, CELL_VOID, CELL_WALL, CELL_TAVERN,
                       CELL_OWN_MINE, CELL_HERO_SPAWN)


class RewardCalulator(object):
    """docstring for RewardCalulator"""

    def __init__(self, state):
        super(RewardCalulator, self).__init__()
        self.state = state

    def get_reward(self, cell):
        if cell == CELL_WALL:
            return 0
        elif cell == CELL_OWN_MINE:
            return -2.0
        elif cell == CELL_VOID:
            return -0.04
        elif cell == CELL_TAVERN:
            if self.state.hero.life < 60:
                return 50.0
            elif self.state.hero.life < 80:
                return 1.0
            else:
                return -5.0
        elif cell == CELL_MINE:
            if self.state.hero.life > 60:
                return 50.0
            elif self.state.hero.life < 60 and self.state.hero.life > 20:
                return 1.0
            else:
                return -5.0
        elif cell in range(1, 5):
            if self.state.heroes[cell].life < self.state.hero.life:
                return self.state.heroes[cell].mine_count * 10
            else:
                return 0
        elif cell == CELL_HERO_SPAWN:
            return -7.0
        else:
            return 1.0
