# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from pointsbot import PointsBot
from pointsbot.commands import fmt_pts
from pointsbot.database import update_usr_points


class PointsAdmin(commands.Cog):
    def __init__(self, bot: PointsBot):
        self.bot = bot

    points_admin = discord.SlashCommandGroup("padmin", "Points administration commands")

    @points_admin.command(name='add', description="Adds points to a user")
    async def add_points(self, ctx: discord.ApplicationContext,
                         user: discord.Option(discord.SlashCommandOptionType.user,
                                              "The user to give points to"),
                         points: discord.Option(discord.SlashCommandOptionType.integer,
                                                "The number of points to add",
                                                default=1)):
        if points < 1:
            if points == 0:
                await ctx.respond("Pointless")
            else:
                await ctx.respond("You can't add negative points. Use `deduct` instead.")
            return
        usr: discord.Member = user
        new_pts = update_usr_points(user, points, self.bot.db)
        await ctx.respond(f"{fmt_pts(usr.mention, new_pts)} [+{points}]")

    @points_admin.command(name='set', description="Sets the points of a user")
    async def set_points(self, ctx: discord.ApplicationContext,
                         user: discord.Option(discord.SlashCommandOptionType.user,
                                              "The user to set points for"),
                         points: discord.Option(discord.SlashCommandOptionType.integer,
                                                "The number of points to set")):
        update_usr_points(user, points, self.bot.db)
        await ctx.respond(f"{user.mention} now has **{points}** points")

    @points_admin.command(name='deduct', description="Deducts points from a user")
    async def deduct_points(self, ctx: discord.ApplicationContext,
                            user: discord.Option(discord.SlashCommandOptionType.user,
                                                 "The user to deduct points from"),
                            points: discord.Option(discord.SlashCommandOptionType.integer,
                                                   "The number of points to deduct",
                                                   default=1)):
        if points < 1:
            if points == 0:
                await ctx.respond("Pointless")
            else:
                await ctx.respond("You can't deduct negative points. Use `add` instead.")
            return
        usr: discord.Member = user
        new_pts = update_usr_points(user, -points, self.bot.db)
        await ctx.respond(f"{fmt_pts(usr.mention, new_pts)} [-{points}]")

    @points_admin.command(name='spread', description='Evenly distributes points for users in a role')
    async def spread(self, ctx: discord.ApplicationContext,
                     role: discord.Option(discord.SlashCommandOptionType.role,
                                          "The role to spread the points amongst"),
                     points: discord.Option(discord.SlashCommandOptionType.integer,
                                            "The number of points to spread")):

        the_role: discord.Role = role
        if the_role is None:
            await ctx.respond("That role doesn't exist!")
            return

        if len(the_role.members) == 0:
            await ctx.respond("Can't give out points to 0 people...")
            return

        if abs(points) < len(the_role.members):
            await ctx.respond("You can't even give one point to everyone! What a grinch.")
            return

        pts_per_usr = points / len(the_role.members)
        for member in the_role.members:
            update_usr_points(member, pts_per_usr, self.bot.db)
        await ctx.respond(f"Evenly distributed {points} points to {len(the_role.members)} users in {the_role.mention} "
                          f"(each user has received: {pts_per_usr:.2f} points)")


def setup(bot: PointsBot):
    bot.add_cog(PointsAdmin(bot))
