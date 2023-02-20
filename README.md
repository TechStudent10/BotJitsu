# BotJitsu
CardJitsu but it's a bot.

## Running

1. Create a bot and obtain its token
2. Rename `.env.example` to `.env` and fill in the fields
3. (Optional) Create a Virtual Environment
   1. Windows (requires the `virtualenv` package to be installed): `virtualenv venv`
   2. Linux/MacOS: `python3 -m venv venv`
4. Install the packages from `requirements.txt`: `pip install -r requirements.txt`
5. Run `python main.py`

Now you can invite the bot to your server and begin playing!

## Usage

First, you and another player must join a VC. One of you must run the slash command `/challenge <player>`. BotJitsu will join the VC you are in and send a DM to the challenger, asking if they accept the challenge. If they say yes, you'll both be sent a DM asking which card you want to use in the format below:

```
<element> <power>
```

Remember:
- Fire beats Snow
- Snow beats Water
- Water beats Fire

In the case that both elements match, the card with the highest power wins. If the cards the same, it's a draw.

More info on how CardJitsu works can be found [here](https://clubpenguin.fandom.com/wiki/Card-Jitsu).

Project is based on PolyMars' [Card-Jitsu-Voice](https://github.com/PolyMarsDev/Card-Jitsu-Voice) project for Alexa.
