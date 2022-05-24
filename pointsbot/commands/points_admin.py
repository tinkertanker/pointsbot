from typing import Union, Optional

# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from pointsbot import PointsBot
from pointsbot.commands import fmt_pts, fmt_spread_pts, fmt_update_pts
from pointsbot.database import update_usr_points, set_usr_points, reset_all, SqliteEngine


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
            await ctx.respond("That role doesn't exist!", ephemeral=True)
        if len(role.members) == 0:
            await ctx.respond("Can't give out points to 0 people...", ephimeral=True)
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
            await ctx.respond("That is pointless...", ephemeral=True)
        new_pts = update_usr_points(user, delta, self.bot.db)
        await ctx.respond(fmt_update_pts(user.mention, delta, new_pts))

    async def set_points(self, ctx: discord.ApplicationContext, user: discord.Member, pts: Union[int, float]):
        """
        Sets the point of a user
        :param ctx: The application context
        :param user: The user to set the points of
        :param pts: The number of points to set
        :return: None
        """
        set_usr_points(user, pts, self.bot.db)
        await ctx.respond(fmt_pts(user.mention, pts))

    points_admin = discord.SlashCommandGroup("padmin", "Points administration commands")

    @points_admin.command(name='spread_add', description='Evenly distributes points for users in a role')
    async def spread_add(self, ctx: discord.ApplicationContext,
                         role: discord.Option(discord.SlashCommandOptionType.role,
                                              "The role to spread the points amongst"),
                         points: discord.Option(discord.SlashCommandOptionType.number,
                                                "The number of points to spread")):
        if points < 0:
            await ctx.respond("Use `spread_deduct` instead. Processing anyway", ephemeral=True)

        await self.spread(ctx, role, points)

    @points_admin.command(name='spread_deduct',
                          description='Evenly distributes points for users in a role, deducting points')
    async def spread_deduct(self, ctx: discord.ApplicationContext,
                            role: discord.Option(discord.SlashCommandOptionType.role,
                                                 "The role to spread deduct the points amongst"),
                            points: discord.Option(discord.SlashCommandOptionType.number,
                                                   "The number of points to spread deduct")):
        if points < 0:
            await ctx.respond("Use `spread_add` instead. Processing anyway", ephemeral=True)
        await self.spread(ctx, role, -points)

    @points_admin.command(name="add", description="Adds points to a user")
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
            await ctx.respond("Note: This should be accomplished with the `deduct` command instead. "
                              "Processing anyway...", ephemeral=True)
        await self.update_points(ctx, user, points)

    @points_admin.command(name="deduct", description="Deducts points from a user")
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
        if points < 0:
            await ctx.respond("Note: This should be accomplished with the `add` command instead. Processing anyway...")
            await ctx.delete(delay=5)
        await self.update_points(ctx, user, -points)

    @points_admin.command(name="set", description="Sets the points of a user")
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

    @points_admin.command(name="reset", description="Resets ALL points in the server")
    async def reset_server(self, ctx: discord.ApplicationContext):
        class View(discord.ui.View):
            def __init__(self, db_engine: SqliteEngine, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.db = db_engine

            @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
            async def yes(self, btn: discord.ui.Button, interaction: discord.Interaction):
                self.disable_all_items()
                reset_all(interaction.guild, self.db)
                await interaction.response.edit_message(content="Ok. Resetting all points to 0", view=self)

            @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
            async def no(self, btn: discord.ui.Button, interaction: discord.Interaction):
                self.disable_all_items()
                await interaction.response.edit_message(content="Reset cancelled", view=self)

        await ctx.respond("Are you sure you want to reset ALL points in this server?", view=View(self.bot.db))

    @points_admin.command(name='debug', description="Temporary debug command")
    async def debug(self, ctx: discord.ApplicationContext,
                    member: discord.Option(discord.SlashCommandOptionType.user, "The user")):
        await ctx.respond(f"member is type member?: {isinstance(member, discord.Member)}")


def setup(bot: PointsBot):
    bot.add_cog(PointsAdmin(bot))
