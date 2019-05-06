import ipywidgets as widgets  # 创建窗体GUI

from interface.basetest_data import WidgetTrad
from interface.basetest_time import WidgetTime
from interface.stock_picking.xuanguui import StockPool
from lib.commen import WidgetBase
from strategy import Strategy
from interface import deal

class WidgetRunTT(WidgetTrad, WidgetTime):
    """基础设置界面：初始资金，回测开始，结束周期，参考大盘等"""

    def __init__(self):
        """初始化基础回测设置界面"""
        # 初始资金
        self.cash = widgets.BoundedIntText(
            value=1000000,
            min=10000,
            max=999999999,
            step=1,
            description='初始资金:',
            disabled=False
        )
        # 时间模式设置
        tm_box = self.init_time_mode_ui()

        # 回测结果设置
        metrics_box = self.init_metrics_ui()

        self.widget = widgets.VBox([self.cash, tm_box, metrics_box])



class BackTest(WidgetBase):

    def __init__(self):
        """构建回测需要的各个组件形成"""
        # 基本页面
        self.tt = WidgetRunTT()
        # 股池
        self.sc = StockPool()
        # 选股策略
        self.bf = Strategy()
        sub_widget_tab = widgets.Tab()
        sub_widget_tab.children = [self.tt.widget, self.sc.widget, self.bf.widget]
        for ind, name in enumerate(['基本', '股池', '策略']):
            sub_widget_tab.set_title(ind, name)

        self.run_loop_bt = widgets.Button(description='开始回测', layout=widgets.Layout(width='98%'),
                                          button_style='danger')
        self.run_loop_bt.on_click(self.run_loop_back)
        self.widget = widgets.VBox([sub_widget_tab, self.run_loop_bt])

    def run_loop_back(self, bt):
        """运行回测所对应的button按钮"""
        # 清理之前的输出结果
        # ABuProgress.clear_output()

        base_run = self.tt
        # 初始资金
        cash = base_run.cash.value
        n_folds = 2
        start = None
        end = None
        if not base_run.run_years.disabled:
            # 如果使用年回测模式
            n_folds = base_run.run_years.value
        if not base_run.start.disabled:
            # 使用开始回测日期
            start = base_run.start.value
        if not base_run.end.disabled:
            # 使用结束回测日期
            end = base_run.end.value

        choice_symbols = self.sc.choice_symbols.options
        if choice_symbols is not None and len(choice_symbols) == 0:
            # 如果一个symbol都没有设置None， 将使用选择的市场进行全市场回测
            choice_symbols = None

        if choice_symbols is not None and len(choice_symbols) == 1:
            # 如果只有1支股票回测，直接使用这个股票做为做为对比基准
            pass
        else:
            # 多只股票情况
            # 多只股票使用run_loop_back
            abu_result_tuple, _ = deal.deal_func(cash,
                                                 # buy_factors,
                                                 # sell_factors,
                                                 # stock_picks,
                                                 choice_symbols=choice_symbols,
                                                 start=start,
                                                 end=end,
                                                 n_folds=n_folds)

        # 买入策略构成序列
        # buy_factors = list(self.bf.factor_dict.values())
        # if len(buy_factors) == 0:
        #     msg = '没有添加任何一个买入策略！'
        #     show_msg_toast_func(msg)
        #     return
        # # ump收尾工作
        # self.ump.run_end(abu_result_tuple, choice_symbols, list(self.bf.factor_dict.keys()),
        #                  list(self.sf.factor_dict.keys()), list(self.ps.factor_dict.keys()))
