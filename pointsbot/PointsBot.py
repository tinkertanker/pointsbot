# noinspection PyPackageRequirements
import logging

import discord

from pointsbot.database import SqliteEngine


class PointsBot(discord.Bot):
    def __init__(self, database_engine: SqliteEngine, *args, **options):
        super().__init__(debug_guilds=[976345115826212884], *args, **options)

        self._setup_database(database_engine)
        self._setup_logging()

        self.load_extension('pointsbot.commands.points')
        self.load_extension('pointsbot.commands.points_admin')

    def _setup_database(self, db_engine: SqliteEngine):
        self.db = db_engine
        self.db.cur().execute(("""
        CREATE TABLE IF NOT EXISTS points (
            user_id INTEGER PRIMARY KEY,
            user_display_name VARCHAR(255) NOT NULL,
            points INTEGER NOT NULL DEFAULT 0
        );"""))
        self.db.cur().execute(("""
        CREATE TABLE IF NOT EXISTS administrators (
            user_id INTEGER PRIMARY KEY
        );
        """))
        self.db.conn().commit()

    def _setup_logging(self):
        self.logger = logging.getLogger('pointsbot')
        self.logger.setLevel(logging.INFO)
        self.logger.info("Logger is now ready.")

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
