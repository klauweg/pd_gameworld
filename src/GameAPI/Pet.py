import math

class Pet():
    def __init__(self, name, xpm, mym, rarity):
        self.name = name
        self.display_name = name
        self.xp_multiply = xpm
        self.money_multiply = mym
        self.rarity = rarity

    def rename(self, new_name):
        self.display_name = new_name