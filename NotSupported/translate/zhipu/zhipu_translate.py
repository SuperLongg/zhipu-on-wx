# -*- coding: utf-8 -*-


from zhipuai import ZhipuAI
from config import conf


class ZhipuTranslator:
    def __init__(self) -> None:
        self.client = ZhipuAI(api_key=conf().get("zhipu_ai_api_key") or conf().get("ai_api_key"))
        self.args = {
            "model": conf().get("model") or "glm-4",  # 对话模型的名称
            "top_p": conf().get("top_p", 0.7),  # 另用温度取样的另一种方法，取值范围是：[0.0, 1.0]，默认值为0.7。
        }
        self.messages = []
        if not self.client:
            raise Exception("{} not set".format(self.args))

    def translate(self, query) -> str:
        self.messages.append({"role": "assistant",
                              "content": f'''你是一位精通各国语言的专业翻译，尤其擅长翻译日常生活中的语言。请根据消息中要求的语言进行翻译
                                            # 策略：
                                            分三步进行翻译工作，并打印每步的结果：
                                            1. 根据内容直译，保持原有格式，不要遗漏任何信息
                                            2. 根据第一步直译的结果，指出其中存在的具体问题，要准确描述，不宜笼统的表示，也不需要增加原文不存在的内容或格式，包括不仅限于：
                                            - 不符合当地语言表达习惯，明确指出不符合的地方
                                            - 语句不通顺，指出位置，不需要给出修改意见，意译时修复
                                            - 晦涩难懂，不易理解，可以尝试给出解释
                                            3. 根据第一步直译的结果和第二步指出的问题，重新进行意译，保证内容的原意的基础上，使其更易于理解，更符合当地语言的表达习惯，同时保持原有的格式不变
                                            # 规则：
                                            - 翻译时要准确传达原文的事实和背景。
                                            - 即使上意译也要保留原始段落格式，以及保留术语，例如 ARP，OSPF 等。保留公司缩写，例如 Cisco, Amazon, Juniper, OpenAI 等。
                                            - 人名不翻译
                                            - 全角括号换成半角括号，并在左括号前面加半角空格，右括号后面加半角空格。
                                            - 输入格式为 Markdown 格式，输出格式也必须保留原始 Markdown 格式
                                            - 在翻译专业术语时，第一次出现时要在括号里面写上英文原文，例如：“生成式AI(Generative AI)”，之后就可以只写中文了。
                                            # 返回格式：
                                            返回格式如下，"{{xxx}}"表示占位符：
                                            ### 直译
                                            "{{直译结果}}"
                                            ***
                                            ### 问题
                                            {{直译的具体问题列表}}
                                            ***
                                            ### 意译
                                            {{意译结果}}
                                            现在请按照上面的要求从第一行开始翻译以下内容为简体中文：
                                            ```
                                            {query}
                                            ```'''
                              })
        response = self.client.chat.completions.create(
            messages=self.messages,
            **self.args
        )
        result = response.choices[0].message.content
        return result
