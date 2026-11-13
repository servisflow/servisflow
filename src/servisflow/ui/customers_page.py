"""UC-02 ve UC-03 ekranı: müşteri kaydı, arama, güncelleme ve araç ekleme."""

import streamlit as st

from servisflow.services import customers, vehicles
from servisflow.services.clock import SystemClock
from servisflow.ui.common import page_header, plate_matches, run


def _customer_data(customer) -> dict:
    """Oturum kapanmadan önce ilişkileri de okunmuş düz veri."""
    return {
        "id": customer.id,
        "name": customer.full_name,
        "phone": customer.phone,
        "vehicles": [
            {
                "id": v.id,
                "plate": v.plate_normalized,
                "brand": v.brand,
                "model": v.model,
            }
            for v in customer.vehicles
        ],
    }


def _new_customer_form() -> None:
    with st.expander("Yeni müşteri", icon=":material/person_add:"):
        with st.form("yeni_musteri"):
            name = st.text_input("Ad soyad", key="yeni_ad")
            phone = st.text_input("Telefon (isteğe bağlı)", key="yeni_tel")
            if st.form_submit_button("Kaydet", type="primary"):
                run(
                    lambda s: customers.create_customer(s, SystemClock(), name, phone),
                    "Müşteri kaydedildi.",
                )


def _plate_search() -> None:
    plate = st.text_input(
        "Plakayla araç bul (ilk karakterler yeterli)",
        key="plaka_ara",
        icon=":material/directions_car:",
    )
    if not plate.strip():
        return
    matches = plate_matches(plate)
    if not matches:
        st.warning("Bu başlangıçla kayıtlı plaka yok (en az 2 karakter girin).")
    for match in matches:
        st.info(match["label"])


def _edit_form(row: dict) -> None:
    # Anahtarlar müşteri kimliğini içerir. Sabit anahtarlı alan Streamlit'te
    # değerini korur ve `value` yok sayılır; başka müşteri seçilince form
    # öncekinde kalıyor, "Güncelle" onun bilgisini yazıyordu (H4-02, TC-31).
    cid = row["id"]
    with st.form(f"duzenle_{cid}"):
        name = st.text_input("Ad soyad", value=row["name"], key=f"duz_ad_{cid}")
        phone = st.text_input("Telefon", value=row["phone"] or "", key=f"duz_tel_{cid}")
        if st.form_submit_button("Güncelle"):
            run(
                lambda s: customers.update_customer(s, row["id"], name, phone),
                "Müşteri güncellendi.",
            )


def _vehicle_form(row: dict) -> None:
    with st.form(f"arac_{row['id']}"):
        st.markdown("**Araç ekle**")
        # Yarım kalan araç bilgisi başka müşteriye taşınmasın (H4-02).
        plate = st.text_input("Plaka", key=f"arac_plaka_{row['id']}")
        brand = st.text_input("Marka", key=f"arac_marka_{row['id']}")
        model = st.text_input("Model", key=f"arac_model_{row['id']}")
        if st.form_submit_button("Aracı kaydet", icon=":material/add:"):
            run(
                lambda s: vehicles.register_vehicle(s, row["id"], plate, brand, model),
                "Araç kaydedildi.",
            )


def render() -> None:
    page_header("Müşteriler ve araçlar", "Müşteri kaydı, arama ve araç ekleme")
    _new_customer_form()
    left, right = st.columns(2)
    with left.container(border=True):
        text = st.text_input(
            "Müşteri ara (ad veya telefon)",
            key="musteri_ara",
            icon=":material/search:",
        )
    with right.container(border=True):
        _plate_search()
    rows = run(
        lambda s: [_customer_data(c) for c in customers.search_customers(s, text)]
    )
    if not rows:
        st.caption("Kayıt bulunamadı.")
        return
    with st.container(border=True):
        _customer_table(rows)
    row = _select_customer(rows)
    left, right = st.columns(2)
    with left.container(border=True):
        st.markdown("**:material/edit: Müşteri bilgileri**")
        _edit_form(row)
    with right.container(border=True):
        st.markdown("**:material/directions_car: Araçlar**")
        _vehicle_table(row)
        _vehicle_form(row)


def _customer_table(rows: list[dict]) -> None:
    st.dataframe(
        [
            {
                "Ad soyad": r["name"],
                "Telefon": r["phone"] or "",
                "Araç": len(r["vehicles"]),
            }
            for r in rows
        ],
        hide_index=True,
        use_container_width=True,
    )


def _select_customer(rows: list[dict]) -> dict:
    by_id = {r["id"]: r for r in rows}
    selected = st.selectbox(
        "Müşteri seç",
        list(by_id),
        format_func=lambda i: f"{by_id[i]['name']} ({by_id[i]['phone'] or '-'})",
        key="musteri_sec",
    )
    return by_id[selected]


def _vehicle_table(row: dict) -> None:
    if not row["vehicles"]:
        st.caption("Bu müşterinin kayıtlı aracı yok.")
        return
    st.dataframe(
        [
            {
                "Plaka": vehicles.format_plate(v["plate"]),
                "Marka": v["brand"],
                "Model": v["model"],
            }
            for v in row["vehicles"]
        ],
        hide_index=True,
    )
