import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_db_signature, get_db_path, get_latest_db_version, get_mcu_xml_path
from parsers.mcu import McuParser
from cache import Cache

def handle_irq(peripheral, mcu_name, db_path=None, cache=None):
    if cache is None:
        cache = Cache()
    db_dir, dbsig = get_db_signature(db_path)
    if db_dir is None:
        return {"status": "error", "error": {"code": "DB_NOT_FOUND", "message": "CubeMX database not found"}}
    cache_key = f"irq_{dbsig}_{mcu_name}_{peripheral}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    mcu_xml = get_mcu_xml_path(db_dir, mcu_name)
    if mcu_xml is None or not mcu_xml.exists():
        return {"status": "error", "error": {"code": "MCU_NOT_FOUND", "message": f"MCU XML for '{mcu_name}' not found"}}
    parser = McuParser(mcu_xml)
    chip_info = parser.parse()
    interrupts = chip_info.get("interrupts", {})
    periph_upper = peripheral.upper()
    result = {}
    for irq_name, irq_info in interrupts.items():
        if periph_upper in irq_name.upper():
            result[irq_name] = irq_info
    if not result:
        return {"status": "error", "error": {"code": "IRQ_NOT_FOUND", "message": f"No interrupts found for '{peripheral}'"}}
    output = {"status": "ok", "data": result}
    cache.set(cache_key, data=output)
    return output

def handle_irq_list(mcu_name, db_path=None, cache=None):
    if cache is None:
        cache = Cache()
    cache_key = f"irq_list_{dbsig}_{mcu_name}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    db_dir, dbsig = get_db_signature(db_path)
    if db_dir is None:
        return {"status": "error", "error": {"code": "DB_NOT_FOUND", "message": "CubeMX database not found"}}
    mcu_xml = get_mcu_xml_path(db_dir, mcu_name)
    if mcu_xml is None or not mcu_xml.exists():
        return {"status": "error", "error": {"code": "MCU_NOT_FOUND", "message": f"MCU XML for '{mcu_name}' not found"}}
    parser = McuParser(mcu_xml)
    chip_info = parser.parse()
    interrupts = chip_info.get("interrupts", {})
    output = {"status": "ok", "data": interrupts}
    cache.set(cache_key, data=output)
    return output
