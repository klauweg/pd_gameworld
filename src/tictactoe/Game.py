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
            0: 99, 1: 99, 2: 99,
            3: 99, 4: 99, 5: 99,
            6: 99, 7: 99, 8: 99
        }

    def is_empty(self):
        if self.players is None:
            return True
        else:
            return False

    def compute_winner(self):
        # winning possibilities
        on_top = self.placedFields[0] + self.placedFields[1] + self.placedFields[2]
        below = self.placedFields[6] + self.placedFields[7] + self.placedFields[8]
        left = self.placedFields[0] + self.placedFields[3] + self.placedFields[6]
        right = self.placedFields[2] + self.placedFields[5] + self.placedFields[8]
        diagonal_right = self.placedFields[6] + self.placedFields[4] + self.placedFields[2]
        diagonal_left = self.placedFields[8] + self.placedFields[4] + self.placedFields[0]
        # winner check
        print(on_top, below, left, right, diagonal_left, diagonal_right)
        if on_top == 6 or below == 6 or left == 6 or right == 6 or diagonal_right == 6 or diagonal_left == 6:
            return 1
        elif on_top == 3 or below == 3 or left == 3 or right == 3 or diagonal_right == 3 or diagonal_left == 3:
            return 0
        else:
            return -1


emptyGame = Game(None)


def get_empty_game():
    return emptyGame
