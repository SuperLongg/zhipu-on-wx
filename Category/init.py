from Category.model import model2classify
from bridge.context import Context


def init(context: Context) -> Context:
    content = context.content
    response = model2classify(content)
    # style元素表示问题的类型
    context.kwargs['style'] = response
    return context