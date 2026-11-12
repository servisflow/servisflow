"""UC-04, UC-05 ve UC-06 ekranı: servis ziyareti, iş listesi ve ✓ tamamlama.

Akış: plaka girilir → araç bulunur → ziyaret açılır → işler eklenir → ✓ ile
tamamlanır. Tamamlanan iş düzenlenemez ve silinemez (BR-02); ✓ yalnızca aynı
İstanbul günü içinde geri alınır (BR-04). Kuralların hepsi servis katmanında.
"""

import streamlit as st

from servisflow.services import completion, tasks, vehicles, visits
from servisflow.services.clock import ISTANBUL, SystemClock
from servisflow.services.reports import vehicle_history
from servisflow.ui.common import (
    act,
    amount_from_input,
    run,
    show_flash,
    tl,
)

DONE = "DONE"


def _when(moment) -> str:
    return f"{moment.astimezone(ISTANBUL):%d.%m.%Y %H:%M}"


def _vehicle_labels(session) -> dict[int, str]:
    return {
        v.id: f"{vehicles.format_plate(v.plate_normalized)} · {v.brand} {v.model}"
        f" · {v.customer.full_name}"
        for v in vehicles.list_vehicles(session)
    }


def _history(session, vehicle_id: int) -> list[dict]:
    """Ziyaretler ve işleri, oturum kapanmadan düz veriye çevrilir."""
    result = []
    for visit in vehicle_history(session, vehicle_id):
        open_total, done_total = tasks.visit_totals(session, visit.id)
        result.append(
            {
                "id": visit.id,
                "opened": _when(visit.opened_at),
                "complaint": visit.complaint,
                "open_total": open_total,
                "done_total": done_total,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "note": t.note,
                        "amount": t.amount_kurus,
                        "done": t.status == DONE,
                        "completed": _when(t.completed_at) if t.completed_at else "",
                    }
                    for t in visit.tasks
                ],
            }
        )
    return result


def _new_visit_form(vehicle_id: int) -> None:
    with st.form("yeni_ziyaret", clear_on_submit=True):
        complaint = st.text_area("Şikâyet / açıklama (isteğe bağlı)", key="sikayet")
        if st.form_submit_button("Yeni servis ziyareti aç"):
            act(
                lambda s: visits.open_visit(s, SystemClock(), vehicle_id, complaint),
                "Ziyaret açıldı; tarih ve saat sistemce atandı.",
            )


def _task_row(task: dict) -> None:
    mark, title, amount, button = st.columns([1, 6, 3, 3])
    mark.markdown("✅" if task["done"] else "☐")
    title.markdown(
        f"**{task['title']}**" + (f"  \n{task['note']}" if task["note"] else "")
    )
    amount.markdown(tl(task["amount"]))
    if task["done"]:
        button.caption(task["completed"])
        if button.button("Geri al", key=f"geri_{task['id']}"):
            act(
                lambda s: completion.undo_completion(s, SystemClock(), task["id"]),
                "✓ geri alındı.",
            )
        return
    if button.button("✓ Tamamla", key=f"tik_{task['id']}"):
        act(
            lambda s: completion.complete_task(s, SystemClock(), task["id"]),
            "İş tamamlandı.",
        )
    with st.expander(f"Düzenle / sil: {task['title']}"):
        _edit_task_form(task)


def _edit_task_form(task: dict) -> None:
    tid = task["id"]
    with st.form(f"duzenle_is_{tid}"):
        title = st.text_input("Başlık", value=task["title"], key=f"is_baslik_{tid}")
        amount = st.number_input(
            "Tutar (TL)",
            min_value=0,
            value=task["amount"] // 100,
            step=1,
            key=f"is_tutar_{tid}",
        )
        note = st.text_input("Not", value=task["note"] or "", key=f"is_not_{tid}")
        if st.form_submit_button("Güncelle"):
            act(
                lambda s: tasks.update_task(
                    s, tid, title, amount_from_input(amount), note
                ),
                "İş güncellendi.",
            )
    if st.button("İşi sil", key=f"sil_{tid}"):
        act(lambda s: tasks.delete_task(s, tid), "İş silindi.")


def _new_task_form(visit_id: int) -> None:
    with st.form(f"yeni_is_{visit_id}", clear_on_submit=True):
        st.markdown("**İş ekle**")
        title = st.text_input("Başlık", key=f"yeni_is_baslik_{visit_id}")
        amount = st.number_input(
            "Tutar (TL)",
            min_value=0,
            step=1,
            key=f"yeni_is_tutar_{visit_id}",
        )
        note = st.text_input("Not (isteğe bağlı)", key=f"yeni_is_not_{visit_id}")
        if st.form_submit_button("İşi ekle"):
            act(
                lambda s: tasks.add_task(
                    s, SystemClock(), visit_id, title, amount_from_input(amount), note
                ),
                "İş eklendi.",
            )


def _visit_block(visit: dict, latest: bool) -> None:
    with st.container(border=True):
        st.markdown(f"#### Ziyaret · {visit['opened']}")
        if visit["complaint"]:
            st.caption(visit["complaint"])
        st.markdown(
            f"Açık işler: **{tl(visit['open_total'])}** · "
            f"Tamamlanan: **{tl(visit['done_total'])}**"
        )
        for task in visit["tasks"]:
            _task_row(task)
        if latest:
            _new_task_form(visit["id"])


def render() -> None:
    st.header("Servis ve işler")
    show_flash()
    labels = run(_vehicle_labels) or {}
    # Liste yazdıkça tarayıcıda süzülür; "prefix" kipi etiketin başına bakar.
    # Etiket boşluklu plakayla başladığı için "06 b" yazınca 06 BA… ve 06 BUM…
    # önerilir. Seçim yapılana kadar hiçbir araç açılmaz (KR-09).
    vehicle_id = st.selectbox(
        "Araç plakası",
        list(labels),
        index=None,
        format_func=labels.get,
        placeholder="Plakayı boşluklu yazın (ör. 06 b) ve listeden seçin",
        filter_mode="prefix",
        key="ziyaret_arac",
    )
    if vehicle_id is None:
        st.caption("Araç Müşteriler ve araçlar ekranından eklenir.")
        return
    st.subheader(labels[vehicle_id])
    _new_visit_form(vehicle_id)
    history = run(lambda s: _history(s, vehicle_id)) or []
    if not history:
        st.caption("Bu araç için henüz ziyaret yok.")
    for index, visit in enumerate(history):
        _visit_block(visit, latest=index == 0)
