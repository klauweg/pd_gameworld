import discord


class Game:
    def __init__(self, players):
        self.players: list = players
        self.currentPlayer = None
        self.fields = {
            "A1": 0, "B1": 1, "C1": 2,
            "A2": 3, "B2": 4, "C3": 5,
            "A3": 6, "B3": 7, "C3": 8
        }
        self.placedFields = {
            0: -1, 1: -1, 2: -1,
            3: -1, 4: -1, 5: -1,
            6: -1, 7: -1, 8: -1
        }

    async def is_empty(self):
        if self.players is None:
            return True
        else:
            return False

    async def compute_winner(self):
        # winning possibilities
        on_top = self.placedFields[0] + self.placedFields[1] + self.placedFields[2]
        below = self.placedFields[6] + self.placedFields[7] + self.placedFields[8]
        left = self.placedFields[0] + self.placedFields[3] + self.placedFields[6]
        right = self.placedFields[2] + self.placedFields[5] + self.placedFields[8]
        diagonal_right = self.placedFields[6] + self.placedFields[4] + self.placedFields[2]
        diagonal_left = self.placedFields[8] + self.placedFields[4] + self.placedFields[0]
        # winner check
        if on_top is 3 or below is 3 or left is 3 or right is 3 or diagonal_right is 3 or diagonal_left:
            return 1
        if on_top is 0 or below is 0 or left is 0 or right is 0 or diagonal_right is 0 or diagonal_left:
            return 0

        return -1


empty_game = Game(None)
