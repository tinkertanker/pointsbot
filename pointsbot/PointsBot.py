import logging

# noinspection PyPackageRequirements
import os.path
from pathlib import Path

import discord

from pointsbot.database import SqliteEngine


class PointsBot(discord.Bot):
    def __init__(self, database_engine: SqliteEngine, *args, **options):
        intents = discord.Intents.default()
        # noinspection PyDunderSlots,PyUnresolvedReferences
        intents.members = True

        super().__init__(debug_guilds=[976345115826212884], intents=intents, *args, **options)

        self._setup_database(database_engine)
        self._setup_logging()

        self.load_extension('pointsbot.commands.points')
        self.load_extension('pointsbot.commands.points_admin')

    def _setup_database(self, db_engine: SqliteEngine):
        self.db = db_engine
        here = os.path.dirname(os.path.abspath(__file__))
        self.db.exec_script(Path(here).parents[0] / 'db.sql')
        self.db.conn.commit()

    def _setup_logging(self):
        self.logger = logging.getLogger('pointsbot')
        self.logger.setLevel(logging.INFO)
        self.logger.info("Logger is now ready.")

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="commands"))
        print(f'Logged on as {self.user}!')
