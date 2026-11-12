"""Ekranların ortak parçaları: veritabanı bağlantısı ve servis çağrısı sarmalayıcısı."""

from collections.abc import Callable
from typing import TypeVar

import streamlit as st
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from servisflow.repository.db import (
    default_url,
    init_db,
    make_engine,
    make_session_factory,
)
from servisflow.services.errors import ServisFlowError

T = TypeVar("T")


@st.cache_resource
def get_engine(url: str) -> Engine:
    engine = make_engine(url)
    init_db(engine)
    return engine


def new_session() -> Session:
    return make_session_factory(get_engine(default_url()))()


def session_scope():
    """Her işlem kendi veritabanı işleminde: başarıda commit, hatada rollback."""
    return make_session_factory(get_engine(default_url())).begin()


def run(action: Callable[[Session], T], success: str | None = None) -> T | None:
    """Servis çağrısını tek işlemde yürütür; iş kuralı hatasını kullanıcıya gösterir.

    Yalnızca `ServisFlowError` türevleri gösterilir; diğer hatalar Streamlit'in
    genel hata mesajına düşer, ayrıntı tarayıcıya gitmez (ADR-007, NFR-08).
    Dönen değer oturum kapandıktan sonra kullanılacağı için düz veri olmalıdır.
    """
    try:
        with session_scope() as session:
            result = action(session)
    except ServisFlowError as exc:
        st.error(str(exc))
        return None
    if success:
        st.success(success)
    return result
