import json
import time
from pathlib import Path
import hashlib

class Cache:
    def __init__(self, cache_dir=None, ttl=3600):
        if cache_dir is None:
            from config import CACHE_DIR
            cache_dir = CACHE_DIR
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.memory_cache = {}
        self._ensure_dir()

    def _ensure_dir(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "chips").mkdir(exist_ok=True)
        (self.cache_dir / "peripherals").mkdir(exist_ok=True)

    def _make_key(self, *args):
        key_str = "_".join(str(a) for a in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, *args):
        key = self._make_key(*args)
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry["time"] < self.ttl:
                return entry["data"]
            del self.memory_cache[key]
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                if time.time() - data.get("time", 0) < self.ttl:
                    self.memory_cache[key] = data
                    return data["data"]
                cache_file.unlink()
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink()
        return None

    def set(self, *args, data=None):
        if data is None:
            if len(args) < 2:
                return
            data = args[-1]
            args = args[:-1]
        key = self._make_key(*args)
        entry = {"time": time.time(), "data": data}
        self.memory_cache[key] = entry
        cache_file = self.cache_dir / f"{key}.json"
        try:
            cache_file.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def clear(self):
        self.memory_cache.clear()
        for f in self.cache_dir.glob("*.json"):
            try:
                f.unlink()
            except Exception:
                pass

    def get_chip_path(self, mcu_name):
        return self.cache_dir / "chips" / f"{mcu_name}.json"

    def get_peripheral_path(self, mcu_name, peripheral):
        return self.cache_dir / "peripherals" / f"{mcu_name}_{peripheral}.json"
