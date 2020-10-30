import asyncio
import logging

import discord

from GameAPI.PlayerDataApi import Utils


class Queue:
    __queued_members={}   # member.id -> queuename
    __playing_members={}  # member.id -> gamename (=queuename)
    
    def __init__(self, name, channel):
        self.channel = channel
        self.queue_message = None
        self.queuename = name
        self.queue = []
        self.on_queue_change = None # Callbackfunktion für die Gamecontroller
        logging.info( "Queue für "+self.queuename+" erstellt." )

    # Wenn sich der Inhalt der Queue verändert:
    def do_on_queue_change( self ):
        logging.info( self.queuename + " queue changed:" )
        logging.info( "  queued members: " + str(Queue.__queued_members) )
        logging.info( "  playing members: " + str(Queue.__playing_members) )
        logging.info( "  queue content: " + str(self.queue) )

        asyncio.create_task(self.send_queue_message())


        # Die vom Gamecontroller registrierte Callbackfunktion ausführen
        self.on_queue_change()

    async def send_queue_message(self):
        if self.queue_message:
            try:
                await self.queue_message.delete()
            except:
                pass

        embed = discord.Embed(title="Queue:", description="", color=0x58ff46)
        embed.set_author(name="Queue",icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.add_field(name="Im Moment in der Queue:",
                        value=', '.join([ ctx.author.name for ctx in self.queue ]) + " !",
                        inline=True)
        self.queue_message = await self.channel.send(embed=embed)
    
########## Queue INPUT

    # Neue Spieler in die Queue
    async def append(self, ctx):
        if ctx.author.id in Queue.__queued_members:
            embed = discord.Embed(title="Achtung, " + ctx.author.name +"!", description="Du bist bereits in der Queue von " + str(Queue.__queued_members[ ctx.author.id ]),color=0x49ff35)
            embed.set_author(name=self.queuename,icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
        elif ctx.author.id in Queue.__playing_members:
            embed = discord.Embed(title="Achtung, " + ctx.author.name +"!", description="Du spielst bereits in " + str(Queue.__playing_members[ ctx.author.id ]),color=0x49ff35)
            embed.set_author(name=self.queuename,icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=7)
        else:
            Queue.__queued_members[ ctx.author.id ] = self.queuename
            self.queue.append(ctx)
            embed = discord.Embed(title="Nice!", description=f"""{ctx.author.name} hat die Queue betreten""",color=0x49ff35)
            embed.set_author(name=self.queuename,icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=3)
            self.do_on_queue_change()

    # Spieler verlässt die Queue selbst:
    async def remove(self, ctx):
        if ctx.author.id in Queue.__queued_members:
            Queue.__queued_members.pop( ctx.author.id )
            self.queue = [ x  for x in self.queue  if x.author.id != ctx.author.id ]
            embed = discord.Embed(title="Bis bald!", description=f"""{ctx.author.name} hat die Queue verlassen""",color=0x49ff35)
            embed.set_author(name=self.queuename,icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
            await ctx.channel.send(embed=embed, delete_after=3)
            self.do_on_queue_change()
            
                                    
############ Queue OUTPUT

    def len(self):
        return len(self.queue)

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
    


