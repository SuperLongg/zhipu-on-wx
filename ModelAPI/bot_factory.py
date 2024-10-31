"""
channel factory
"""
from common import const


def create_bot(bot_type):
    """
    create a bot_type instance
    :param bot_type: bot type code
    :return: bot instance
    """
    if bot_type == const.ZHIPU_AI:
        # 智普API
        from ModelAPI.zhipuai.zhipuai_bot import ZHIPUAIBot
        return ZHIPUAIBot()

    raise RuntimeError
