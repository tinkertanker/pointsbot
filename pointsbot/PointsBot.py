# noinspection PyPackageRequirements
import logging

import discord


class PointsBot(discord.Bot):
    def __init__(self, *args, **options):
        super().__init__(debug_guilds=[976345115826212884], *args, **options)
        self.load_extension('pointsbot.commands.points')

    def _setup_logging(self):
        self.logger = logging.getLogger('pointsbot')
        self.logger.setLevel(logging.INFO)
        self.logger.info("Logger is now ready.")

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
