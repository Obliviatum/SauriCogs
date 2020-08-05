from datetime import datetime as dt
import discord

from redbot.core import checks, commands, Config

from redbot.core.bot import Red

__author__ = "saurichable"


class UserLog(commands.Cog):
    """Log when users join/leave into your specified channel."""

    __author__ = "saurichable"
    __version__ = "1.0.3"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=56546565165465456, force_registration=True
        )

        self.config.register_guild(channel=None, join=True, leave=True, invites={})

    @commands.group(autohelp=True)
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def userlog(self, ctx):
        """Manage user log settings."""
        pass

    @userlog.command(name="channel")
    async def user_channel_log(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for logs.

        If the channel is not provided, logging will be disabled."""
        if channel:
            await self.config.guild(ctx.guild).channel.set(channel.id)
            await self.set_invites(guild)
        else:
            await self.config.guild(ctx.guild).channel.set(None)
        await ctx.tick()

    @userlog.command(name="join")
    async def user_join_log(self, ctx: commands.Context, on_off: bool = None):
        """Toggle logging when users join the current server. 

        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).join())
        )
        await self.config.guild(ctx.guild).join.set(target_state)
        if target_state:
            await ctx.send("Logging users joining is now enabled.")
        else:
            await ctx.send("Logging users joining is now disabled.")

    @userlog.command(name="leave")
    async def user_leave_log(self, ctx: commands.Context, on_off: bool = None):
        """Toggle logging when users leave the current server.

        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).leave())
        )
        await self.config.guild(ctx.guild).leave.set(target_state)
        if target_state:
            await ctx.send("Logging users leaving is now enabled.")
        else:
            await ctx.send("Logging users leaving is now disabled.")
            
    async def set_invites(self, guild):
        try:
	    invs = await self.bot.get_guild(guild.id).invites()
	    invs = dict([[inv.url, inv.uses] for inv in invs])
	    await self.config.guild(guild).invites.set(invs)
	except discord.Forbidden:
	    pass
	except discord.HTTPException:
	    pass

    async def joined_with(self, member):
        try:
	    json_list = await self.config.guild(member.guild).invites()
	    inv_list = await self.bot.get_guild(member.guild.id).invites()
	    for invite in inv_list:
		if invite.uses > json_list.get(invite.url, 0):
		    return invite
	except discord.Forbidden:
	    pass
	except discord.HTTPException:
	    pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        join = await self.config.guild(member.guild).join()
        if not join:
            return
        channel = member.guild.get_channel(await self.config.guild(member.guild).channel())
        if not channel:
            return
        time = dt.utcnow()
        users = len(member.guild.members)
        since_created = (time - member.created_at).days
        user_created = member.created_at.strftime("%Y-%m-%d, %H:%M")

        created_on = f"{user_created} ({since_created} days ago)"
        
        invite = await self.joined_with(member)
	joined_with = f"{invite.url} referred by {invite.inviter}\nused {invite.uses}/{invite.max_uses}"

        embed = discord.Embed(
            description=f"{member.mention} ({member.name}#{member.discriminator})",
            colour=discord.Colour.green(),
            timestamp=member.joined_at,
        )
        embed.add_field(name="Total Users:", value=str(users))
        embed.add_field(name="Account created on:", value=created_on)
        embed.add_field(name="Joined with:", value=joined_with)
        embed.set_footer(text=f"User ID: {member.id}")
        embed.set_author(
            name=f"{member.name} has joined {member.guild.name}",
            url=member.avatar_url,
            icon_url=member.avatar_url,
        )
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        leave = await self.config.guild(member.guild).leave()
        if not leave:
            return
        channel = member.guild.get_channel(await self.config.guild(member.guild).channel())
        if not channel:
            return
        time = dt.utcnow()
        users = len(member.guild.members)
        since_joined = (time - member.joined_at).days
	user_joined = member.joined_at.strftime("%Y-%m-%d, %H:%M")

	joined_on = f"{user_joined} ({since_joined} days ago)"

        embed = discord.Embed(
            description=f"{member.mention} ({member.name}#{member.discriminator})",
            colour=discord.Colour.red(),
            timestamp=time,
        )
        embed.add_field(name="Total Users:", value=str(users))
        embed.add_field(name="Account joined on:", value=joined_on)
        embed.set_footer(text=f"User ID: {member.id}")
        embed.set_author(
            name=f"{member.name} has left {member.guild.name}",
            url=member.avatar_url,
            icon_url=member.avatar_url,
        )
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_invite_create(self, invite):
		guild = invite.guild
		channel = guild.get_channel(await self.config.guild(guild).channel())
		if not channel:
			return
		await self.set_invites(invite.guild)

	@commands.Cog.listener()
	async def on_invite_delete(self, invite):
		guild = invite.guild
		channel = guild.get_channel(await self.config.guild(guild).channel())
		if not channel:
			return
		await self.set_invites(invite.guild)
