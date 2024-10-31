# encoding:utf-8

import json
import logging
import os
import pickle
import copy

from common.log import logger

# 将所有可用的配置项写在字典里, 请使用小写字母
# 此处的配置值无实际意义，程序不会读取此处的配置，仅用于提示格式，请将配置加入到config.json中
available_setting = {
    # openai api配置
    "ai_api_key": "",  # openai api key
    "proxy": "",  # openai使用的代理
    # chatgpt模型， 当use_azure_chatgpt为true时，其名称为Azure上model deployment名称
    "model": "gpt-3.5-turbo",  # 可选择: gpt-4o, pt-4o-mini, gpt-4-turbo, claude-3-sonnet, wenxin, moonshot, qwen-turbo, xunfei, glm-4, minimax, gemini等模型，全部可选模型详见common/const.py文件
    "bot_type": "",  # 可选配置，使用兼容openai格式的三方服务时候，需填"chatGPT"。bot具体名称详见common/const.py文件列出的bot_type，如不填根据model名称判断，
    # Bot触发配置
    "single_chat_prefix": ["bot", "@bot"],  # 私聊时文本需要包含该前缀才能触发机器人回复
    "single_chat_reply_prefix": "[bot] ",  # 私聊时自动回复的前缀，用于区分真人
    "single_chat_reply_suffix": "",  # 私聊时自动回复的后缀，\n 可以换行
    "group_chat_prefix": ["@bot"],  # 群聊时包含该前缀则会触发机器人回复
    "no_need_at": False,  # 群聊回复时是否不需要艾特
    "group_chat_reply_prefix": "",  # 群聊时自动回复的前缀
    "group_chat_reply_suffix": "",  # 群聊时自动回复的后缀，\n 可以换行
    "group_chat_keyword": [],  # 群聊时包含该关键词则会触发机器人回复
    "group_at_off": False,  # 是否关闭群聊时@bot的触发
    "group_name_white_list": ["霸凌测试群"],  # 开启自动回复的群名称列表
    "group_name_keyword_white_list": [],  # 开启自动回复的群名称关键词列表
    "group_chat_in_one_session": ["霸凌测试群"],  # 支持会话上下文共享的群名称
    "nick_name_black_list": [],  # 用户昵称黑名单
    "group_welcome_msg": "",  # 配置新人进群固定欢迎语，不配置则使用随机风格欢迎
    "trigger_by_self": False,  # 是否允许机器人触发
    "text_to_image": "dall-e-2",  # 图片生成模型，可选 dall-e-2, dall-e-3
    "concurrency_in_session": 1,  # 同一会话最多有多少条消息在处理中，大于1可能乱序
    "image_create_size": "256x256",  # 图片大小,可选有 256x256, 512x512, 1024x1024 (dall-e-3默认为1024x1024)
    "group_chat_exit_group": False,
    # chatgpt会话参数
    "expires_in_seconds": 3600,  # 无操作会话的过期时间:1小时
    # 人格描述
    "character_desc": "你是基于大语言模型的AI智能助手，旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。",
    "conversation_max_tokens": 1000,  # 支持上下文记忆的最多字符数
    # chatgpt限流配置
    "rate_limit_chatgpt": 20,  # chatgpt的调用频率限制
    "rate_limit_dalle": 50,  # openai dalle的调用频率限制
    # chatgpt api参数 参考https://platform.openai.com/docs/api-reference/chat/create
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "request_timeout": 180,  # chatgpt请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
    "timeout": 120,  # chatgpt重试超时时间，在这个时间内，将会自动重试
    # zhipu api参数
    "messages": "",  #调用语言模型时，当前对话消息列表作为模型的提示输入，以JSON数组形式提供，例如{"role": "user", "content": "Hello"}。可能的消息类型包括系统消息、用户消息、助手消息和工具消息。
    "request_id": "", #由用户端传递，需要唯一；用于区分每次请求的唯一标识符。如果用户端未提供，平台将默认生成。
    "do_sample": "", #当do_sample为true时，启用采样策略；当do_sample为false时，温度和top_p等采样策略参数将不生效。默认值为true。
    "stream": "", #该参数在使用同步调用时应设置为false或省略。表示模型在生成所有内容后一次性返回所有内容。默认值为false。如果设置为true，模型将通过标准Event Stream逐块返回生成的内容。当Event Stream结束时，将返回一个data: [DONE]消息。
    "temperature": "", #采样温度，控制输出的随机性，必须为正数取值范围是：[0.0, 1.0]，默认值为0.95。
    "top_p": "", #另用温度取样的另一种方法，取值范围是：[0.0, 1.0]，默认值为0.7。
    "max_tokens": "", #模型输出的最大token数，最大输出为4095，默认值为1024。
    "stop": "", #模型遇到stop指定的字符时会停止生成。目前仅支持单个stop词，格式为["stop_word1"]。
    "tools": "", #模型可以调用的工具。
    "type": "", #工具类型，目前支持 function、retrieval、web_search。
    "tool_choice": "", #用于控制模型选择调用哪个函数的方式，仅在工具类型为function时补充。默认auto，目前仅支持auto。
    "user_id": "", #终端用户的唯一ID，帮助平台对终端用户的非法活动、生成非法不当信息或其他滥用行为进行干预。ID长度要求：至少6个字符，最多128个字符。
    # 语音设置
    "speech_recognition": True,  # 是否开启语音识别
    "group_speech_recognition": False,  # 是否开启群组语音识别
    "voice_reply_voice": False,  # 是否使用语音回复语音，需要设置对应语音合成引擎的api key
    "always_reply_voice": False,  # 是否一直使用语音回复
    "voice_to_text": "openai",  # 语音识别引擎，支持openai,baidu,google,azure,xunfei,ali
    "text_to_voice": "openai",  # 语音合成引擎，支持openai,baidu,google,azure,xunfei,ali,pytts(offline),elevenlabs,edge(online)
    "text_to_voice_model": "tts-1",
    "tts_voice_id": "",
    #图设置
    "image_create_prefix": "",
    # 服务时间限制，目前支持itchat
    "chat_time_module": False,  # 是否开启服务时间限制
    "chat_start_time": "00:00",  # 服务开始时间
    "chat_stop_time": "24:00",  # 服务结束时间
    # 翻译api
    "translate": "zhipu",  # 直接让大模型翻译返回content，也可以使用其他翻译api，例如百度(新注册可试用)
    # itchat的配置
    "hot_reload": False,  # 是否开启热重载
    # chatgpt指令自定义触发词
    "clear_memory_commands": ["#清除记忆"],  # 重置会话指令，必须以#开头
    # channel配置
    "channel_type": "",  # 通道类型，只支持个人wx，已删除其他渠道
    "debug": False,  # 是否开启debug模式，开启后会打印更多日志
    "appdata_dir": "",  # 数据目录
    # 插件配置
    "plugin_trigger_prefix": "$",  # 规范插件提供聊天相关指令的前缀，建议不要和管理员指令前缀"#"冲突
    # 是否使用全局插件配置
    "use_global_plugin_config": False,
    "max_media_send_count": 3,  # 单次最大发送媒体资源的个数
    "media_send_interval": 1,  # 发送图片的事件间隔，单位秒
    # 智谱AI 平台配置
    "zhipu_ai_api_key": "",
    "zhipu_ai_api_base": "https://open.bigmodel.cn/api/paas/v4",
    "zhipu_web_search": False
}


