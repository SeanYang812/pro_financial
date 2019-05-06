from IPython.display import display


class WidgetBase(object):
    """界面组件基类，限定最终widget为self.widget"""

    def __call__(self):
        return self.widget

    def display(self):
        """显示使用统一display"""
        display(self.widget)


def to_unicode(text, encoding=None, errors='strict'):
    """
    to_native_str对py2生效，对str直接返回，其它的encode，默认utf-8
    """
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError('to_unicode must receive a bytes, str or unicode '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'

    try:
        decode_text = text.decode(encoding, errors)
    except:
        # 切换试一下，不行就需要上层处理
        decode_text = text.decode('gbk' if encoding == 'utf-8' else 'utf-8', errors)
    return decode_text
