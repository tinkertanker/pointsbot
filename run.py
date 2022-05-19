import os

import pointsbot
import dotenv


def main():
    dotenv.load_dotenv()
    bot = pointsbot.PointsBot()
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == "__main__":
    main()