class Config(dict):
    def __init__(self, d=None):
        super().__init__()
        if d is None:
            d = {}
        for k, v in d.items():
            self[k] = v
        # user_datas: 用户数据，key为用户名，value为用户数据，也是dict
        self.user_datas = {}

    def __getitem__(self, key):
        if key not in available_setting:
            raise Exception("key {} not in available_setting".format(key))
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key not in available_setting:
            raise Exception("key {} not in available_setting".format(key))
        return super().__setitem__(key, value)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError as e:
            return default
        except Exception as e:
            raise e

    # Make sure to return a dictionary to ensure atomic
    def get_user_data(self, user) -> dict:
        if self.user_datas.get(user) is None:
            self.user_datas[user] = {}
        return self.user_datas[user]

    def load_user_datas(self):
        try:
            with open(os.path.join(get_appdata_dir(), "user_datas.pkl"), "rb") as f:
                self.user_datas = pickle.load(f)
                logger.info("[Config] User datas loaded.")
        except FileNotFoundError as e:
            logger.info("[Config] User datas file not found, ignore.")
        except Exception as e:
            logger.info("[Config] User datas error: {}".format(e))
            self.user_datas = {}

    def save_user_datas(self):
        try:
            with open(os.path.join(get_appdata_dir(), "user_datas.pkl"), "wb") as f:
                pickle.dump(self.user_datas, f)
                logger.info("[Config] User datas saved.")
        except Exception as e:
            logger.info("[Config] User datas error: {}".format(e))


