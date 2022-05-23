import discord
from discord.ext import commands

from pointsbot import PointsBot


class Points(commands.Cog):
    def __init__(self, bot: PointsBot):
        self.bot = bot

    points = discord.SlashCommandGroup("points", "Points related commands.")

    @points.command(name='self', description="Retrieves your own points")
    async def points_self(self, ctx: discord.ApplicationContext):
        """
        Retrieves your own points.
        :param ctx: The applicationcontext
        :return: The number of points you have
        """
        await ctx.respond("You don't have any points")

    @points.command(name="get", description="Retrieves the points of another user")
    async def points_get(self, ctx: discord.ApplicationContext,
                         user: discord.Option(discord.SlashCommandOptionType.user, "The user to retrieve points for")):
        # note: the description MUST be specified under discord.Option, otherwise the docstring introspection fails
        # this is a bug with py-cord
        """
        Retrieves the points of another user.
        :param ctx: The applicationcontext
        :param user: The user to retrieve points for
        :return: The number of points the user has
        """
        usr: discord.Member = user
        await ctx.respond(f"{usr.mention} doesn't have any points")


def setup(bot: PointsBot):
    bot.add_cog(Points(bot))
