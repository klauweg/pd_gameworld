class Game:
    def __init__(self):
        self.players = []
        self.currentPlayer = None
        self.currentPlayerID = 0

    def start(self):
        pass

    def stop(self):
        pass

    def change_to_next_player(self):
        self.currentPlayerID += 1
        if self.currentPlayerID > self.players.__len__() - 1:
            self.currentPlayerID = 0
            self.currentPlayer = self.players[self.currentPlayerID]
            return self.currentPlayer
        self.currentPlayer = self.players[self.currentPlayerID]
        return self.currentPlayer

    def is_empty(self):
        return self.players.__len__() - 1 > 0

    def compute_winner(self):
        pass


