from zhipuai import ZhipuAI

from common.log import logger
from config import conf

prompt = """
   {input}
   #任务
   按照下列情况分析输入是属于哪种类型
   ##
   如果是询问时间或日期相关，就返回"1"
   ##
   如果是询问天气相关，就返回"2"
   ##
   如何都不相关，就返回"0"
   #注意
   只能返回要求的值，只能返回规定的值有且只有一个

   {output}
"""

def model2classify(content: str) -> str:
    # 后续有其他免费API/或可用API 这里再做客制化
    client = ZhipuAI(api_key=conf().get("zhipu_ai_api_key") or conf().get("ai_api_key"))
    args = {
        "model": conf().get("model") or "glm-4",  # 对话模型的名称
        # "temperature": conf().get("temperature", 0.9),  # 采样温度，控制输出的随机性，必须为正数取值范围是：[0.0, 1.0]，默认值为0.95。和top_p二选一
        "top_p": 0,  # 让回复的答案唯一
    }
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content":content}]
    response = client.chat.completions.create(messages=messages, **args)
    logger.info("[model] response.choices[0].message.content: {}".format(response.choices[0].message.content))
    return response.choices[0].message.content
