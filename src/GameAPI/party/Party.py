import logging
logger = logging.getLogger("party")

import asyncio

import discord
from discord.ext import commands
from myclient import client, MyEmbed

class Party(commands.Cog):

    __partys = []

    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.members = []
        self.playing = False
        self.invite_messages = []
        Party.__partys.append(self)
        client.add_cog(self)

        async def create_partychannel():
            self.partychannel = await client.guilds[0].create_text_channel(
                name=self.owner.name + "'s Party",
                category=client.get_channel(773935446732308502))
            role = client.guilds[0].get_role(741823660188500008)
            await self.partychannel.set_permissions(role, read_messages=False)
            await self.partychannel.set_permissions(self.owner, read_messages=True)

        asyncio.create_task(create_partychannel())

        logger.info("Party Created")

    def is_in_party(member):
        for party in Party.__partys:
            for party_member in party.members:
                if party_member == member:
                    return True
            if party.owner == member:
                return True
        return False

    def get_party_from_channel(channel):
        for party in Party.__partys:
            if party.partychannel == channel:
                return party
        return False

    def remove_party(party):
        client.remove_cog(party)
        Party.__partys.remove(party)

    @commands.Cog.listener()
    async def on_reaction_add(self, payload: discord.Reaction, member):
        if payload.message in self.invite_messages and not member in self.members and member.id is not client.user.id:
            if payload.emoji == "✅":
                self.invite_messages.remove(payload.message)
                await payload.message.delete()
                self.members.append(member)
                await self.partychannel.set_permissions(member, read_messages=True)
                embed = MyEmbed(name = "Party",
                      title=member.name + " hat die Party Anfrage angenommen!",
                      description="",
                      color=0x00FF00)
                await self.partychannel.send(embed=embed, delete_after=7)
                embed = MyEmbed(name = "Party",
                      title="Du hast die Party Anfrage angenommen",
                      description="( Es wurde für euch ein PartyChannel erstellt )",
                      color=0x00FF00)
                await payload.message.channel.send(embed=embed, delete_after=7)
            elif payload.emoji == "🚫":
                self.invite_messages.remove(payload.message)
                await payload.message.delete()
                embed = MyEmbed(name = "Party",
                      title=member.name + " hat die Party Anfrage abgelehnt!",
                      description="",
                      color=0xFF0000)
                await self.partychannel.send(embed=embed, delete_after=7)
                embed = MyEmbed(name="Party",
                      title="Du hast die Party Anfrage Abgelehnt",
                      description="( Frage nach einer erneuten Einladung"
                                  " wenn dies nicht gewollt war )",
                      color=0xFFFF00)
                await payload.message.channel.send(embed=embed, delete_after=7)
            else:
                await payload.message.remove_reaction(payload.emoji, member)  # remove add

@client.command()
async def party(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    party = Party.get_party_from_channel(ctx.channel)
    if party == False:
        return
    #INVITEN EINES SPIELERS
    if len(args) == 2 and args[0].upper() == "INVITE":
        if ctx.channel == party.partychannel:
            if ctx.author == party.owner:
                if len(party.members) < 10:
                    member = ctx.guild.get_member_named(args[1])
                    if not member == None:
                        if not member in party.members and not member == party.owner:
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
                        else:
                            embed = MyEmbed(name="Party", 
                                  title="Der Spieler ist bereits in deiner Party!",
                                  description="",
                                  color=0xFF0000)
                            await party.partychannel.send(embed=embed, delete_after=7)
                    else:
                        embed = MyEmbed(name="Party",
                                  title="Dieser Spieler existiert nicht",
                                  description="( Groß und klein Schreibung beachten! )",
                                  color=0xFF0000)
                        await party.partychannel.send(embed=embed, delete_after=7)
                else:
                    embed = MyEmbed(name="Party",
                              title="Du hast die maximale Anzahl an Spielern "
                              "in deiner Party erreicht!",
                              description="( Werfe einen Spieler aus der "
                              "Party um neue einzuladen! )",
                              color=0xFF0000)
                    await party.partychannel.send(embed=embed, delete_after=7)


    #LEAVEN AUS DER PARTY
    if len(args) == 1 and args[0].upper() == "LEAVE":
        print("leave")
        if ctx.channel == party.partychannel:
            print("rightchannel")
            if party.owner == ctx.author:
                print("owner")
                embed = MyEmbed(name="Party",
                     title=ctx.author.name,
                     description=ctx.author.name + ", der Owner hat die "
                     "Party verlassen. Deswegen wird die Party aufgelöst.",
                     color=0xFFFF00)
                await party.partychannel.send(embed=embed, delete_after=7)
                await asyncio.sleep(7)
                #CHANNEL LÖSCHEN
                await party.partychannel.delete()
                Party.remove_party(party)
                logger.info("Party Deleted")
            else:
                party.members.remove(ctx.author)
                await party.partychannel.set_permissions(ctx.author, read_messages=False)
                embed = MyEmbed(name="Party",
                     title=ctx.author.name + " hat die Party verlassen",
                     description="Bis Bald!",
                     color=0x00FF00)
                await party.partychannel.send(embed=embed, delete_after=7)

    #EINEN SPIELER KICKEN
    if len(args) == 2 and args[0].upper() == "KICK":
        if ctx.channel == party.partychannel:
            if party.owner == ctx.author:
                member = ctx.guild.get_member_named(args[1])
                if not member == None and member in party.members:
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

    #EINEN SPIELER KICKEN
    if len(args) == 1 and args[0].upper() == "LIST":
        if ctx.channel == party.partychannel:
            embed = MyEmbed(name="Party",
                title="Aktuell in der Party ( " + 
                    str(len(party.members) + 1) + " )",
                description=', '.join([member.name for member in party.members]),
                color=0x00FF00)
            embed.add_field(name="Owner:",
                            value=party.owner.name,
                            inline=False)
            await party.partychannel.send(embed=embed, delete_after=7)

@client.command()
async def createparty(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    if Party.is_in_party(ctx.author):
        embed = MyEmbed(name="Party", title=ctx.author.name + 
             ", du bist bereits in einer Party!",
             description="( Geh in den Party Channel und schreibe !party leave )",
             color=0xFF0000)
        await ctx.channel.send(embed=embed, delete_after=7)
        return
    else:
        embed = MyEmbed(title="Party erfolgreich erstellt!",
             description="",
             color=0x00FF00)
        await ctx.channel.send(embed=embed, delete_after=7)
        Party(ctx.author)

# Aufräumen beim Start:
@client.listen()
async def on_ready():
    for channel in client.get_all_channels():
        if "party" in channel.name:
            logger.info("delete " + channel.name)
            await channel.delete()




