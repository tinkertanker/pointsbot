import os

import pointsbot
import dotenv
import os

from pointsbot.database import SqliteEngine


def main():
    dotenv.load_dotenv()
    if not os.getenv('DISCORD_TOKEN'):
        print("Can't run without a discord token!")
        exit(1)
    if not os.getenv('DISCORD_SERVER'):
        print("Please supply a discord server you would like PointsBot to monitor")
        exit(1)
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "pointsbot.sqlite"))
    sqlite_engine = SqliteEngine(db_file)
    bot = pointsbot.PointsBot(sqlite_engine, run_in_servers=[int(os.getenv('DISCORD_SERVER'))])
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == "__main__":
    main()
