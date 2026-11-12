"""Ekranların ortak parçaları: veritabanı bağlantısı ve servis çağrısı sarmalayıcısı."""

from collections.abc import Callable
from decimal import Decimal
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


def tl(kurus: int) -> str:
    """Kuruşu Türkçe biçimde TL olarak yazar: 160050 → '1.600,50 TL'.

    Hesap Decimal ile yapılır; float yalnızca yuvarlama hatası getirirdi (ADR-003).
    """
    text = f"{Decimal(kurus) / 100:,.2f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".") + " TL"


def amount_from_input(value: float) -> Decimal:
    """`st.number_input` float döndürür; `Decimal(str(x))` girilen değeri korur.

    `Decimal(1.15)` 1.1499999... olurdu; `str(1.15)` ise '1.15' verir (ADR-003).
    """
    return Decimal(str(value))


FLASH_OK = "flash_ok"
FLASH_ERROR = "flash_error"


def act(action: Callable[[Session], object], success: str) -> None:
    """Düğmeyle tetiklenen işlemi yürütür ve sayfayı yeniden çizer.

    Liste, işlemden önce çizildiği için sonuç ancak yeniden çizimde görünür;
    mesaj oturum durumunda taşınır ve `show_flash` ile sayfanın başında gösterilir.
    """
    try:
        with session_scope() as session:
            action(session)
    except ServisFlowError as exc:
        st.session_state[FLASH_ERROR] = str(exc)
    else:
        st.session_state[FLASH_OK] = success
    st.rerun()


def show_flash() -> None:
    if FLASH_ERROR in st.session_state:
        st.error(st.session_state.pop(FLASH_ERROR))
    if FLASH_OK in st.session_state:
        st.success(st.session_state.pop(FLASH_OK))
