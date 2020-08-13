import json
from GameAPI.utils import Players
import logging


def add_player_data(player: Players.Player):
    if get_player_data(player.user_id) is None:
        player_stats: Players.PlayerStats = player.player_stats
        player_object = {player.user_id: {"xp": player.xp, "TicTacToe": player_stats.tictactoe,
                                          "Connect4": player_stats.connect4, "Hangman": player_stats.hangman}}
        json.dump(player_object, open("../resources/player_data.json", "w+"))
    else:
        logging.error("[GameAPI] Cant add player that already exists.")
        return


def get_player_data(userID):
    player_object = json.load(open("../resources/player_data.json", "r+"))[str(userID)]
    if player_object is None:
        return None
    player_stats = Players.PlayerStats()
    player_stats.tictactoe = player_object["TicTacToe"]
    player_stats.connect4 = player_object["Connect4"]
    player_stats.hangman = player_object["Hangman"]
    player = Players.Player(userID, player_object["xp"], player_stats)
    return player


def update_player_data(userID, field_name: str, new_field_value):
    if get_player_data(userID) is None:
        logging.error("[GameAPI] Player does not exists.")
    player_object = get_player_data(userID).to_json()
    player_object[str(userID)][field_name] = new_field_value
    json.dump(player_object, open("../resources/player_data.json", "r+"))
