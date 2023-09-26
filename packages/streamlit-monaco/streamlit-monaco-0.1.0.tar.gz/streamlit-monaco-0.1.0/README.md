# 📝 Streamlit Monaco

[![GitHub][github_badge]][github_link] [![PyPI][pypi_badge]][pypi_link]

## Installation

```sh
pip install streamlit-monaco
```

## Getting started

```python
from streamlit_monaco import st_monaco
import streamlit as st

st.title("Streamlit Markdown Editor")

content = st_monaco(value="# Hello world", height="600px", language="markdown")

if st.button("Show editor's content"):
    st.write(content)
```




[github_badge]: https://badgen.net/badge/icon/GitHub?icon=github&color=black&label
[github_link]: https://github.com/marcusschiesser/streamlit-monaco
[pypi_badge]: https://badgen.net/pypi/v/streamlit-monaco?icon=pypi&color=black&label
[pypi_link]: https://pypi.org/project/streamlit-monaco
