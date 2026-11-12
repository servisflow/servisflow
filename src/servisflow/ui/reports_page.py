"""UC-07 ekranı: dönemsel brüt iş bedeli (FR-08, BR-05, BR-06).

Toplam, seçilen dönemde ✓ ile tamamlanan işlerin tutarlarıdır; açık işler
sayılmaz. Dönem sınırları İstanbul takvimine göredir. Bu tutar tahsilat veya
kâr değildir.
"""

from datetime import datetime, timedelta

import streamlit as st

from servisflow.services import reports
from servisflow.services.clock import ISTANBUL
from servisflow.ui.common import run, tl

PERIOD_LABELS = {
    reports.PERIOD_DAY: "Günlük",
    reports.PERIOD_WEEK: "Haftalık",
    reports.PERIOD_MONTH: "Aylık",
    reports.PERIOD_YEAR: "Yıllık",
}


def _report(session, kind: str, day) -> dict:
    start, end = reports.period_bounds(kind, day)
    return {
        "total": reports.gross_total(session, start, end),
        "first": start.astimezone(ISTANBUL).date(),
        # Sorgu [start, end) yarı açık; kullanıcıya dönemin son günü gösterilir.
        "last": (end.astimezone(ISTANBUL) - timedelta(days=1)).date(),
        "rows": [
            {
                "Tamamlanma": f"{t.completed_at.astimezone(ISTANBUL):%d.%m.%Y %H:%M}",
                "Plaka": t.visit.vehicle.plate_normalized,
                "İş": t.title,
                "Tutar": tl(t.amount_kurus),
            }
            for t in reports.completed_tasks(session, start, end)
        ],
    }


def render() -> None:
    st.header("Dönemsel brüt iş bedeli")
    kind = st.radio(
        "Dönem",
        list(PERIOD_LABELS),
        format_func=PERIOD_LABELS.get,
        horizontal=True,
        key="donem",
    )
    day = st.date_input(
        "Dönemi içeren gün",
        value=datetime.now(ISTANBUL).date(),
        format="DD.MM.YYYY",
        key="donem_gunu",
    )
    report = run(lambda s: _report(s, kind, day))
    if report is None:
        return
    st.metric(
        f"{PERIOD_LABELS[kind]} toplam "
        f"({report['first']:%d.%m.%Y} – {report['last']:%d.%m.%Y})",
        tl(report["total"]),
    )
    st.caption("Yalnızca ✓ ile tamamlanan işler sayılır; tahsilat veya kâr değildir.")
    if report["rows"]:
        st.dataframe(report["rows"], hide_index=True)
    else:
        st.caption("Bu dönemde tamamlanan iş yok.")
