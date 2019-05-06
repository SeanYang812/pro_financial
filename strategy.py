from ipywidgets import widgets, Button, Layout
from lib.commen import WidgetBase


class StrategyVisualization(WidgetBase):
    """策略管理可视化基础类"""

    def __init__(self, show_add_buy=True, add_button_style='default'):
        self.factor_dict = {}
        self.factor_wg_array = []
        # 策略候选池可x轴左右滚动
        self.factor_layout = widgets.Layout(overflow_x='scroll',
                                            # flex_direction='row',
                                            display='flex')
        self.selected_factors = widgets.SelectMultiple(
            options=[],
            description='已添加策略:',
            disabled=False,
            layout=widgets.Layout(width='100%', align_items='stretch')
        )
        words = ['均值回归策略', '双均线策略', '因子选股']

        # self.selected_factors.observe(self.add_factor(self.factor_dict), names='value')

        # 已添加的全局策略可点击删除
        self.selected_factors.observe(self.remove_factor, names='value')
        # 全局策略改变通知接收序列
        self.selected_factors_obs = set()
        # self.factor_box = [Button(description=w) for w in words]
        # 默认不启动可滚动因子界面，因为对外的widget版本以及os操作系统不统一
        self.scroll_factor_box = False
        self._sub_children_group_cnt = 3
        self.show_add_buy = show_add_buy
        self.add_button_style = add_button_style

        items_layout = Layout(width='auto')
        children = [Button(description=word, layout=items_layout, button_style='danger') for word in words]

        self.factor_layout = widgets.Layout(overflow_x='scroll',
                                            flex_direction='row',
                                            display='flex')

        self.factor_box = widgets.Box(children=children,
                                      layout=self.factor_layout)
        if self.factor_box is None:
            raise RuntimeError('_init_widget must build factor_box!')
        self.widget = widgets.VBox([self.factor_box, self.selected_factors])

    def register_subscriber(self, observe):
        """注册已选策略池更新通知"""
        self.selected_factors_obs.add(observe)

    def refresh_factor(self):
        """已选策略池刷新，通知其它更新"""
        self.selected_factors.options = list(self.factor_dict.keys())
        self.notify_subscriber()

    def notify_subscriber(self):
        """通知已选策略池发生改变的observe"""
        for observe in self.selected_factors_obs:
            if hasattr(observe, 'notify_subscriber'):
                observe.notify_subscriber()

    def remove_factor(self, select):
        """点击从策略池中删除已选择的策略"""
        for st_key in list(select['new']):
            self.factor_dict.pop(st_key)
        self.selected_factors.options = list(self.factor_dict.keys())
        # 通知其它需要一起更新的界面进行更新
        self.notify_subscriber()

    def add_factor(self, factor_dict, only_one=False):
        """根据具体策略提供的策略字典对象和策略描述构建上层策略序列"""
        print("你执行了添加策略")
        # if factor_desc_key in self.factor_dict:
        #     msg = u'{} 策略已经添加过，重复添加！'.format(to_unicode(factor_desc_key))
        #
        #     return
        if only_one:
            """
                非重复容器类型策略，如一个买入策略只能对应一个仓位管理策略
                大多数为可复容器类型策略，如可以有多个买入因子，多个卖出，
                多个选股因子
            """
            # 对基础类型不要使用clear等函数，py2低版本不支持
            # self.factor_dict.clear()
            self.factor_dict = {}
        self.factor_dict = factor_dict
        self.selected_factors.options = list(self.factor_dict.keys())
        # 通知其它需要一起更新的界面进行更新
        # self.notify_subscriber()
        # msg = u'{}策略已添加成功！'.format(to_unicode(factor_desc_key))
        # show_msg_toast_func(msg)


class Strategy(StrategyVisualization):
    """策略组织类"""

    def __init_widget(self):
        self.sf_array = []
        self.sf_array.append(MeanReversion(self))
        self.sf_array.append(DoubleAverages(self))
        self.sf_array.append(FactorStockPick(self))

        self.scroll_factor_box = False

        children = [sf() for sf in self.sf_array]

        self.factor_layout = widgets.Layout(overflow_x='scroll',
                                            flex_direction='row',
                                            display='flex')

        self.factor_box = widgets.Box(children=children,
                                      layout=self.factor_layout)


