"""İşletme sorumlusu hesabını oluşturan kurulum betiği (FR-01).

Kullanım (repo kökünden): python -m servisflow.create_owner
Parola ekrana yazılmaz ve iki kez sorulur.
"""

import getpass
import sys

from servisflow.repository.db import init_db, make_engine, make_session_factory
from servisflow.services.auth import create_owner
from servisflow.services.errors import ServisFlowError


def main(input_fn=input, getpass_fn=getpass.getpass, url: str | None = None) -> int:
    username = input_fn("Kullanıcı adı: ")
    password = getpass_fn("Parola: ")
    if password != getpass_fn("Parola (tekrar): "):
        print("Parolalar eşleşmiyor.", file=sys.stderr)
        return 1
    engine = make_engine(url)
    init_db(engine)
    try:
        with make_session_factory(engine).begin() as session:
            create_owner(session, username, password)
    except ServisFlowError as exc:
        print(exc, file=sys.stderr)
        return 1
    finally:
        engine.dispose()
    print("Hesap oluşturuldu.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
