import logging

class Queue:
    __queued_members={}   # member.id -> queuename
    __playing_members={}  # member.id -> gamename (=queuename)
    
    def __init__(self, name):
        self.queuename = name
        self.queue = []
        self.on_queue_change = None # Callbackfunktion für die Gamecontroller

    # Wenn sich der Inhalt der Queue verändert:
    def do_on_queue_change( self ):
        logger.info( self.queuename + "queue changed:" )
        logger.info( "  queued members: " + str(Queue.__queued_members) )
        logger.info( "  playing members: " + str(Queue.__playing_members) )
        logger.info( "  queue content: " + str(self.queue) )
        # Die vom Gamecontroller registrierte Callbackfunktion ausführen
        self.on_queue_change()
    
########## Queue INPUT

    # Neue Spieler in die Queue
    async def append(self, ctx):
        if ctx.author.id in Queue.__queued_members:
            await ctx.channel.send( str( ctx.author ) + 
                                    " ist schon in der queue " + 
                                    str(Queue.__queued_members[ ctx.author.id ]), delete_after=10)
        elif ctx.author.id in Queue.__playing_members:
            await ctx.channel.send( str( ctx.author ) + 
                                    " spielt schon " + 
                                    str(Queue.__playing_members[ ctx.author.id ]), delete_after=10)
        else:
            Queue.__queued_members[ ctx.author.id ] = self.queuename
            self.queue.append(ctx)
            self.do_on_queue_change()

    # Spieler verlässt die Queue selbst:
    async def remove(self, ctx):
        if ctx.author.id in Queue.__queued_members:
            Queue.__queued_members.pop( ctx.author.id )
            self.queue = [ x  for x in self.queue  if x.author.id != ctx.author.id ]
            await ctx.channel.send( str( ctx.author ) + 
                                    " verlässt die Queue " + self.name, delete_after=10 )
            self.do_on_queue_change()
            
                                    
############ Queue OUTPUT

    def len(self):
        return len(self.queue)
    
    # Wenn ein Spiel beendet ist, muss diese funktion aufgerufen werden:
    # Das kann letztlich das Spiel nur selbst machen, da es möglich ist, dass
    # Spieler aus einem Spiel ausscheiden, bevor das Spiel komplett beendet ist.
    def release_player(self, playerid):
        Queue.__playing_members.pop( playerid )
        
    # Hier holen die Spiele ihre Player (contexte) aus der Queue:
    # Der Member kommt aus der queued liste in die playing liste
    def pop(self):
        ctx = self.queue.pop(0)
        Queue.__queued_members.pop( ctx.author.id )
        Queue.__playing_members[ ctx.author.id ] = self.queuename
        self.do_on_queue_change()
        return ctx
    


