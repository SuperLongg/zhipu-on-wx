# 简介
> 基于chatgpt-on-wechat项目，完善部分函数参数错误，删除插件部分，删除了文生图相关功能，只支持个人微信(使用itchat-UOS项目), 后续改用工作流方式

## 1.运行环境
测试环境python版本为3.12.7

## 2.下载代码
```bash
git clone https://github.com/SuperLongg/zhipu-on-wx.git
```

## 3.安装依赖
```bash
pip3 install -r requirements.txt
```

## 4.注意事项
- 1)glm-4-flash为智谱免费api，需要前往官网(https://bigmodel.cn/usercenter/apikeys)注册账号获取apikey
- 2)使用itchat-UOS库作为微信个人号的接口
- 3)登录账号需要实名认证(即绑定银行卡)

## 5.config配置
模板为根目录的config-template.json
```bash
cp config-template.json config.json
```
配置一份自定义的config.json
```bash
{
  "channel_type": "wx",                                   # 聊天渠道类型，不用更改(只支持个人wx，已删除其他渠道)
  "model": "glm-4-flash",                                 # 大模型选择，可以为智谱的其他模型比如glm-4、glm-4-plus
  "ai_api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",          # 模型的apikey
  "text_to_image": "dall-e-2",                            # 文生图模型，已删除，暂不支持，后续找到可用API会加上
  "voice_to_text": "baidu",                               # 语音识别引擎，暂未调试，代码中修改为百度API，注册账号后可以免费使用30天
  "text_to_voice": "baidu",                               # 语音合成引擎，暂未调试。
  "proxy": "",                                            # 代理。暂时用不到
  "hot_reload": false,                                    # 热重载开关
  "single_chat_prefix": [
    "@bot"
  ],                                                      # 私聊时文本需要包含该前缀才能触发机器人回复，不需要前缀触发删除修改为""即可
  "single_chat_reply_prefix": "[bot]:",                   # 私聊时自动回复的前缀，用于区分真人
  "group_chat_prefix": [
    "@bot"
  ],                                                      # 群聊时包含该前缀则会触发机器人回复
  "group_name_white_list": [
    "xxxQ1",
    "xxxQ2"
  ],                                                      # 开启自动回复的群名称列表
  "image_create_prefix": [
    "画"
  ],                                                      # 图片生成的触发词
  "debug": false,                                         # debug模式，开启后会打印更多日志
  "speech_recognition": true,                             # 是否开启语音识别
  "group_speech_recognition": false,                      # 是否开启群组语音识别
  "voice_reply_voice": false,                             # 是否使用语音回复语音，需要设置对应语音合成引擎的api key
  "conversation_max_tokens": 2500,                        # 支持上下文记忆的最多字符数
  "expires_in_seconds": 3600,                             # 无操作会话的过期时间:1小时
  "character_desc": "你是基于大语言模型的AI智能助手，旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。",  # 系统提示词
  "temperature": 1.0                                      # 采样温度，控制输出的随机性
}
```

## 6.运行
**本地运行**：
```bash
python3 app.py
```