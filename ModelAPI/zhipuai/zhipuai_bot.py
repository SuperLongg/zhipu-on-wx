# encoding:utf-8
from datetime import datetime

from zhipuai import ZhipuAI

from Category.data import data_prompt
from Category.weather import weather_prompt
from ModelAPI.bot import Bot
from ModelAPI.session_manager import SessionManager
from ModelAPI.zhipuai.zhipu_ai_image import ZhipuAIImage
from ModelAPI.zhipuai.zhipu_ai_session import ZhipuAISession
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf, load_config


# ZhipuAI对话模型API
class ZHIPUAIBot(Bot, ZhipuAIImage):
    def __init__(self):
        super().__init__()
        self.sessions = SessionManager(ZhipuAISession)
        self.args = {
            "model": conf().get("model") or "glm-4",  # 对话模型的名称
            # "temperature": conf().get("temperature", 0.9),  # 采样温度，控制输出的随机性，必须为正数取值范围是：[0.0, 1.0]，默认值为0.95。和top_p二选一
            "top_p": conf().get("top_p", 0.7),  # 另用温度取样的另一种方法，取值范围是：[0.0, 1.0]，默认值为0.7。
        }
        self.tools = [{
            "type": "web_search",
            "web_search": {
                "enable": True
            }
        }]
        #很重要的一点，zhipu的网络检索是智谱内部自动判断是否需要进行，触发方式不确定，目前是在系统提示词中加入时间会跟容易触发
        self.client = ZhipuAI(api_key=conf().get("zhipu_ai_api_key") or conf().get("ai_api_key"))

    def reply(self, query, context=None):
        # acquire reply content
        if context.type == ContextType.TEXT:
            logger.info("[ZHIPU_AI] query={}".format(query))
            session_id = context["session_id"]
            reply = None
            clear_memory_commands = conf().get("clear_memory_commands", ["#清除记忆"])
            if query in clear_memory_commands:
                self.sessions.clear_session(session_id)
                reply = Reply(ReplyType.INFO, "记忆已清除")
            elif query == "#清除所有":
                self.sessions.clear_all_session()
                reply = Reply(ReplyType.INFO, "所有人记忆已清除")
            elif query == "#更新配置":
                load_config()
                reply = Reply(ReplyType.INFO, "配置已更新")
            if reply:
                return reply
            session = self.sessions.session_query(query, session_id)
            logger.debug("[ZHIPU_AI] session query={}".format(session.messages))

            new_args = self.args.copy()
            reply_content = self.reply_text(session, args=new_args, style=context.kwargs['style'])
            logger.debug(
                "[ZHIPU_AI] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(
                    session.messages,
                    session_id,
                    reply_content["content"],
                    reply_content["completion_tokens"],
                )
            )
            if reply_content["completion_tokens"] == 0 and len(reply_content["content"]) > 0:
                reply = Reply(ReplyType.ERROR, reply_content["content"])
            elif reply_content["completion_tokens"] > 0:
                self.sessions.session_reply(reply_content["content"], session_id, reply_content["total_tokens"])
                reply = Reply(ReplyType.TEXT, reply_content["content"])
            else:
                reply = Reply(ReplyType.ERROR, reply_content["content"])
                logger.debug("[ZHIPU_AI] reply {} used 0 tokens.".format(reply_content))
            return reply
        elif context.type == ContextType.IMAGE_CREATE:
            ok, retstring = self.create_img(query)
            if ok:
                reply = Reply(ReplyType.IMAGE_URL, retstring)
            else:
                reply = Reply(ReplyType.ERROR, retstring)
            return reply

        else:
            reply = Reply(ReplyType.ERROR, "Bot不支持处理{}类型的消息".format(context.type))
            return reply

    def reply_text(self, session: ZhipuAISession, args=None, style=None, retry_count=0) -> dict:
        """
        call zhipu AI to get the answer
        :param session: a conversation session
        :param args: AI parameters
        :param style: Type of content
        :param retry_count: retry count
        :return: {}
        """
        try:
            if args is None:
                args = self.args
            messages = session.messages
            if "1" in style:
                messages = [{"role": "system", "content": data_prompt},
                            messages[-1],
                            {"role": "user", "content": f"Time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, 周{datetime.now().weekday() + 1}"}]
                args["top_p"] = 0
                logger.debug("[ZHIPU_AI] style=1 args={}".format(args))
                response = self.client.chat.completions.create(messages=messages, **args, tools=self.tools)
            elif "2" in style:
                messages = [{"role": "system", "content": weather_prompt.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))},
                            messages[-1]]
                logger.debug("[ZHIPU_AI] style=2 args={}".format(args))
                response = self.client.chat.completions.create(messages=messages, **args, tools=self.tools)
            elif "0" in style:
                response = self.client.chat.completions.create(messages=messages, **args)
            else:
                return {"completion_tokens": 0, "content": "类别解析错误，不在定义内"}
            logger.debug("[ZHIPU_AI] response={}".format(response))
            return {
                "total_tokens": response.usage.total_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "content": response.choices[0].message.content,
            }

        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "content": "出错了:{}".format(e)}
            if need_retry:
                logger.warn("[ZHIPU_AI] 第{}次重试".format(retry_count + 1))
                return self.reply_text(session, args, retry_count + 1)
            else:
                return result
