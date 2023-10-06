from __future__ import annotations

from typing import TYPE_CHECKING

from trame.decorators import change
from trame.widgets import vuetify

from simview.apptrame.app.base import AppExtend
from simview.apptrame.app.views.base_components import ui_card
from simview.apptrame.app.views.view_graphs import PLOTS

if TYPE_CHECKING:
    from simview.apptrame.app.main import App


class PlotterUI(AppExtend):
    @change("active_plot")
    def on_active_plot_change(self, active_plot, **kwargs):
        print("updated -> ", active_plot)
        self.app.ctrl.figure_update(PLOTS[active_plot]())

    def toggle_table(self, *args):
        self.app.state.table_view = not self.app.state.table_view
        self.app.ctrl.view_update()


def plotter_drawer(app: App):
    app.state.table_view = False
    pui = PlotterUI(app)
    with ui_card("Plotter", pui.toggle_table):
        with vuetify.VCol(v_show=f"table_view == true", dense=True):
            vuetify.VSelect(
                label="Plot",
                v_model=("active_plot", "Table"),
                items=("plots", list(PLOTS.keys())),
                hide_details=True,
                dense=True,
                outlined=True,
                classes="pt-2",
            )
