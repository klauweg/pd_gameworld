from GameAPI.PlayerAPI import FileManager
import logging


def add_xp(user_id, xp):
    if not FileManager.exists_player(user_id):
        logging.error("[GameAPI] Player does not exists.")
    FileManager.update_player_data(user_id, "xp", FileManager.get_player_data(user_id).xp + xp)


def remove_xp(user_id, xp):
    add_xp(user_id, -xp)


def compute_wl(user_id, game: str):
    game_stats = FileManager.get_field(user_id, game)
    wl = 0
    if game_stats[1] == 0:
        wl = game_stats[0]
        return wl
    wl = game_stats[0] / game_stats[1]
    return wl


def add_to_stats(user_id, game: str, wins=0, loses=0, played=0):
    if not FileManager.exists_player(user_id):
        logging.error("[GameAPI] Player does not exists.")
    game_stats = FileManager.get_field(user_id, game)
    new_stats = (game_stats[0] + wins, game_stats[1] + loses, game_stats[2] + played,
                 compute_wl(user_id, game))
    FileManager.update_player_data(user_id, game, new_stats)
