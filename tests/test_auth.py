"""UC-01 testleri: giriş, CAPTCHA, hatalı deneme listesi.

TC-01, TC-02, TC-04, TC-05, TC-32.
"""

from datetime import timedelta

import pytest
from argon2 import PasswordHasher

from servisflow import create_owner as setup_script
from servisflow.repository.models import LoginAttempt, User
from servisflow.services import auth
from servisflow.services.errors import (
    AuthenticationError,
    ConflictError,
    ValidationError,
)

PAROLA = "dogru-parola-123"


@pytest.fixture
def owner(session):
    return auth.create_owner(session, "sorumlu", PAROLA)


def _fail(session, clock, username="sorumlu", password="yanlis", captcha=False):
    with pytest.raises(AuthenticationError) as info:
        auth.authenticate(session, clock, username, password, captcha)
    clock.advance(timedelta(minutes=1))
    return str(info.value)


# --- Hesap oluşturma ---------------------------------------------------------


def test_tc02_parola_argon2id_ile_ozetlenir(session, owner):
    row = session.get(User, owner.id)
    assert row.password_hash.startswith("$argon2id$")
    assert PAROLA not in row.password_hash


def test_ikinci_hesap_olusturulamaz(session, owner):
    with pytest.raises(ConflictError):
        auth.create_owner(session, "ikinci", PAROLA)


@pytest.mark.parametrize(
    "username, password",
    [("", PAROLA), ("x" * 51, PAROLA), ("sorumlu", "kisa123"), ("sorumlu", "x" * 129)],
)
def test_gecersiz_hesap_bilgisi(session, username, password):
    with pytest.raises(ValidationError):
        auth.create_owner(session, username, password)


# --- Giriş -------------------------------------------------------------------


def test_dogru_giris(session, clock, owner):
    user = auth.authenticate(session, clock, " sorumlu ", PAROLA, False)
    assert user.id == owner.id
    assert user.last_login_at == clock.now()


def test_tc01_tc05_yanlis_parola_ve_olmayan_ad_ayni_mesaj(session, clock, owner):
    assert (
        _fail(session, clock) == _fail(session, clock, "olmayan") == auth.LOGIN_FAILED
    )


@pytest.mark.parametrize(
    "username, password", [("", ""), ("sorumlu", ""), ("", PAROLA)]
)
def test_bos_alanlar_reddedilir(session, clock, owner, username, password):
    assert _fail(session, clock, username, password) == auth.LOGIN_FAILED


def test_her_deneme_kaydedilir(session, clock, owner):
    _fail(session, clock)
    auth.authenticate(session, clock, "sorumlu", PAROLA, False)
    assert [
        a.success for a in session.query(LoginAttempt).order_by(LoginAttempt.id)
    ] == [
        False,
        True,
    ]


def test_cok_uzun_kullanici_adi_kirpilarak_kaydedilir(session, clock, owner):
    """R-11: saldırganın gönderdiği 10.000 karakterlik ad tabloyu şişirmez."""
    _fail(session, clock, "a" * 10_000)
    assert len(session.query(LoginAttempt).one().username) == auth.USERNAME_MAX


def test_eski_parametreli_ozet_giriste_yenilenir(session, clock):
    weak = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash(PAROLA)
    session.add(User(username="sorumlu", password_hash=weak))
    session.flush()
    user = auth.authenticate(session, clock, "sorumlu", PAROLA, False)
    assert user.password_hash != weak
    assert not PasswordHasher().check_needs_rehash(user.password_hash)


def test_bozuk_ozet_girisi_reddeder(session, clock):
    session.add(User(username="sorumlu", password_hash="bozuk"))
    session.flush()
    assert _fail(session, clock, password=PAROLA) == auth.LOGIN_FAILED


# --- CAPTCHA: TC-04 ----------------------------------------------------------


def test_tc04_iki_hatadan_sonra_captcha_yok_ucten_sonra_var(session, clock, owner):
    _fail(session, clock)
    _fail(session, clock)
    assert not auth.captcha_required(session, "sorumlu")
    _fail(session, clock)
    assert auth.captcha_required(session, "sorumlu")


