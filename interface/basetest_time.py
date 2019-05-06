from ipywidgets import widgets

class WidgetTime(object):
    """
        使用混入而不要做为上层widget拥有的模式，可为多个上层使用
        便于上层widgte使用self去获取设置，统一上层使用
        混入类：基础时间模式设置：
        1. 年数模式
        2. 开始结束模式
    """

    # noinspection PyProtectedMember
    def init_time_mode_ui(self):
        """构建基础env widget ui return widgets.VBox"""
        # 回测时间模式
        self.time_mode = widgets.RadioButtons(
            options={'使用回测年数': 0,
                     '使用回测开始结束日期': 1},
            value=0,
            description='时间模式:',
            disabled=False
        )
        self.time_mode.observe(self.on_time_mode_change, names='value')
        # 年数模式
        self.run_years = widgets.BoundedIntText(
            value=2,
            min=1,
            max=6,
            step=1,
            description='回测年数:',
            disabled=False
        )
        # 开始结束模式
        self.start = widgets.Text(
            value='2015-01-01',
            placeholder='年-月-日',
            description='开始日期:',
            disabled=False
        )
        self.end = widgets.Text(
            value='2019-04-26',
            placeholder='年-月-日',
            description='结束日期:',
            disabled=False
        )
        self.run_years.disabled = False
        self.start.disabled = True
        self.end.disabled = True

        return widgets.VBox([self.time_mode, self.run_years, self.start, self.end])

    def on_time_mode_change(self, change):
        """切换使用年数还是起始，结束时间做为回测参数"""
        if change['new'] == 0:
            self.run_years.disabled = False
            self.start.disabled = True
            self.end.disabled = True
        else:
            self.run_years.disabled = True
            self.start.disabled = False
            self.end.disabled = False



