import logging
logger = logging.getLogger("party")

import asyncio

import discord
from discord.ext import commands
from myclient import client

class Party(commands.Cog):

    __partys = []

    def __init__(self, owner):
        super().__init__()
        self.qualified_name = str(owner.id)
        self.owner = owner
        self.members = []
        self.playing = False
        self.invite_messages = []
        Party.__partys.append(self)

        async def create_partychannel():
            self.partychannel = await client.guilds[0].create_text_channel(
                name=self.owner.name + "'s Party",
                category=client.get_channel(773935446732308502))
            role = client.guilds[0].get_role(741823660188500008)
            await self.partychannel.set_permissions(role, read_messages=False)
            await self.partychannel.set_permissions(self.owner, read_messages=True)

        asyncio.create_task(create_partychannel())

        client.add_cog(self)
        logger.info("Party Created")

    def is_in_party(member):
        for party in Party.__partys:
            for party_member in party.members:
                if party_member == member:
                    return True
            if party.owner == member:
                return True
        return False

    @commands.command()
    async def party(self, ctx: commands.Context, *args):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        #INVITEN EINES SPIELERS
        if len(args) == 2 and args[0].upper() == "INVITE":
            if ctx.channel == self.partychannel:
                if ctx.author == self.owner and len(args) == 1:
                    if len(self.members) < 10:
                        member = ctx.guild.get_member_named(args[1])
                        if not member == None:
                            if not member in self.members and not member == self.owner:
                                embed = discord.Embed(title="Der Spieler " + self.owner.name + " hat dich in eine Party eingeladen!",
                                                      description="( Klicke auf den Haken um die Einladung zu akzeptieren )",
                                                      color=0x00FF00)
                                embed.set_thumbnail(
                                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                                embed.set_author(name="Party",
                                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                                invite_message = await self.partychannel.send(embed=embed)
                                await invite_message.add_reaction("🚫")
                                await invite_message.add_reaction("✅")
                                self.invite_messages.append(invite_message)

                                embed = discord.Embed(title="Der Spieler " + member.name + " wurde in die Party eingeladen!", description="Bitte warte, bis er die Einladung akzeptiert", color=0x00FF00)
                                embed.set_thumbnail( url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                                embed.set_author(name="Party", icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                                await self.partychannel.send(embed=embed, delete_after=7)
                            else:
                                embed = discord.Embed(title="Der Spieler ist bereits in deiner Party!",
                                                      description="",
                                                      color=0xFF0000)
                                embed.set_thumbnail(
                                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                                embed.set_author(name="Party",
                                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                                await self.partychannel.send(embed=embed, delete_after=7)
                        else:
                            embed = discord.Embed(title="Dieser Spieler existiert nicht",
                                                  description="( Groß und klein Schreibung beachten! )",
                                                  color=0xFF0000)
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            embed.set_author(name="Party",
                                             icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                            await self.partychannel.send(embed=embed, delete_after=7)
                    else:
                        embed = discord.Embed(title="Du hast die maximale Anzahl an Spielern in deiner Party erreicht!",
                                              description="( Werfe einen Spieler aus der Party um neue einzuladen! )",
                                              color=0xFF0000)
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_author(name="Party",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.partychannel.send(embed=embed, delete_after=7)


        #LEAVEN AUS DER PARTY
        if len(args) == 1 and args[0].upper() == "LEAVE":
            if ctx.channel == self.partychannel:
                if self.owner == ctx.author:
                    embed = discord.Embed(title=ctx.author.name,
                                          description=ctx.author.name + ", der Owner hat die Party verlassen. Deswegen wird die Party aufgelößt.",
                                          color=0xFFFF00)
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_author(name="Party",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.partychannel.send(embed=embed, delete_after=7)
                    await asyncio.sleep(7)
                    #CHANNEL LÖSCHEN
                    client.remove_cog(str(self.owner.id))
                    await self.partychannel.delete()
                    Party.__partys.remove(self)
                    logger.info("Party Deleted")
                else:
                    self.members.remove(ctx.author)
                    await self.partychannel.set_permissions(ctx.author, read_messages=False)
                    embed = discord.Embed(title=ctx.author.name + " hat die Party verlassen",
                                          description="Bis Bald!",
                                          color=0x00FF00)
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    embed.set_author(name="Party",
                                     icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                    await self.partychannel.send(embed=embed, delete_after=7)

        #EINEN SPIELER KICKEN
        if len(args) == 2 and args[0].upper() == "KICK":
            if ctx.channel == self.partychannel:
                if self.owner == ctx.author:
                    member = ctx.guild.get_member_named(args[1])
                    if not member == None and member in self.members:
                        self.members.remove(member)
                        await self.partychannel.set_permissions(member, read_messages=False)
                        embed = discord.Embed(title=ctx.owner.name + " Hat den Spieler " + member.name + " aus der Party gekickt!",
                                              description="( Es sind nun noch " + str(len(self.members)+1) + " Spieler in der Party! )",
                                              color=0xFFFF00)
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_author(name="Party",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.partychannel.send(embed=embed, delete_after=7)
                    else:
                        embed = discord.Embed(title="Der Spieler " + args[1] + " ist nicht in deiner Party!",
                                              description="Hat die Party verlassen",
                                              color=0xFF0000)
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        embed.set_author(name="Party",
                                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                        await self.partychannel.send(embed=embed, delete_after=7)

        #EINEN SPIELER KICKEN
        if len(args) == 1 and args[0].upper() == "LIST":
            if ctx.channel == self.partychannel:
                embed = discord.Embed(
                    title="Aktuell in der Party ( " + str(len(self.members) + 1) + " )",
                    description=', '.join(self.members),
                    color=0x00FF00)
                embed.add_field(name="Owner:",
                                value=self.owner.name,
                                inline=False)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_author(name="Party",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.partychannel.send(embed=embed, delete_after=7)

    # Action bei drücken eines Reaction-Buttons: (Spielzug)
    @client.listen()
    async def on_reaction_add(self, payload: discord.Reaction, member):
        if payload.message in self.invite_messages and not member in self.members:
            if payload.emoji == "✅":
                self.invite_messages.remove(payload.message)
                payload.message.delete()
                self.members.append(member)
                await self.partychannel.set_permissions(member, read_messages=True)
                embed = discord.Embed(title=member.name + " hat die Party Anfrage angenommen!",
                                      description="",
                                      color=0xFF0000)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_author(name="Party",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.partychannel.send(embed=embed, delete_after=7)
                embed = discord.Embed(title="Du hast die Party Anfrage angenommen",
                                      description="( Es wurde für euch ein PartyChannel erstellt )",
                                      color=0xFF0000)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_author(name="Party",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await client.get_channel(payload.channel_id).send(embed=embed, delete_after=7)
            elif payload.emoji == "🚫":
                self.invite_messages.remove(payload.message)
                payload.message.delete()
                embed = discord.Embed(title=member.name + " hat die Party Anfrage abgelehnt!",
                                      description="",
                                      color=0xFF0000)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_author(name="Party",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await self.partychannel.send(embed=embed, delete_after=7)
                embed = discord.Embed(title="Du hast die Party Anfrage Abgelehnt",
                                      description="( Frage nach einer erneuten Einladung wenn dies nicht gewollt war )",
                                      color=0x00FF00)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                embed.set_author(name="Party",
                                 icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
                await client.get_channel(payload.channel_id).send(embed=embed, delete_after=7)

@client.command()
async def createparty(ctx: commands.Context, *args):
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    if Party.is_in_party(ctx.author):
        embed = discord.Embed(title=ctx.author.name + ", du bist bereits in einer Party!",
                              description="( Geh in den Party Channel und schreibe !party leave )",
                              color=0xFF0000)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="Party",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await ctx.channel.send(embed=embed, delete_after=7)
        return
    else:
        embed = discord.Embed(title="Party erfolgreich erstellt!",
                              description="",
                              color=0x00FF00)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        embed.set_author(name="Party",
                         icon_url="https://cdn.discordapp.com/app-icons/742032003125346344/e4f214ec6871417509f6dbdb1d8bee4a.png?size=256")
        await ctx.channel.send(embed=embed, delete_after=7)
        Party(ctx.author)

# Aufräumen beim Start:
@client.listen()
async def on_ready():
    for channel in client.get_all_channels():
        if "party" in channel.name:
            logger.info("delete " + channel.name)
            await channel.delete()




