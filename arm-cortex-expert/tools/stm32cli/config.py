import os
from pathlib import Path

DEFAULT_DB_PATH = os.path.join(os.path.expanduser("~"), ".stm32cubemx", "databases")
CACHE_DIR = Path.home() / ".stm32cli_cache"
CACHE_TTL = 3600  # 1 hour

def get_db_path(custom_path=None):
    if custom_path:
        return custom_path
    if "STM32CUBEMX_DB_PATH" in os.environ:
        return os.environ["STM32CUBEMX_DB_PATH"]
    return DEFAULT_DB_PATH

def _version_key(name):
    """'DB.6.10' -> (6, 10)。数字段比较，避免字符串排序把 6.9 排在 6.10 之后。"""
    parts = []
    for p in name.replace("DB.", "", 1).split("."):
        try:
            parts.append(int(p))
        except ValueError:
            pass
    return tuple(parts)

def get_latest_db_version(db_path):
    db_path = Path(db_path)
    if not db_path.exists():
        return None
    versions = []
    for d in db_path.iterdir():
        if d.is_dir() and d.name.startswith("DB."):
            v = _version_key(d.name)
            if v:
                versions.append((v, d))
    if not versions:
        return None
    versions.sort(key=lambda x: x[0], reverse=True)
    return versions[0][1]

def get_db_signature(db_path=None):
    """解析数据库目录并返回 (db_dir, signature)。

    signature 含数据库绝对路径与 families.xml 修改时间，
    保证切换数据库或数据库更新后缓存自动失效。
    返回 (None, None) 表示数据库不可用。
    """
    root = Path(get_db_path(db_path))
    if not root.exists():
        return None, None
    db_dir = get_latest_db_version(root)
    if db_dir is None:
        return None, None
    fam = db_dir / "db" / "mcu" / "families.xml"
    try:
        mtime = int(fam.stat().st_mtime)
    except OSError:
        mtime = 0
    return db_dir, f"{db_dir}|{mtime}"

def get_mcu_xml_path(db_dir, mcu_name):
    mcu_dir = db_dir / "db" / "mcu"
    xml_file = mcu_dir / f"{mcu_name}.xml"
    if xml_file.exists():
        return xml_file
    return None

def get_ip_dir(db_dir):
    return db_dir / "db" / "mcu" / "IP"

def get_families_xml(db_dir):
    return db_dir / "db" / "mcu" / "families.xml"
