"""Streamlit giriş noktası: `streamlit run src/servisflow/ui/app.py`.

Arayüz yalnızca `services` katmanını çağırır (ADR-001). Oturum açılmadan giriş
ekranı dışında hiçbir ekran çizilmez (FR-01, TC-03).
"""

import logging

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from servisflow.services import auth, customers, reports, vehicles
from servisflow.services.clock import ISTANBUL, SystemClock
from servisflow.services.errors import ServisFlowError
from servisflow.ui import customers_page, reports_page, visits_page
from servisflow.ui.common import (
    DB_ERROR_MESSAGE,
    ICON,
    LOGO,
    new_session,
    page_header,
    run,
    session_scope,
    tl,
)

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
MENU_ICONS = {
    "Ana sayfa": ":material/dashboard:",
    "Müşteriler ve araçlar": ":material/group:",
    "Servis ve işler": ":material/car_repair:",
    "Rapor": ":material/bar_chart:",
}
MENU_KEY = "menu"


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
    _, middle, _ = st.columns([1, 1.2, 1])
    with middle:
        st.image(ICON, width=72)
        st.title("ServisFlow", anchor=False)
        st.caption("Oto servis iş takibi ve dönemsel iş raporu")
        with st.container(border=True):
            _login_form()


def _login_form() -> None:
    st.subheader("Giriş", anchor=False)
    if ERROR_KEY in st.session_state:
        st.error(st.session_state.pop(ERROR_KEY))
    needs_captcha = _captcha_needed()
    if needs_captcha and CAPTCHA_KEY not in st.session_state:
        st.session_state[CAPTCHA_KEY] = auth.new_captcha()

    with st.form("giris", border=False):
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Parola", type="password")
        answer = None
        if needs_captcha:
            question, _ = st.session_state[CAPTCHA_KEY]
            answer = st.text_input(f"Robot doğrulaması: {question}")
        submitted = st.form_submit_button(
            "Giriş yap", type="primary", use_container_width=True
        )

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


def _dashboard(session, today) -> dict:
    """Ana sayfa özeti; toplamlar rapor servisinden gelir (BR-05)."""

    def total(kind):
        return reports.gross_total(session, *reports.period_bounds(kind, today))

    day_bounds = reports.period_bounds(reports.PERIOD_DAY, today)
    open_count, open_total = reports.open_work(session)
    return {
        "today": total(reports.PERIOD_DAY),
        "week": total(reports.PERIOD_WEEK),
        "month": total(reports.PERIOD_MONTH),
        "open_count": open_count,
        "open_total": open_total,
        "customers": len(customers.search_customers(session, "")),
        "vehicles": len(vehicles.list_vehicles(session)),
        "done_today": [
            {
                "Saat": f"{t.completed_at.astimezone(ISTANBUL):%H:%M}",
                "Plaka": vehicles.format_plate(t.visit.vehicle.plate_normalized),
                "İş": t.title,
                "Tutar": tl(t.amount_kurus),
            }
            for t in reports.completed_tasks(session, *day_bounds)
        ],
    }


def _go(page: str) -> None:
    st.session_state[MENU_KEY] = page


def _metric_cards(data: dict) -> None:
    cards = [
        ("Bugün tamamlanan", tl(data["today"])),
        ("Bu hafta", tl(data["week"])),
        ("Bu ay", tl(data["month"])),
        (f"Açık işler ({data['open_count']})", tl(data["open_total"])),
    ]
    for column, (label, value) in zip(st.columns(4), cards):
        with column.container(border=True):
            st.metric(label, value)


def _quick_actions(data: dict) -> None:
    st.markdown("**Hızlı işlemler**")
    for label, page, icon in (
        ("Müşteri veya araç ekle", "Müşteriler ve araçlar", ":material/person_add:"),
        ("Ziyaret aç, iş gir", "Servis ve işler", ":material/build:"),
        ("Dönem raporu", "Rapor", ":material/bar_chart:"),
    ):
        st.button(
            label, icon=icon, on_click=_go, args=(page,), use_container_width=True
        )
    st.caption(f"{data['customers']} müşteri · {data['vehicles']} araç kayıtlı")


def home_page() -> None:
    today = SystemClock().now().astimezone(ISTANBUL).date()
    page_header("Genel bakış", f"{today:%d.%m.%Y} · Tamamlanan işler ve açık işler")
    failed = st.session_state.pop(FAILED_KEY, [])
    if failed:
        lines = "\n".join(
            f"- {t.astimezone(ISTANBUL):%d.%m.%Y %H:%M:%S}" for t in failed
        )
        st.warning(f"Son girişinizden bu yana {len(failed)} hatalı deneme:\n{lines}")
    data = run(lambda s: _dashboard(s, today))
    if data is None:
        return
    _metric_cards(data)
    left, right = st.columns([2, 1])
    with left.container(border=True):
        st.markdown("**Bugün tamamlanan işler**")
        if data["done_today"]:
            st.dataframe(data["done_today"], hide_index=True, use_container_width=True)
        else:
            st.caption("Bugün henüz ✓ ile tamamlanan iş yok.")
    with right.container(border=True):
        _quick_actions(data)


def app_page() -> None:
    with st.sidebar:
        page = st.radio(
            "Menü",
            list(PAGES),
            format_func=lambda name: f"{MENU_ICONS[name]} {name}",
            key=MENU_KEY,
        )
        st.divider()
        st.button(
            "Çıkış yap",
            icon=":material/logout:",
            on_click=logout,
            use_container_width=True,
        )
    render = PAGES[page]
    if render is None:
        home_page()
    else:
        render()


def main() -> None:
    # NFR-08: yalnızca genel hata mesajı. Ayar koddan da verilir ki uygulama
    # repo kökü dışından başlatıldığında da geçerli olsun (PR #10 incelemesi).
    st.set_option("client.showErrorDetails", "none")
    st.set_page_config(page_title="ServisFlow", page_icon=ICON, layout="wide")
    st.logo(LOGO, icon_image=ICON, size="large")
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
