from datetime import datetime

import requests
from bs4 import BeautifulSoup
from zhipuai import ZhipuAI

from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from plugins import EventContext, EventAction, Event, Plugin
from NotSupported.meteo.docs_prompt import OPEN_METEO_DOCS
from NotSupported.meteo.summary import reduce_prompt

# 目前先不启动插件，后续开放
# @plugins.register(
#     name="meteo",
#     desire_priority=-1,
#     hidden=False,
#     desc="Check the weather",
#     version="1.0",
#     author="zzl",
# )
class Meteo(Plugin):
    # description: str = (
    #     "When you want to obtain weather information, use this tool. Analyze which weather information the user wants, "
    #     "describe the problem rigorously in natural language, and then pass it on to this tool."
    #     "It's best to append the weather granularity to the end of the input, such as 'by hour' or 'by day', "
    #     "with priority given to 'by hour' when querying the weather on a specific day."
    # )

    def __init__(self):
        super().__init__()
        self.args = {
            "model": conf().get("model") or "glm-4",  # 对话模型的名称
            "top_p": 0,  # 另用温度取样的另一种方法，取值范围是：[0.0, 1.0]，默认值为0.7。
        }
        self.item = [{"role": "assistant", "content": OPEN_METEO_DOCS}]
        self.client = ZhipuAI(api_key=conf().get("zhipu_ai_api_key") or conf().get("ai_api_key"))
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        query = e_context["context"].content
        # Use the tool
        if not query:
            logger.error("[meteo]the input of tool is empty")
            return
        query += f"\nThe current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} in UTC+8."
        user_item = {"role": "user", "content": query}
        self.item.append(user_item)
        url = self.client.chat.completions.create(message=self.item, **self.args).choices[0].message.content.splitlines()[0]
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            reply = Reply()
            # 解析 HTML 内容
            soup = BeautifulSoup(response.content, "html.parser")
            # get text
            text = soup.get_text()
            reduce_text_history = [user_item, {"role": "assistant", "content": reduce_prompt(text)}]
            reduce_text = self.client.chat.completions.create(messages=reduce_text_history, **self.args).choices[0].message.content
            reply.type = ReplyType.TEXT
            reply.content = reduce_text
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return
        else:
            logger.error(f"[meteo]Requests get status_code is error: {response.status_code}")
            return
