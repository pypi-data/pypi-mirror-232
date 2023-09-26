from pathlib import Path
from streamlit.components.v1 import declare_component
import os

if os.environ.get("RELEASE_BUILD") == "true":
    ELEMENTS_FRONTEND = {
        "path": (Path(version.__file__).parent / "frontend/build").resolve()
    }
else:
    ELEMENTS_FRONTEND = {"url": "http://localhost:3001"}

render_component = declare_component("streamlit_monaco", **ELEMENTS_FRONTEND)
