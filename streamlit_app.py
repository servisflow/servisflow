"""Streamlit Community Cloud giriş noktası (Faz 4 - iv, devreye alma).

Bulut, depoyu paket olarak kurmaz (`pip install -e .` çalışmaz); bu yüzden
`src` klasörü içe aktarma yoluna eklenir ve asıl uygulama çalıştırılır.
Yerelde yine `streamlit run src/servisflow/ui/app.py` kullanılabilir.
"""

import runpy
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

runpy.run_path(str(SRC / "servisflow" / "ui" / "app.py"), run_name="__main__")
