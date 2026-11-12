"""UC-05 testleri: iş ekleme, düzenleme, silme ve tutar dönüşümü (TC-15 – TC-17)."""

from datetime import timedelta
from decimal import Decimal

import pytest

from servisflow.repository.models import (
    TASK_DONE,
    TASK_TODO,
    Customer,
    ServiceTask,
    ServiceVisit,
    Vehicle,
)
from servisflow.services import tasks
from servisflow.services.errors import ConflictError, NotFoundError, ValidationError


@pytest.fixture
def visit(session, clock):
    customer = Customer(full_name="Can GPT", created_at=clock.now())
    vehicle = Vehicle(
        customer=customer, plate_normalized="34BJK321", brand="Isuzu", model="10 Long"
    )
    visit = ServiceVisit(vehicle=vehicle, opened_at=clock.now())
    session.add(visit)
    session.flush()
    return visit


def _mark_done(session, task, clock):
    """UC-06 henüz yok; işi doğrudan DONE yapar."""
    task.status = TASK_DONE
    task.completed_at = clock.now()
    session.flush()


# --- to_kurus: BR-01 ---------------------------------------------------------


@pytest.mark.parametrize(
    "amount, kurus",
    [
        (Decimal("0.01"), 1),  # TC-15 alt sınır
        (Decimal("1000000.00"), 100_000_000),  # TC-15 üst sınır
        (Decimal("1600.50"), 160_050),  # TC-16
        (Decimal("1600.5"), 160_050),
        (Decimal("1200"), 120_000),
        (1200, 120_000),  # tam TL
    ],
)
def test_gecerli_tutar_kurusa_cevrilir(amount, kurus):
    assert tasks.to_kurus(amount) == kurus


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0"),  # TC-15
        Decimal("0.00"),
        Decimal("-5"),
        Decimal("1000000.01"),  # TC-15
        Decimal("10.005"),  # TC-16: ikiden fazla ondalık
        Decimal("NaN"),
        Decimal("Infinity"),
    ],
)
def test_gecersiz_tutar_reddedilir(amount):
    with pytest.raises(ValidationError):
        tasks.to_kurus(amount)


# 1.5 ikili sistemde tam saklanır; yalnızca 1.15 ile test, float yasağını değil
# ondalık kontrolünü sınardı (mutasyon testiyle bulundu).
@pytest.mark.parametrize("amount", [1.5, 1.15, "1600,50", "abc", True, None])
def test_decimal_olmayan_tutar_reddedilir(amount):
    """float yuvarlama hatası taşır, metin ayrıştırılmaz (RV-05), bool sayı değildir."""
    with pytest.raises(ValidationError):
        tasks.to_kurus(amount)


def test_float_tuzagi_decimal_strden_kurulmali():
    """1.15 float olarak 1.149999... saklanır; Decimal(float) bu hatayı taşır."""
    with pytest.raises(ValidationError):
        tasks.to_kurus(Decimal(1.15))
    assert tasks.to_kurus(Decimal(str(1.15))) == 115


# --- add_task: FR-05 ---------------------------------------------------------


def test_is_eklenir_todo_ve_saat_saglayicidan_zaman_alir(session, clock, visit):
    task = tasks.add_task(
        session, clock, visit.id, "  Ön sol teker ", Decimal("1600"), "Bilya, keçe"
    )
    assert task.id is not None
    assert task.title == "Ön sol teker"
    assert task.note == "Bilya, keçe"
    assert task.amount_kurus == 160_000
    assert task.status == TASK_TODO
    assert task.completed_at is None
    assert task.created_at == clock.now()


def test_ziyarete_birden_fazla_is_eklenir(session, clock, visit):
    tasks.add_task(session, clock, visit.id, "Ön sol teker", Decimal("1600"))
    tasks.add_task(session, clock, visit.id, "Yağ değişimi", Decimal("1200"))
    session.refresh(visit)
    assert [t.title for t in visit.tasks] == ["Ön sol teker", "Yağ değişimi"]


@pytest.mark.parametrize("note", [None, "", "   \n"])
def test_bos_not_none_olarak_saklanir(session, clock, visit, note):
    task = tasks.add_task(session, clock, visit.id, "Yağ", Decimal("1"), note)
    assert task.note is None


