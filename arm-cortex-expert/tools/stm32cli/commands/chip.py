import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_db_signature, get_db_path, get_latest_db_version, get_mcu_xml_path, get_families_xml
from parsers.families import FamiliesParser
from parsers.mcu import McuParser
from cache import Cache

def handle_chip(mcu_name, db_path=None, cache=None):
    if cache is None:
        cache = Cache()
    db_dir, dbsig = get_db_signature(db_path)
    if db_dir is None:
        return {"status": "error", "error": {"code": "DB_NOT_FOUND", "message": "CubeMX database not found"}}
    cached = cache.get("chip", dbsig, mcu_name)
    if cached:
        return cached
    families_xml = get_families_xml(db_dir)
    if not families_xml.exists():
        return {"status": "error", "error": {"code": "FAMILIES_NOT_FOUND", "message": "families.xml not found"}}
    parser = FamiliesParser(families_xml)
    result = parser.find_mcu(mcu_name)
    if result is None:
        return {"status": "error", "error": {"code": "MCU_NOT_FOUND", "message": f"MCU '{mcu_name}' not found"}}
    mcu_xml = get_mcu_xml_path(db_dir, mcu_name)
    if mcu_xml and mcu_xml.exists():
        mcu_parser = McuParser(mcu_xml)
        detailed = mcu_parser.parse()
        result.update(detailed)
    output = {"status": "ok", "data": result}
    cache.set("chip", dbsig, mcu_name, data=output)
    return output

def handle_chip_list(family=None, core=None, db_path=None, cache=None):
    if cache is None:
        cache = Cache()
    db_dir, dbsig = get_db_signature(db_path)
    if db_dir is None:
        return {"status": "error", "error": {"code": "DB_NOT_FOUND", "message": "CubeMX database not found"}}
    cache_key = f"chip_list_{dbsig}_{family}_{core}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    families_xml = get_families_xml(db_dir)
    if not families_xml.exists():
        return {"status": "error", "error": {"code": "FAMILIES_NOT_FOUND", "message": "families.xml not found"}}
    parser = FamiliesParser(families_xml)
    result = parser.list_mcus(family_filter=family, core_filter=core)
    output = {"status": "ok", "data": result, "count": len(result)}
    cache.set(cache_key, data=output)
    return output
