import json

filename="player_data_new.json"

# Wir erzeugen einen Context Manager, welcher die JSON Daten lädt, ggf.
# die Datei erzeugt, und ggf. den Benutzer anlegt und weiterhin das Aktualisieren
# der Daten im JSON File sicher stellt.
class ModStatsData():
    def __init__(self, user_id):
        self.user_id = user_id

    def __enter__(self):  # vor der Modifikation
        try:
            file = open( filename, "r")
            self.data = json.load(file)
            file.close()
        except:
            print("File existiert nicht, leeres Dictionary erzeugen...")
            self.data = {}
        
        if self.user_id in self.data: # Existiert der Benutzer?
            self.user = self.data[self.user_id] # Daten des Benutzer extrahieren
        else:
            self.user = { "xp": 0 } # sonst neuen Benutzer mit xp=0 anlegen
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback): # nach der Modifikation
        self.data[ self.user_id ] = self.user
        with open(filename, "w") as file:
            json.dump( self.data, file, indent=4)

#############################################################################
# API Functions:
# (Nicht existierende Benutzer werden vom Context-Manager angelegt.)

# XP eines Users um bestimmten Wert erhöhen:
def add_xp(user_id , xp):
    with ModStatsData( user_id ) as data:
        data.user["xp"] += xp

# Spielstatistiken 
def add_player_stats(user_id, gamename, won ):
    with ModStatsData( user_id ) as data:
        if not gamename in data.user:  # Falls für dieses Spiel noch keine Statistik existiert
            data.user[gamename] = [ 0,0 ]   # neue Statistik anlegen
        data.user[gamename][0] += 1  # Anzahl der gesamten Spiele +1
        if won:                      # War das Spiel gewonnen?
            data.user[gamename][1] += 1  # Dann Anzahl der gewonnenen Spiele erhöhen

