import streamlit as st
from radiflow_folder_upload import radiflow_folder_upload

status = radiflow_folder_upload(
    "Monitor", "ws://localhost:8010/feature-manager/monitor-job-ws", "test"
)
st.write(status)
