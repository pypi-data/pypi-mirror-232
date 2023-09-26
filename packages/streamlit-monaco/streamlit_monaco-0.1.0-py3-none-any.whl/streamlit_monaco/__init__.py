from streamlit_monaco.render import render_component

__version__ = "0.1.0"


def st_monaco(
    value="",
    height="200px",
    language="markdown",
):
    return render_component(
        value=value,
        height=height,
        language=language,
    )
