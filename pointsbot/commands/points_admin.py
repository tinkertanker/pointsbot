# noinspection PyPackageRequirements
from typing import Union, Optional

import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from pointsbot import PointsBot
from pointsbot.commands import fmt_pts, fmt_spread_pts, fmt_update_pts
from pointsbot.database import update_usr_points, set_usr_points


class PointsAdmin(commands.Cog):
    def __init__(self, bot: PointsBot):
        self.bot = bot

    async def spread(self, ctx: discord.ApplicationContext, role: Optional[discord.Role], pts: Union[int, float]):
        """
        Spreads the points, and also throws some useful responses
        :param ctx: The application context
        :param role: The role to spread the points to
        :param pts: The number of points to spread
        :return: None
        """
        if role is None:
            await ctx.respond("That role doesn't exist!")
            return
        if len(role.members) == 0:
            await ctx.respond("Can't give out points to 0 people...")
            return
        pts_per_usr = pts / len(role.members)
        for member in role.members:
            update_usr_points(member, pts_per_usr, self.bot.db)
        await ctx.respond(fmt_spread_pts(role, pts))

    async def update_points(self, ctx: discord.ApplicationContext,
                            user: discord.Member,
                            delta: Union[int, float]):
        """
        Updates the points of a user
        :param ctx: The application context
        :param user: The user to update
        :param delta: The number of points to update by
        :return: None
        """
        if delta == 0:
            await ctx.respond("That is pointless...")
            return
        new_pts = update_usr_points(user, delta, self.bot.db)
        await ctx.respond(fmt_update_pts(user.mention, delta, new_pts))

    @commands.slash_command(name="padd", description="Adds points to a user")
    async def points_add(self, ctx: discord.ApplicationContext,
                         user: discord.Option(discord.SlashCommandOptionType.user,
                                              "The user to add points to"),
                         points: discord.Option(discord.SlashCommandOptionType.number,
                                                "The number of points to add",
                                                default=1)):
        """
        Adds points to a user
        :param ctx: The application context
        :param user: The user to add points to
        :param points: The number of points to add
        :return: None
        """
        if points < 0:
            await ctx.respond("Use the `deduct` command instead.")
            return
        await self.update_points(ctx, user, points)

    @commands.slash_command(name="pdeduct", description="Deducts points from a user")
    async def points_deduct(self, ctx: discord.ApplicationContext,
                            user: discord.Option(discord.SlashCommandOptionType.user,
                                                 "The user to deduct points from"),
                            points: discord.Option(discord.SlashCommandOptionType.number,
                                                   "The number of points to deduct",
                                                   default=1)):
        """
        Deducts points from a user
        :param ctx: The application context
        :param user: The user to deduct points from
        :param points: The number of points to deduct
        :return: None
        """
        if points > 0:
            await ctx.respond("Use the `add` command instead.")
            return
        await self.update_points(ctx, user, -points)

    @commands.slash_command(name="pset", description="Sets the points of a user")
    async def points_set(self, ctx: discord.ApplicationContext,
                         user: discord.Option(discord.SlashCommandOptionType.user,
                                              "The user to set points for"),
                         points: discord.Option(discord.SlashCommandOptionType.number,
                                                "The number of points to set",
                                                default=1)):
        """
        Sets the points of a user
        :param ctx: The application context
        :param user: The user to set points for
        :param points: The number of points to set
        :return: None
        """
        await self.set_points(ctx, user, points)

    points_admin = discord.SlashCommandGroup("padmin", "Points administration commands")

    @points_admin.command(name='spread_add', description='Evenly distributes points for users in a role')
    async def spread_add(self, ctx: discord.ApplicationContext,
                         role: discord.Option(discord.SlashCommandOptionType.role,
                                              "The role to spread the points amongst"),
                         points: discord.Option(discord.SlashCommandOptionType.number,
                                                "The number of points to spread")):
        if points < 0:
            await ctx.respond("Use `spread_deduct` instead.")
            return

        await self.spread(ctx, role, points)

    @points_admin.command(name='spread_deduct',
                          description='Evenly distributes points for users in a role, deducting points')
    async def spread_deduct(self, ctx: discord.ApplicationContext,
                            role: discord.Option(discord.SlashCommandOptionType.role,
                                                 "The role to spread deduct the points amongst"),
                            points: discord.Option(discord.SlashCommandOptionType.number,
                                                   "The number of points to spread deduct")):
        if points < 0:
            await ctx.respond("Use `spread_add` instead.")
            return
        await self.spread(ctx, role, -points)

    @points_admin.command(name='debug', description="Temporary debug command")
    async def debug(self, ctx: discord.ApplicationContext,
                    member: discord.Option(discord.SlashCommandOptionType.user, "The user")):
        await ctx.respond(f"member is type member?: {isinstance(member, discord.Member)}")


def setup(bot: PointsBot):
    bot.add_cog(PointsAdmin(bot))
