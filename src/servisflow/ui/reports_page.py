"""UC-07 ekranı: dönemsel brüt iş bedeli (FR-08, BR-05, BR-06).

Toplam, seçilen dönemde ✓ ile tamamlanan işlerin tutarlarıdır; açık işler
sayılmaz. Dönem sınırları İstanbul takvimine göredir. Bu tutar tahsilat veya
kâr değildir.
"""

from datetime import datetime, timedelta

import streamlit as st

from servisflow.services import reports, vehicles
from servisflow.services.clock import ISTANBUL
from servisflow.ui.common import page_header, run, tl

PERIOD_LABELS = {
    reports.PERIOD_DAY: "Günlük",
    reports.PERIOD_WEEK: "Haftalık",
    reports.PERIOD_MONTH: "Aylık",
    reports.PERIOD_YEAR: "Yıllık",
}


def _chart_rows(tasks, kind: str) -> list[dict]:
    """Grafik için tamamlanan işler güne (yıllıkta aya) göre toplanır."""
    pattern = "%m.%Y" if kind == reports.PERIOD_YEAR else "%d.%m"
    sums: dict[str, int] = {}
    for t in tasks:
        label = f"{t.completed_at.astimezone(ISTANBUL):{pattern}}"
        sums[label] = sums.get(label, 0) + t.amount_kurus // 100
    return [{"Dönem": k, "TL": v} for k, v in sums.items()]


def _report(session, kind: str, day) -> dict:
    start, end = reports.period_bounds(kind, day)
    done = reports.completed_tasks(session, start, end)
    return {
        "total": reports.gross_total(session, start, end),
        "first": start.astimezone(ISTANBUL).date(),
        # Sorgu [start, end) yarı açık; kullanıcıya dönemin son günü gösterilir.
        "last": (end.astimezone(ISTANBUL) - timedelta(days=1)).date(),
        "rows": [
            {
                "Tamamlanma": f"{t.completed_at.astimezone(ISTANBUL):%d.%m.%Y %H:%M}",
                "Plaka": vehicles.format_plate(t.visit.vehicle.plate_normalized),
                "İş": t.title,
                "Tutar": tl(t.amount_kurus),
            }
            for t in done
        ],
        "chart": _chart_rows(done, kind),
    }


def render() -> None:
    page_header(
        "Dönemsel brüt iş bedeli",
        "Yalnızca ✓ ile tamamlanan işler sayılır; tahsilat veya kâr değildir.",
    )
    with st.container(border=True):
        left, right = st.columns([2, 1])
        kind = left.radio(
            "Dönem",
            list(PERIOD_LABELS),
            format_func=PERIOD_LABELS.get,
            horizontal=True,
            key="donem",
        )
        day = right.date_input(
            "Dönemi içeren gün",
            value=datetime.now(ISTANBUL).date(),
            format="DD.MM.YYYY",
            key="donem_gunu",
        )
    report = run(lambda s: _report(s, kind, day))
    if report is None:
        return
    with st.container(border=True):
        st.metric(
            f"{PERIOD_LABELS[kind]} toplam "
            f"({report['first']:%d.%m.%Y} – {report['last']:%d.%m.%Y})",
            tl(report["total"]),
        )
        if report["rows"] and kind != reports.PERIOD_DAY:
            st.bar_chart(
                report["chart"], x="Dönem", y="TL", color="#C2410C", height=220
            )
    if report["rows"]:
        st.dataframe(report["rows"], hide_index=True, use_container_width=True)
    else:
        st.caption("Bu dönemde tamamlanan iş yok.")
