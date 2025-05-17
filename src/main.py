from alicebot import Bot
from alicebot.adapter.dingtalk import DingTalkAdapter

bot = Bot()
bot.load_adapters(DingTalkAdapter)

if __name__ == "__main__":
    bot.run()