# noinspection PyPackageRequirements
import logging

import discord


class PointsBot(discord.Bot):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    def _setup_logging(self):
        self.logger = logging.getLogger('pointsbot')
        self.logger.setLevel(logging.INFO)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