def test_tc04_captcha_yanlissa_dogru_parola_da_reddedilir(session, clock, owner):
    for _ in range(3):
        _fail(session, clock)
    assert _fail(session, clock, password=PAROLA) == auth.CAPTCHA_FAILED
    user = auth.authenticate(session, clock, "sorumlu", PAROLA, True)
    assert user.id == owner.id
    assert not auth.captcha_required(session, "sorumlu")


def test_captcha_olmayan_ad_icin_de_ayni_davranir(session, clock, owner):
    """KR-03, R-02: CAPTCHA'nın çıkması adın var olup olmadığını sızdırmaz."""
    for name in ("sorumlu", "olmayan"):
        for _ in range(3):
            _fail(session, clock, name)
    assert auth.captcha_required(session, "sorumlu")
    assert auth.captcha_required(session, "olmayan")


# --- Hatalı deneme listesi: TC-32 --------------------------------------------


def test_tc32_hatali_denemeler_ilk_giriste_listelenir_sonra_bos(session, clock, owner):
    times = []
    for _ in range(3):
        times.append(clock.now())
        _fail(session, clock)
    auth.authenticate(session, clock, "sorumlu", PAROLA, True)
    assert auth.failed_attempts_since_last_login(session, "sorumlu") == times

    clock.advance(timedelta(hours=1))
    auth.authenticate(session, clock, "sorumlu", PAROLA, False)
    assert auth.failed_attempts_since_last_login(session, "sorumlu") == []


def test_hic_giris_yoksa_liste_bos(session):
    assert auth.failed_attempts_since_last_login(session, "sorumlu") == []


# --- CAPTCHA üretimi ---------------------------------------------------------


def test_captcha_sorusu_ve_cevabi():
    question, answer = auth.new_captcha()
    a, b = (int(x) for x in question.split(" kaç")[0].split(" + "))
    assert a + b == answer
    assert auth.check_captcha(answer, f" {answer} ")
    assert not auth.check_captcha(answer, str(answer + 1))
    assert not auth.check_captcha(answer, "abc")
    assert not auth.check_captcha(answer, None)


# --- Kurulum betiği ----------------------------------------------------------


def _run(tmp_path, answers, passwords):
    url = f"sqlite:///{tmp_path / 'kurulum.db'}"
    pw = iter(passwords)
    return setup_script.main(lambda _: answers, lambda _: next(pw), url)


def test_kurulum_betigi_hesap_olusturur(tmp_path, capsys):
    assert _run(tmp_path, "sorumlu", [PAROLA, PAROLA]) == 0
    assert "oluşturuldu" in capsys.readouterr().out
    assert _run(tmp_path, "ikinci", [PAROLA, PAROLA]) == 1  # tek hesap
    assert "zaten var" in capsys.readouterr().err


def test_kurulum_betigi_parola_eslesmezse_durur(tmp_path, capsys):
    assert _run(tmp_path, "sorumlu", [PAROLA, "baska"]) == 1
    assert "eşleşmiyor" in capsys.readouterr().err


def test_olmayan_kullanici_sahte_ozetle_eslesen_parolayla_da_giremez(
    session, clock, owner, monkeypatch
):
    """Zamanlama için kullanılan sahte özet tutsa bile kullanıcı yoksa giriş olmaz.

    Mutasyon testiyle bulundu: `user is not None` koruması hiçbir testte sınanmıyordu.
    """
    fake = PasswordHasher().hash("sahte-ozet-parolasi")
    monkeypatch.setattr(auth, "_dummy_hash", lambda: fake)
    assert _fail(session, clock, "olmayan", "sahte-ozet-parolasi") == auth.LOGIN_FAILED


def test_tc32_giristen_sonraki_hatalar_bu_girisin_listesine_karismaz(
    session, clock, owner
):
    """Liste, önceki ve son başarılı giriş arasıyla sınırlıdır (mutasyonla bulundu)."""
    before = clock.now()
    _fail(session, clock)
    auth.authenticate(session, clock, "sorumlu", PAROLA, False)
    clock.advance(timedelta(minutes=5))
    _fail(session, clock)  # oturum açıkken başkasının denemesi
    assert auth.failed_attempts_since_last_login(session, "sorumlu") == [before]
