"""Streamlit giriş noktası: `streamlit run src/servisflow/ui/app.py`."""

import streamlit as st

from servisflow.repository.db import init_db, make_engine


@st.cache_resource
def get_engine():
    engine = make_engine()
    init_db(engine)
    return engine


def main() -> None:
    st.set_page_config(page_title="ServisFlow")
    get_engine()
    st.title("ServisFlow")
    st.info("Uygulama iskeleti hazır. Ekranlar use case PR'larıyla eklenecek.")


main()
