from ipywidgets import widgets
import os
from conf import settings

widgets.DatePicker(
    description='Pick a Date',
    disabled=False
)
class WidgetTrad(object):
    """
        1. 输出度量对象：
            1. 只输出交易单：orders_pd
            2. 只输出行为单：action_pd
            3. 只输出资金单：capital_pd
            4. 同时输出交易单，行为单，资金单(orders_pd, action_pd, capital_pd)
        2. 输出交易单最大行列显示设置：
            1. 默认最大行显示50
            2. 默认最大列显示50
        3. 是否将交易单，行为单，资金单保存在本地output文件中
    """
    def init_metrics_ui(self):
        """构建基础env widget ui return widgets.VBox"""

        self.metrics_out_put = widgets.RadioButtons(
            options={'只输出交易单：orders_pd': 0,
                     '只输出行为单：action_pd': 1,
                     '只输出资金单：capital_pd': 2,
                     '输出交易单，行为单，资金单': 3},
            value=0,
            description='输出对象:',
            disabled=False
        )

        out_put_display_max_label1 = widgets.Label('输出显示最大行列数，最大100行，100列',
                                                   layout=widgets.Layout(width='300px', align_items='stretch'))
        out_put_display_max_label2 = widgets.Label('如需查看更多输出表单，请选择保存输出至文件',
                                                   layout=widgets.Layout(width='300px', align_items='stretch'))
        self.out_put_display_max_rows = widgets.IntSlider(
            value=50,
            min=1,
            max=100,
            step=1,
            description='行数',
            disabled=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )

        self.out_put_display_max_columns = widgets.IntSlider(
            value=50,
            min=1,
            max=100,
            step=1,
            description='列数',
            disabled=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        out_put_display = widgets.VBox([out_put_display_max_label1,
                                        out_put_display_max_label2,
                                        self.out_put_display_max_rows,
                                        self.out_put_display_max_columns])

        save_out_put_lable = widgets.Label('是否保存交易单，行为单，资金单到文件',
                                           layout=widgets.Layout(width='300px', align_items='stretch'))
        save_out_put_lable2 = widgets.Label('路径:{}'.format(os.path.join(settings.BASE_DIR, 'out_put')),
                                            layout=widgets.Layout(width='300px', align_items='stretch'))
        self.save_out_put = widgets.Checkbox(
            value=False,
            description='保存输出',
            disabled=False,
        )
        save_out_put = widgets.VBox([save_out_put_lable,
                                     save_out_put_lable2,
                                     self.save_out_put])

        accordion = widgets.Accordion()
        accordion.children = [widgets.VBox([self.metrics_out_put, out_put_display, save_out_put])]
        accordion.set_title(0, '回测度量结果设置')

        return accordion