config = Config()


def drag_sensitive(config):
    try:
        if isinstance(config, str):
            conf_dict: dict = json.loads(config)
            conf_dict_copy = copy.deepcopy(conf_dict)
            for key in conf_dict_copy:
                if "key" in key or "secret" in key:
                    if isinstance(conf_dict_copy[key], str):
                        conf_dict_copy[key] = conf_dict_copy[key][0:3] + "*" * 5 + conf_dict_copy[key][-3:]
            return json.dumps(conf_dict_copy, indent=4)

        elif isinstance(config, dict):
            config_copy = copy.deepcopy(config)
            for key in config:
                if "key" in key or "secret" in key:
                    if isinstance(config_copy[key], str):
                        config_copy[key] = config_copy[key][0:3] + "*" * 5 + config_copy[key][-3:]
            return config_copy
    except Exception as e:
        logger.exception(e)
        return config
    return config


def load_config():
    global config
    config_path = "./config.json"
    if not os.path.exists(config_path):
        logger.info("配置文件不存在，将使用config-template.json模板")
        config_path = "./config-template.json"

    config_str = read_file(config_path)
    logger.debug("[INIT] config str: {}".format(drag_sensitive(config_str)))

    # 将json字符串反序列化为dict类型
    config = Config(json.loads(config_str))

    # override config with environment variables.
    # Some online deployment platforms (e.g. Railway) deploy project from github directly. So you shouldn't put your secrets like api key in a config file, instead use environment variables to override the default config.
    for name, value in os.environ.items():    #获取当前环境变量的键值对
        name = name.lower()
        if name in available_setting:
            logger.info("[INIT] override config by environ args: {}={}".format(name, value))
            # try:
            #     config[name] = eval(value)   # 这个value具体是什么？ 使用 ast.literal_eval，它只会解析字面量和容器类型，不会执行任意代码。
            # except:
            #     if value == "false":
            #         config[name] = False
            #     elif value == "true":
            #         config[name] = True
            #     else:
            #         config[name] = value

    if config.get("debug", False):
        logger.setLevel(logging.DEBUG)
        logger.debug("[INIT] set log level to DEBUG")

    logger.info("[INIT] load config: {}".format(drag_sensitive(config)))

    config.load_user_datas()


def get_root():
    return os.path.dirname(os.path.abspath(__file__))


def read_file(path):
    with open(path, mode="r", encoding="utf-8") as f:
        return f.read()


def conf():
    return config


def get_appdata_dir():
    data_path = os.path.join(get_root(), conf().get("appdata_dir", ""))
    if not os.path.exists(data_path):
        logger.info("[INIT] data path not exists, create it: {}".format(data_path))
        os.makedirs(data_path)
    return data_path


# global plugin config
plugin_config = {}


def write_plugin_config(pconf: dict):
    """
    写入插件全局配置
    :param pconf: 全量插件配置
    """
    global plugin_config
    for k in pconf:
        plugin_config[k.lower()] = pconf[k]


def pconf(plugin_name: str) -> dict:
    """
    根据插件名称获取配置
    :param plugin_name: 插件名称
    :return: 该插件的配置项
    """
    return plugin_config.get(plugin_name.lower())


# 全局配置，用于存放全局生效的状态
global_config = {"admin_users": []}
