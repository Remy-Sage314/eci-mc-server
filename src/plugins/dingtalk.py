from alicebot import Plugin

class HalloAlice(Plugin):
    async def handle(self) -> None:
        await self.event.reply("Hello Alice!")

    async def rule(self) -> bool:
        return (
                self.event.adapter.name == "dingtalk"
                # and self.event.type == "message"
                # and str(self.event.message).lower() == "hello"
        )