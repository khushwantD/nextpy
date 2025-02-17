from typing import Dict, List, Tuple
import nextpy as xt
from nextpy.frontend.components.leaflet import (
    map_container,
    tile_layer,
    marker,
    popup,
    )


class State(xt.State):
    """The app state."""

    pass


def index():
    return xt.center(
        map_container(
            tile_layer(
                attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            ),
            center=[51.505, -0.09],
            zoom=13,
            scroll_wheel_zoom=True,
            height="98vh",
            width="100%",
        ),
    )


# Add state and page to the app.
app = xt.App(state=State)
app.add_page(index)