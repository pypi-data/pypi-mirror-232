import os

import streamlit.components.v1 as components

_RELEASE = True
if not _RELEASE:
    _component_func = components.declare_component(
        "radiflow_folder_upload",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "radiflow_folder_upload", path=build_dir
    )


def radiflow_folder_upload(websocket_url: str, key=None):
    component_value = _component_func(
        websocket_url=websocket_url, key=key, default=None
    )
    return component_value
