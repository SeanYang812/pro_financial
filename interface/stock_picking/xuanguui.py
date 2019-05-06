from ipywidgets import widgets
from lib.commen import WidgetBase, to_unicode
from conf import settings

class StockPool(WidgetBase):
    """股票池选股ui界面"""

    # noinspection PyProtectedMember
    def __init__(self):
        """构建股票池选股ui界面"""
        label_layout = widgets.Layout(width='300px', align_items='stretch', justify_content='space-between')
        # self.cs_tip = widgets.Label(value='如果股池为空，回测将使用大盘市场中所有股票', layout=label_layout)
        # 股票池多选框
        self.choice_symbols = widgets.SelectMultiple(
            description='股池:',
            disabled=False,
            layout=widgets.Layout(width='300px', align_items='stretch', justify_content='space-between')
        )
        self.choice_symbols.observe(self.choice_symbols_select, names='value')

        # 构建所有沙盒中的数据序列
        market_title = ['A股','港股']
        cn_seed_symbol = [to_unicode('{}:{}'.format(name[0], symbol))
                          for symbol, name in settings.get_stock_list(settings.K_SAND_BOX_CN).items()]
        # hk_seed_symbol = [to_unicode('{}:{}'.format(name[0], symbol))
        #                   for symbol, name in settings.get_stock_list(settings.K_SAND_BOX_HK).items()]
        # print("cn_seed_symbol",cn_seed_symbol)
        # print("hk_seed_symbol",hk_seed_symbol)
        self.market_dict = {'A股': cn_seed_symbol,}
        # 一个市场一个tab，tab中的symbol为沙盒中的symbol
        self.market_widget_tab = widgets.Tab()
        self.market_symbol_widget = []

        for title in market_title:
            market_symbol = widgets.SelectMultiple(
                options=self.market_dict[title],
                description=title,
                disabled=False
            )

            market_symbol.observe(self.on_already_select, names='value')
            self.market_symbol_widget.append(market_symbol)
            self.market_widget_tab.children = self.market_symbol_widget

            for ind, name in enumerate(market_title):
                self.market_widget_tab.set_title(ind, name)

            self.sc_box = WidgetSearchBox(self.on_already_select)()

        self.widget = widgets.VBox([self.choice_symbols, self.market_widget_tab,self.sc_box])

    def on_already_select(self, select):
        """搜索框或者内置沙盒symbol中点击放入股票池"""
        st_symbol = [symbol.split(':')[1] if symbol.find(':') > 0
                     else symbol for symbol in list(select['new'])]
        # 更新股票池中原有的symbol序列
        self.choice_symbols.options = list(set(st_symbol + list(self.choice_symbols.options)))

    def choice_symbols_select(self, select):
        """股票池中点击删除股票池中对应的symbol"""
        # FIXME BUG 低版本ipywidgets下删除的不对
        self.choice_symbols.options = list(set(self.choice_symbols.options) - set(select['new']))


class WidgetSearchBox(WidgetBase):
    """搜索框ui界面"""

    # noinspection PyProtectedMember
    def __init__(self, search_result_callable):
        """构建股票池选股ui界面"""
        if not callable(search_result_callable):
            raise TypeError('search_result_select_func must callable!')
        # symbol搜索框构建
        self.search_bt = widgets.Button(description='搜索:', layout=widgets.Layout(height='10%', width='7%'))
        self.search_input = widgets.Text(
            value='',
            placeholder='请输入股票代码...',
            description='',
            disabled=False
        )
        # symbol搜索结果框
        self.search_result = widgets.SelectMultiple(
            options=[],
            description='搜索结果:',
            disabled=False,
            layout=widgets.Layout(width='300px', align_items='stretch', justify_content='space-between')
        )
        self.search_result.observe(search_result_callable, names='value')
        self.search_bt.on_click(self._do_search)

        # 搜索框 ＋ 按钮 ＋ 结果框 box拼接
        sc_hb = widgets.HBox([self.search_bt, self.search_input])
        self.widget = widgets.VBox([sc_hb, self.search_result])

    # noinspection PyUnusedLocal
    def _do_search(self, bt):
        """搜索框搜索执行函数"""
        ts_code = self.search_input.value
        if ts_code[0] == '0':
            ts_code += ".SZ"
        elif ts_code[0] == '6':
            ts_code += ".SH"
        code_data = data[data['ts_code'].isin([ts_code])]
        ts_name = code_data.name.values
        ts_code = ts_code[:6]
        for name in ts_name:
            self.search_result.options = [f'{name}:{ts_code}']
