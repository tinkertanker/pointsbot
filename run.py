import os

import pointsbot
import dotenv


def main():
    dotenv.load_dotenv()
    if not os.getenv('DISCORD_TOKEN'):
        print("Can't run without a discord token!")
        exit(1)
    bot = pointsbot.PointsBot()
    bot.run(os.getenv('DISCORD_TOKEN'))


if __name__ == "__main__":
    main()
