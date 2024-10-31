def create_translator(voice_type):
    if voice_type == "zhipu":
        from NotSupported.translate.zhipu.zhipu_translate import ZhipuTranslator
        return ZhipuTranslator()
    raise RuntimeError
