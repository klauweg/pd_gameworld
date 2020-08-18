class Queue:
    __occupied_players=[]

    def __init__(self):
        self.queue = []
        self.add_action = None # Callbackfunktion für die Spiele

    async def append(self, ctx):
        if ctx.author in Queue.__occupied_players:
            await ctx.channel.send( str( ctx.author ) + " ist schon in einer Queue", delete_after=10)
        else:
            Queue.__occupied_players.append( ctx.author)
            self.queue.append(ctx)
            await self.add_action()  # Callbackfunktion ausführen

    def release_player(self, player):
        self.__occupied_players.remove( player )

    def pop(self):
        return self.queue.pop(0)

    def len(self):
        return len(self.queue)
