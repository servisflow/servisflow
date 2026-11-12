"""UC-02 ve UC-03 ekranı: müşteri kaydı, arama, güncelleme ve araç ekleme."""

import streamlit as st

from servisflow.services import customers, vehicles
from servisflow.services.clock import SystemClock
from servisflow.ui.common import run


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
    with st.expander("Yeni müşteri"):
        with st.form("yeni_musteri"):
            name = st.text_input("Ad soyad", key="yeni_ad")
            phone = st.text_input("Telefon (isteğe bağlı)", key="yeni_tel")
            if st.form_submit_button("Kaydet"):
                run(
                    lambda s: customers.create_customer(s, SystemClock(), name, phone),
                    "Müşteri kaydedildi.",
                )


def _plate_search() -> None:
    plate = st.text_input("Plakayla araç bul", key="plaka_ara")
    if not plate.strip():
        return

    def find(session):
        v = vehicles.find_vehicle_by_plate(session, plate)
        return f"{v.plate_normalized} · {v.brand} {v.model} · {v.customer.full_name}"

    found = run(find)
    if found:
        st.info(found)


def _edit_form(row: dict) -> None:
    with st.form(f"duzenle_{row['id']}"):
        name = st.text_input("Ad soyad", value=row["name"], key="duz_ad")
        phone = st.text_input("Telefon", value=row["phone"] or "", key="duz_tel")
        if st.form_submit_button("Güncelle"):
            run(
                lambda s: customers.update_customer(s, row["id"], name, phone),
                "Müşteri güncellendi.",
            )


def _vehicle_form(row: dict) -> None:
    with st.form(f"arac_{row['id']}"):
        st.markdown("**Araç ekle**")
        plate = st.text_input("Plaka", key="arac_plaka")
        brand = st.text_input("Marka", key="arac_marka")
        model = st.text_input("Model", key="arac_model")
        if st.form_submit_button("Aracı kaydet"):
            run(
                lambda s: vehicles.register_vehicle(s, row["id"], plate, brand, model),
                "Araç kaydedildi.",
            )


def render() -> None:
    st.header("Müşteriler ve araçlar")
    _new_customer_form()
    _plate_search()
    st.divider()

    text = st.text_input("Müşteri ara (ad veya telefon)", key="musteri_ara")
    rows = run(
        lambda s: [_customer_data(c) for c in customers.search_customers(s, text)]
    )
    if not rows:
        st.caption("Kayıt bulunamadı.")
        return
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
    )
    by_id = {r["id"]: r for r in rows}
    selected = st.selectbox(
        "Müşteri seç",
        list(by_id),
        format_func=lambda i: f"{by_id[i]['name']} ({by_id[i]['phone'] or '-'})",
        key="musteri_sec",
    )
    row = by_id[selected]
    _edit_form(row)
    if row["vehicles"]:
        st.dataframe(
            [
                {"Plaka": v["plate"], "Marka": v["brand"], "Model": v["model"]}
                for v in row["vehicles"]
            ],
            hide_index=True,
        )
    else:
        st.caption("Bu müşterinin kayıtlı aracı yok.")
    _vehicle_form(row)
