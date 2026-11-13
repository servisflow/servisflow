"""Streamlit giriş noktası: `streamlit run src/servisflow/ui/app.py`.

Arayüz yalnızca `services` katmanını çağırır (ADR-001). Oturum açılmadan giriş
ekranı dışında hiçbir ekran çizilmez (FR-01, TC-03).
"""

import logging

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from servisflow.services import auth
from servisflow.services.clock import ISTANBUL, SystemClock
from servisflow.services.errors import ServisFlowError
from servisflow.ui import customers_page, reports_page, visits_page
from servisflow.ui.common import DB_ERROR_MESSAGE, new_session, session_scope

logger = logging.getLogger("servisflow")

USER_KEY = "user_id"
CAPTCHA_KEY = "captcha"
FAILED_KEY = "failed_attempts"
LAST_NAME_KEY = "last_username"
ERROR_KEY = "login_error"

PAGES = {
    "Ana sayfa": None,
    "Müşteriler ve araçlar": customers_page.render,
    "Servis ve işler": visits_page.render,
    "Rapor": reports_page.render,
}


def bootstrap_owner() -> None:
    """Bulut kurulumu: sırlarda `[owner]` varsa ve hesap yoksa hesabı oluşturur.

    Streamlit Community Cloud'da kabuk olmadığı için `create_owner` betiği
    çalışmaz; veritabanı yeniden başlatmada silinebildiği için hesap her
    açılışta sırlardan geri gelir. Sır yoksa (yerel kurulum) hiçbir şey yapmaz.
    Parola depoya girmez, yalnızca bulutun sır ayarındadır (Faz 4 - iv).
    """
    try:
        owner = st.secrets["owner"]
        username, password = owner["username"], owner["password"]
    except (FileNotFoundError, KeyError):
        return
    try:
        with session_scope() as session:
            if auth.ensure_owner(session, username, password):
                logger.info("Sorumlu hesabı sırlardan oluşturuldu.")
    except ServisFlowError as exc:
        logger.error("Sırlardaki sorumlu hesabı geçersiz: %s", exc)


def _captcha_needed() -> bool:
    name = st.session_state.get(LAST_NAME_KEY)
    if not name:
        return False
    with session_scope() as session:
        return auth.captcha_required(session, name)


def login_page() -> None:
    st.title("ServisFlow")
    st.subheader("Giriş")
    if ERROR_KEY in st.session_state:
        st.error(st.session_state.pop(ERROR_KEY))
    needs_captcha = _captcha_needed()
    if needs_captcha and CAPTCHA_KEY not in st.session_state:
        st.session_state[CAPTCHA_KEY] = auth.new_captcha()

    with st.form("giris"):
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Parola", type="password")
        answer = None
        if needs_captcha:
            question, _ = st.session_state[CAPTCHA_KEY]
            answer = st.text_input(f"Robot doğrulaması: {question}")
        submitted = st.form_submit_button("Giriş yap")

    if submitted:
        _try_login(username, password, answer)


def _try_login(username: str, password: str, answer: str | None) -> None:
    captcha = st.session_state.pop(CAPTCHA_KEY, None)
    passed = captcha is not None and auth.check_captcha(captcha[1], answer)
    st.session_state[LAST_NAME_KEY] = username
    # `begin()` hata görünce rollback yapar; ama başarısız deneme kaydı
    # (LoginAttempt) kalmalı (FR-01). Bu yüzden oturum elle yönetilir ve
    # hata durumunda da commit edilir.
    session = new_session()
    try:
        user = auth.authenticate(session, SystemClock(), username, password, passed)
        failed = auth.failed_attempts_since_last_login(session, username)
        session.commit()
    except ServisFlowError as exc:
        session.commit()
        # Sayfa yeniden çizilir ki 3. hatadan sonra CAPTCHA alanı hemen çıksın;
        # yoksa form, deneme kaydedilmeden önceki duruma göre çizilmiş kalır.
        st.session_state[ERROR_KEY] = str(exc)
        st.rerun()
    finally:
        session.close()
    st.session_state[USER_KEY] = user.id
    st.session_state[FAILED_KEY] = failed
    st.rerun()


def logout() -> None:
    """Oturum durumunun tamamı silinir; geri tuşu yalnızca giriş ekranını gösterir."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def home_page() -> None:
    st.title("ServisFlow")
    failed = st.session_state.pop(FAILED_KEY, [])
    if failed:
        lines = "\n".join(
            f"- {t.astimezone(ISTANBUL):%d.%m.%Y %H:%M:%S}" for t in failed
        )
        st.warning(f"Son girişinizden bu yana {len(failed)} hatalı deneme:\n{lines}")
    st.info("Soldaki menüden bir ekran seçin.")


def app_page() -> None:
    with st.sidebar:
        page = st.radio("Menü", list(PAGES), key="menu")
        st.button("Çıkış yap", on_click=logout)
    render = PAGES[page]
    if render is None:
        home_page()
    else:
        render()


def main() -> None:
    # NFR-08: yalnızca genel hata mesajı. Ayar koddan da verilir ki uygulama
    # repo kökü dışından başlatıldığında da geçerli olsun (PR #10 incelemesi).
    st.set_option("client.showErrorDetails", "none")
    st.set_page_config(page_title="ServisFlow")
    try:
        bootstrap_owner()
        if st.session_state.get(USER_KEY) is None:
            login_page()
        else:
            app_page()
    except SQLAlchemyError:
        # TC-30: veritabanına erişilemezse kullanıcı yalnızca genel mesajı görür;
        # ayrıntı (yığın izi, dosya yolu, SQL) yalnızca sunucu günlüğüne yazılır
        # (ADR-007, R-08). st.rerun'un istisnası bu türden olmadığı için etkilenmez.
        logger.exception("Veritabanı hatası")
        st.error(DB_ERROR_MESSAGE)


main()
