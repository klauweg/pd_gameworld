import logging
logger = logging.getLogger("party")

import asyncio
import discord
from discord.ext import commands
import weakref

### User Modules
from myclient import client, MyEmbed
import Games.tictactoe as tictactoe
import Games.connectfour as connectfour

partys = {}

class Party():
    def __init__(self, channel, owner):
        self.partychannel = channel
        self.owner = owner
        self.members = []
        self.playing = False
        self.invite_messages = []

    def __del__(self):
        logger.info("Party of {} deleted.".format( self.owner.name ) )
        
                
##############################################################################
# Party commands:
class PartyCog( commands.Cog ):
    # Aufräumen beim Start:
    @commands.Cog.listener()
    async def on_ready( self ):
        for channel in client.get_all_channels():
            if "party" in channel.name:
                logger.info("delete " + channel.name)
                await channel.delete()
                    
    # Party Commands:
    @commands.group()
    async def party(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid party command...")

    # Start eines Spiels:
    @party.command()
    async def play(self, ctx, *args):
        party = partys.get( ctx.channel, None )
        if not party:
            return # Der Channel ist keine Party
        gamename = args[0]
        logger.info("Trying to start: "+str(gamename))
        if gamename in "tictactoe":
            tictactoe.Game( client, party.partychannel, [ ctx.author, ctx.author ] )
        elif gamename in "connectfour":
            connectfour.Game( party.partychannel, ctx.author, ctx.author )

    # Party CREATE
    @party.command()
    async def create(self, ctx, *args):
        for party in partys:
            if (ctx.author in party.members) or (ctx.author == party.owner):
                embed = MyEmbed(name="Party", title=ctx.author.name + 
                   ", du bist bereits in einer Party!",
                   description="( Geh in den Party Channel"
                   "und schreibe !party leave )",
                   color=0xFF0000)
                await ctx.channel.send(embed=embed, delete_after=7)
                return

        owner = ctx.author
        # Partychannel erstellen:
        partychannel = await client.guilds[0].create_text_channel(
           name=owner.name + "'s Party",
           category=client.get_channel(773935446732308502))
        partys[partychannel] = Party(partychannel, owner) # Party erstellen
        # Benachrichtigen:
        role = client.guilds[0].get_role(741823660188500008)
        await partychannel.set_permissions(role, read_messages=False)
        await partychannel.set_permissions(owner, read_messages=True)
        embed = MyEmbed(title="Party erfolgreich erstellt!",
           description="",
           color=0x00FF00)
        await ctx.channel.send(embed=embed, delete_after=7)
        logger.info("Party Created by {}.".format( ctx.author.name ))

    # INVITE to Party
    @party.command()
    async def invite(self, ctx, *args):
        party = partys.get( ctx.channel, None )
        if not party:
            return # Der Channel hat keine Party
        if ctx.author != party.owner:
            return # Der User ist nicht der Owner
        if len( party.members ) >= 10:
            embed = MyEmbed(name="Party",
              title="Du hast die maximale Anzahl an Spielern "
              "in deiner Party erreicht!",
              description="( Werfe einen Spieler aus der "
              "Party um neue einzuladen! )",
              color=0xFF0000)
            await party.partychannel.send(embed=embed, delete_after=7)
            return # Maximale Spielerzahl erreicht
        member = ctx.guild.get_member_named(args[0])
        if not member:
            embed = MyEmbed(name="Party",
              title="Dieser Spieler existiert nicht",
              description="( Groß und klein Schreibung beachten! )",
              color=0xFF0000)
            await party.partychannel.send(embed=embed, delete_after=7)
            return # Der einzuladende Spieler existiert nicht
        if member in party.members:
            embed = MyEmbed(name="Party", 
               title="Der Spieler ist bereits in deiner Party!",
               description="",
               color=0xFF0000)
            await party.partychannel.send(embed=embed, delete_after=7)
            return # Spieler kann immer nur in einer Party sein
        # Einladen:
        embed = MyEmbed(name="Party",
           title="Der Spieler " + party.owner.name +
           " hat dich in eine Party eingeladen!",
           description="( Klicke auf den Haken um "
           "die Einladung zu akzeptieren )",
           color=0x00FF00)
        invite_message = await member.send(embed=embed)
        await invite_message.add_reaction("🚫")
        await invite_message.add_reaction("✅")
        party.invite_messages.append(invite_message)

        embed = MyEmbed(name="Party", title="Der Spieler " +
              member.name + " wurde in die Party eingeladen!",
              description="Bitte warte, bis er die "
              "Einladung akzeptiert", color=0x00FF00)
        await party.partychannel.send(embed=embed, delete_after=7)
        logger.info( "Invited {} to Partychannel".format( member.name ) ) 
                            

    #LEAVEN AUS DER PARTY
    @party.command()
    async def leave(self, ctx, *args):
        party = partys.get( ctx.channel, None )
        if not party:
            return # Der Channel hat keine Party
        if party.owner == ctx.author:
            embed = MyEmbed(name="Party",
               title=ctx.author.name,
               description=ctx.author.name + ", der Owner hat die "
               "Party verlassen. Deswegen wird die Party aufgelöst.",
               color=0xFFFF00)
            await ctx.channel.send(embed=embed, delete_after=7)
            await asyncio.sleep(7)
            #CHANNEL LÖSCHEN
            partys.pop( ctx.channel ) # Referenz löschen -> GC
            await ctx.channel.delete()
        else:
            party.members.remove(ctx.author)
            await party.partychannel.set_permissions(ctx.author, read_messages=False)
            embed = MyEmbed(name="Party",
              title=ctx.author.name + " hat die Party verlassen",
              description="Bis Bald!",
              color=0x00FF00)
            await party.partychannel.send(embed=embed, delete_after=7)

    #EINEN SPIELER KICKEN
    @party.command()
    async def kick(self, ctx, *args):
        party = partys.get( ctx.channel, None )
        if not party:
            return # Der Channel hat keine Party
        if party.owner != ctx.author:
            return # Nur owner darf kicken
        member = ctx.guild.get_member_named(args[0])
        if member in party.members:
            party.members.remove(member)
            await party.partychannel.set_permissions(member, read_messages=False)
            embed = MyEmbed(name="Party", title=ctx.author.name +
                " Hat den Spieler " + member.name +
                " aus der Party gekickt!",
                description="( Es sind nun noch " + str(len(party.members)+1)
                + " Spieler in der Party! )",
                color=0xFFFF00)
            await party.partychannel.send(embed=embed, delete_after=7)
        else:
            embed = MyEmbed(name="Party", title="Der Spieler " +
                args[1] + " ist nicht in deiner Party!",
                description="Hat die Party verlassen",
                color=0xFF0000)
            await party.partychannel.send(embed=embed, delete_after=7)

    #List Member:
    @party.command()
    async def list(self, ctx, *args):
        party = partys.get( ctx.channel, None )
        if not party:
            return # Der Channel hat keine Party
        embed = MyEmbed(name="Party",
           title="Aktuell in der Party ( " + 
           str(len(party.members) + 1) + " )",
           description=', '.join([member.name for member in party.members]),
           color=0x00FF00)
        embed.add_field(name="Owner:", value=party.owner.name, inline=False)
        await party.partychannel.send(embed=embed, delete_after=7)

    
    #Reactions:
    @commands.Cog.listener()
    async def on_reaction_add(self, payload, member):
        src_channel = payload.message.channel
        party = partys.get( src_channel, None )
        if not party:
            return # Der Channel hat keine Party
        if not payload.message in party.invite_messages:
            return # Reaction gehört zu keiner invite_message
        if member in party.members:
            return # Member ist schon in der Party
            # Warum hat er dann überhaupt eine Einladung bekommen können?
        if member.id == client.user.id:
            return # ???????????
               
        if payload.emoji == "✅": # angenommen:
            party.invite_messages.remove(payload.message)
            await payload.message.delete()
            party.members.append(member)
            await party.partychannel.set_permissions(member, read_messages=True)
            embed = MyEmbed(name = "Party",
               title=member.name + " hat die Party Anfrage angenommen!",
               description="",
               color=0x00FF00)
            await party.partychannel.send(embed=embed, delete_after=7)
            embed = MyEmbed(name = "Party",
               title="Du hast die Party Anfrage angenommen",
               description="( Es wurde für euch ein PartyChannel erstellt )",
               color=0x00FF00)
            await payload.message.channel.send(embed=embed, delete_after=7)
                
        elif payload.emoji == "🚫": # abgelehnt:
            party.invite_messages.remove(payload.message)
            await payload.message.delete()
            embed = MyEmbed(name = "Party",
               title=member.name + " hat die Party Anfrage abgelehnt!",
               description="",
               color=0xFF0000)
            await party.partychannel.send(embed=embed, delete_after=7)
            embed = MyEmbed(name="Party",
               title="Du hast die Party Anfrage Abgelehnt",
               description="( Frage nach einer erneuten Einladung"
               " wenn dies nicht gewollt war )",
               color=0xFFFF00)
            await payload.message.channel.send(embed=embed, delete_after=7)
        
        else:
            await payload.message.remove_reaction(payload.emoji, member)  # remove add

                

client.add_cog(PartyCog())
logger.info("Party Cog loaded")



