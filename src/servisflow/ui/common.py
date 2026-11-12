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
from servisflow.services import vehicles
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
    """Kuruşu Türkçe biçimde TL olarak yazar: 160000 → '1.600 TL'.

    Tutarlar tam TL girilir (BR-01 v1.4); eski kayıtlarda kuruş varsa
    '1.600,50 TL' biçiminde gösterilir. Hesap Decimal iledir (ADR-003).
    """
    value = Decimal(kurus) / 100
    text = f"{value:,.0f}" if kurus % 100 == 0 else f"{value:,.2f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".") + " TL"


def amount_from_input(value: int | float) -> Decimal:
    """Sayı alanının değerini Decimal'e çevirir.

    Alan tam sayı adımlıdır ve int döndürür. Yine de float gelirse
    `Decimal(str(x))` girilen değeri korur; `Decimal(1.15)` 1.1499... olurdu.
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


def plate_matches(text: str) -> list[dict]:
    """Plakanın başıyla eşleşen araçlar, düz veri olarak (KR-09)."""

    def find(session):
        return [
            {
                "id": v.id,
                "label": f"{v.plate_normalized} · {v.brand} {v.model}"
                f" · {v.customer.full_name}",
            }
            for v in vehicles.suggest_plates(session, text)
        ]

    return run(find) or []
