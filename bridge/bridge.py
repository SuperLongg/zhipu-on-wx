from ModelAPI.bot_factory import create_bot
from NotSupported.translate.factory import create_translator
from common import const
from common.log import logger
from common.singleton import singleton
from config import conf
from .context import Context
from .reply import Reply


# from voice.factory import create_voice


@singleton
class Bridge(object):
    def __init__(self):
        self.btype = {
            "chat": const.ZHIPU_AI,
            "voice_to_text": conf().get("voice_to_text", "baidu"),
            "text_to_voice": conf().get("text_to_voice", "baidu"),
            "translate": conf().get("translate", "baidu"),
        }
        # 这边取配置的模型
        bot_type = conf().get("bot_type")
        if bot_type:
            self.btype["chat"] = bot_type
        else:
            model_type = conf().get("model") or const.ZHIPU_AI
            if model_type in [const.ZHIPU_AI]:
                self.btype["chat"] = const.ZHIPU_AI
        self.bots = {}
        self.chat_bots = {}

    # 模型对应的接口
    def get_bot(self, typename):
        if self.bots.get(typename) is None:
            logger.info("create bot {} for {}".format(self.btype[typename], typename))
            if typename == "chat":
                self.bots[typename] = create_bot(self.btype[typename])
            # elif typename == "text_to_voice":
            #     self.bots[typename] = create_voice(self.btype[typename])
            # elif typename == "voice_to_text":
            #     self.bots[typename] = create_voice(self.btype[typename])
            elif typename == "translate":
                self.bots[typename] = create_translator(self.btype[typename])
        return self.bots[typename]

    def get_bot_type(self, typename):
        return self.btype[typename]

    def fetch_reply_content(self, query, context: Context) -> Reply:
        return self.get_bot("chat").reply(query, context)

    def fetch_voice_to_text(self, voiceFile) -> Reply:
        return self.get_bot("voice_to_text").voiceToText(voiceFile)

    def fetch_text_to_voice(self, text) -> Reply:
        return self.get_bot("text_to_voice").textToVoice(text)

    def fetch_translate(self, text) -> Reply:
        return self.get_bot("translate").translate(text)

    def find_chat_bot(self, bot_type: str):
        if self.chat_bots.get(bot_type) is None:
            self.chat_bots[bot_type] = create_bot(bot_type)
        return self.chat_bots.get(bot_type)

    def reset_bot(self):
        """
        重置bot路由
        """
        self.__init__()