@pytest.mark.parametrize("title", ["", "   ", "\t\n", "x" * 101])
def test_gecersiz_baslik_reddedilir(session, clock, visit, title):
    """\\t ve \\n SQLite trim() kısıtından geçer; servis str.strip() ile yakalar."""
    with pytest.raises(ValidationError):
        tasks.add_task(session, clock, visit.id, title, Decimal("1"))


def test_baslik_siniri_100_karakter(session, clock, visit):
    task = tasks.add_task(session, clock, visit.id, "x" * 100, Decimal("1"))
    assert len(task.title) == 100


def test_uzun_not_reddedilir(session, clock, visit):
    with pytest.raises(ValidationError):
        tasks.add_task(session, clock, visit.id, "Yağ", Decimal("1"), "x" * 501)


def test_olmayan_ziyarete_is_eklenemez(session, clock):
    with pytest.raises(NotFoundError):
        tasks.add_task(session, clock, 999, "Yağ", Decimal("1"))


def test_gecersiz_tutarla_hicbir_sey_eklenmez(session, clock, visit):
    with pytest.raises(ValidationError):
        tasks.add_task(session, clock, visit.id, "Yağ", Decimal("0"))
    assert session.query(ServiceTask).count() == 0


# --- update_task / delete_task: BR-02, BR-08 --------------------------------


def test_todo_is_duzenlenir(session, clock, visit):
    task = tasks.add_task(session, clock, visit.id, "Yağ", Decimal("1200"))
    clock.advance(timedelta(hours=1))
    updated = tasks.update_task(
        session, task.id, "Yağ + filtre", Decimal("1350.50"), ""
    )
    assert (updated.title, updated.amount_kurus, updated.note) == (
        "Yağ + filtre",
        135_050,
        None,
    )
    assert updated.created_at != clock.now()  # düzenleme oluşturma zamanını değiştirmez


def test_done_is_duzenlenemez(session, clock, visit):
    """TC-17: tamamlanan işin tutarı ve başlığı kilitlidir (BR-02)."""
    task = tasks.add_task(session, clock, visit.id, "Yağ", Decimal("1200"))
    _mark_done(session, task, clock)
    with pytest.raises(ConflictError):
        tasks.update_task(session, task.id, "Yağ", Decimal("9999"), None)
    session.refresh(task)
    assert task.amount_kurus == 120_000


def test_gecersiz_duzenleme_isi_degistirmez(session, clock, visit):
    task = tasks.add_task(session, clock, visit.id, "Yağ", Decimal("1200"))
    with pytest.raises(ValidationError):
        tasks.update_task(session, task.id, "", Decimal("1300"), None)
    session.refresh(task)
    assert (task.title, task.amount_kurus) == ("Yağ", 120_000)


def test_olmayan_is_duzenlenemez(session):
    with pytest.raises(NotFoundError):
        tasks.update_task(session, 999, "Yağ", Decimal("1"), None)


def test_todo_is_silinir(session, clock, visit):
    task = tasks.add_task(session, clock, visit.id, "Yağ", Decimal("1200"))
    tasks.delete_task(session, task.id)
    assert session.get(ServiceTask, task.id) is None


def test_done_is_silinemez(session, clock, visit):
    """TC-17 ve BR-08: yalnızca TODO iş silinebilir."""
    task = tasks.add_task(session, clock, visit.id, "Yağ", Decimal("1200"))
    _mark_done(session, task, clock)
    with pytest.raises(ConflictError):
        tasks.delete_task(session, task.id)
    assert session.get(ServiceTask, task.id) is not None


def test_olmayan_is_silinemez(session):
    with pytest.raises(NotFoundError):
        tasks.delete_task(session, 999)


# --- visit_totals: UC-05 ana akış, “açık ve tamamlanmış toplamlar” -----------


def test_ziyaret_toplamlari_acik_ve_tamamlanan_ayri(session, clock, visit):
    teker = tasks.add_task(session, clock, visit.id, "Ön sol teker", Decimal("1600"))
    tasks.add_task(session, clock, visit.id, "Yağ değişimi", Decimal("1200"))
    _mark_done(session, teker, clock)
    assert tasks.visit_totals(session, visit.id) == (120_000, 160_000)


def test_bos_ziyaretin_toplamlari_sifir(session, visit):
    assert tasks.visit_totals(session, visit.id) == (0, 0)


def test_olmayan_ziyaretin_toplamlari_istenemez(session):
    with pytest.raises(NotFoundError):
        tasks.visit_totals(session, 999)