class WidgetFactorBase(WidgetBase):
    """策略可视化基础类"""

    def __init__(self, wg_manager):
        self.wg_manager = wg_manager
        self.widget = None
        self.label_layout = widgets.Layout(width='300px', align_items='stretch')
        self.description_layout = widgets.Layout(height='150px')
        self.widget_layout = widgets.Layout(align_items='stretch', justify_content='space-between')


class WidgetFactorBuyBase(WidgetFactorBase):
    """买入策略可视化基础类"""

    def __init__(self, wg_manager):
        super(WidgetFactorBuyBase, self).__init__(wg_manager)
        # if wg_manager.add_button_style == 'grid':
        #     add_cb = widgets.Button(description=u'添加为寻找买入策略最优参数组合', layout=widgets.Layout(width='98%'),
        #                             button_style='info')
        #     add_cb.on_click(self.add_buy_factor)
        #
        #     add_dp = widgets.Button(description=u'添加为寻找独立买入策略最佳组合', layout=widgets.Layout(width='98%'),
        #                             button_style='warning')
        #     add_dp.on_click(self.add_buy_factor_grid)
        #
        #     self.add = widgets.VBox([add_cb, add_dp])
        # else:
        self.add = widgets.Button(description='添加为全局策略', layout=widgets.Layout(width='98%'),
                                  button_style='info')
        self.add.on_click(self.add_buy_factor)
        # self._init_widget()

    def add_buy_factor(self, bt):
        """对应按钮添加策略，构建策略字典对象factor_dict以及唯一策略描述字符串factor_desc_key"""
        factor_dict, factor_desc_key = self.make_buy_factor_unique()
        self.wg_manager.add_factor(factor_dict, factor_desc_key)


