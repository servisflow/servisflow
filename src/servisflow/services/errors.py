"""Servis katmanının hata türleri; mesajları kullanıcıya gösterilebilir."""


class ServisFlowError(Exception):
    """Tüm iş kuralı hatalarının tabanı."""


class ValidationError(ServisFlowError):
    """Girdi bir iş kuralını ihlal ediyor (ör. BR-01 tutar aralığı)."""


class NotFoundError(ServisFlowError):
    """İstenen kayıt yok."""


class ConflictError(ServisFlowError):
    """İstek mevcut durumla çelişiyor (ör. aynı plaka, DONE işi düzenleme)."""