class MeanReversion(StrategyVisualization):
    """
    均值回归策略:
    1. 均值回归：“跌下去的迟早要涨上来”
    2. 均值回归的理论基于以下观测：价格的波动一般会以它的均线为中心。也就是说，当标的价格由于波动而偏离移动均线时，它将调整并重新归于均线。
    3. 偏离程度：(MA-P)/MA
    4. 策略：在每个调仓日进行（每月调一次仓）
      4.1 计算池内股票的N日移动均线；
      4.2 计算池内所有股票价格与均线的偏离度；
      4.3 选取偏离度最高的num_stocks支股票并进行调仓。
    """

    def _init_widget(self):
        self.description = widgets.Textarea(
            value='日胜率均值回复策略：\n'
                  '1. 默认以40天为周期(8周)结合涨跌阀值计算周几适合买入\n'
                  '2. 回测运行中每一月重新计算一次上述的周几适合买入\n'
                  '3. 在策略日任务中买入信号为：昨天下跌，今天开盘也下跌，且明天是计算出来的上涨概率大的\'周几\'',
            description='周涨胜率',
            disabled=False,
            layout=self.description_layout
        )

        self.buy_dw_label = widgets.Label('代表周期胜率阀值，默认0.55即55%的胜率',
                                          layout=self.label_layout)
        self.buy_dw = widgets.FloatSlider(
            value=0.55,
            min=0.50,
            max=0.99,
            step=0.01,
            description='胜率',
            disabled=False,
            orientation='horizontal',
            readout=True,
            readout_format='.2f',
        )
        self.buy_dw_box = widgets.VBox([self.buy_dw_label, self.buy_dw])

        self.buy_dwm_label = widgets.Label('代表涨幅比例阀值系数，默认0.618',
                                           layout=self.label_layout)
        self.buy_dwm = widgets.FloatSlider(
            value=0.618,
            min=0.50,
            max=1.0,
            step=0.01,
            description='系数',
            disabled=False,
            orientation='horizontal',
            readout=True,
            readout_format='.3f'
        )
        self.buy_dwm_box = widgets.VBox([self.buy_dwm_label, self.buy_dwm])

        self.dw_period_label = widgets.Label('代表分所使用的交易周期，默认40天周期(8周)',
                                             layout=self.label_layout)
        self.dw_period = widgets.IntSlider(
            value=40,
            min=20,
            max=120,
            step=1,
            description='周期',
            disabled=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        self.dw_period_box = widgets.VBox([self.dw_period_label, self.dw_period])
        self.widget = widgets.VBox([self.description, self.buy_dw_box,
                                    self.buy_dwm_box, self.dw_period_box, self.add],  # border='solid 1px',
                                   layout=self.widget_layout)

    def make_buy_factor_unique(self):
        """对应按钮添加双均线策略，构建策略字典对象factor_dict以及唯一策略描述字符串factor_desc_key"""
        factor_dict = {'class': AbuFactorBuyWD, 'buy_dw': self.buy_dw.value,
                       'buy_dwm': self.buy_dwm.value, 'dw_period': self.dw_period.value}
        factor_desc_key = '日胜率{},{},{}均值回复买入'.format(
            self.buy_dw.value, self.buy_dwm.value, self.dw_period.value)
        return factor_dict, factor_desc_key


class DoubleAverages(WidgetFactorBase):
    """
    双均线策略:
    1. 预设两条均线：如一个ma=5，一个ma=60, 5的均线被称作快线，60的均线被称作慢线
    2. 择时买入策略中当快线上穿慢线（ma5上穿ma60）称为形成金叉买点信号，买入股票
    3. 自适应动态慢线，不需要输入慢线值，根据走势震荡套利空间，寻找合适的ma慢线
    4. 自适应动态快线，不需要输入快线值，根据慢线以及大盘走势，寻找合适的ma快线
    """

    def _init_widget(self):
        """构建AbuDoubleMaBuy策略参数界面"""

        self.description = widgets.Textarea(
            value=u'动态自适应双均线买入策略：\n'
                  u'双均线策略是量化策略中经典的策略之一，其属于趋势跟踪策略: \n'
                  u'1. 预设两条均线：如一个ma=5，一个ma=60, 5的均线被称作快线，60的均线被称作慢线\n'
                  u'2. 择时买入策略中当快线上穿慢线（ma5上穿ma60）称为形成金叉买点信号，买入股票\n'
                  u'3. 自适应动态慢线，不需要输入慢线值，根据走势震荡套利空间，寻找合适的ma慢线\n'
                  u'4. 自适应动态快线，不需要输入快线值，根据慢线以及大盘走势，寻找合适的ma快线',
            description=u'双均线买',
            disabled=False,
            layout=self.description_layout
        )

        self.slow_label = widgets.Label(u'默认使用动态慢线，可手动固定慢线值', layout=self.label_layout)
        self.slow_int = widgets.IntSlider(
            value=60,
            min=10,
            max=120,
            step=1,
            description=u'手动',
            disabled=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        self.auto_slow = widgets.Checkbox(
            value=True,
            description=u'动态慢线',
            disabled=False
        )

        def slow_change(change):
            self.slow_int.disabled = change['new']

        self.auto_slow.observe(slow_change, names='value')
        self.slow = widgets.VBox([self.auto_slow, self.slow_int])
        self.slow_box = widgets.VBox([self.slow_label, self.slow])

        self.fast_label = widgets.Label(u'默认使用动态快线，可手动固定快线值', layout=self.label_layout)
        self.fast_int = widgets.IntSlider(
            value=5,
            min=1,
            max=90,
            step=1,
            description=u'手动',
            disabled=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        self.auto_fast = widgets.Checkbox(
            value=True,
            description=u'动态快线',
            disabled=False,
        )

        def fast_change(change):
            self.fast_int.disabled = change['new']

        self.auto_fast.observe(fast_change, names='value')
        self.fast = widgets.VBox([self.auto_fast, self.fast_int])
        self.fast_box = widgets.VBox([self.fast_label, self.fast])

        self.widget = widgets.VBox([self.description, self.slow_box, self.fast_box, self.add],  # border='solid 1px',
                                   layout=self.widget_layout)

    def make_buy_factor_unique(self):
        """对应按钮添加AbuDoubleMaBuy策略，构建策略字典对象factor_dict以及唯一策略描述字符串factor_desc_key"""
        slow_int = -1 if self.auto_slow.value else self.slow_int.value
        fast_int = -1 if self.auto_fast.value else self.fast_int.value

        factor_dict = {'class': AbuDoubleMaBuy, 'slow': slow_int, 'fast': fast_int}
        factor_desc_key = u'动态双均慢{}快{}买入'.format(
            u'动态' if slow_int == -1 else slow_int, u'动态' if fast_int == -1 else fast_int)
        return factor_dict, factor_desc_key


class TurtleStrategy(StrategyVisualization):
    """
    海龟策略：

    """
    pass


class FactorStockPick(StrategyVisualization):
    """
    因子选股：

    """
    pass
