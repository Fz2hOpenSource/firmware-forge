import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_db_signature, get_db_path, get_latest_db_version, get_mcu_xml_path
from parsers.mcu import McuParser
from cache import Cache

def handle_peripheral(peripheral_type, mcu_name, instance=None, db_path=None, cache=None):
    if cache is None:
        cache = Cache()
    db_dir, dbsig = get_db_signature(db_path)
    if db_dir is None:
        return {"status": "error", "error": {"code": "DB_NOT_FOUND", "message": "CubeMX database not found"}}
    cache_key = f"periph_{dbsig}_{mcu_name}_{peripheral_type}_{instance}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    mcu_xml = get_mcu_xml_path(db_dir, mcu_name)
    if mcu_xml is None or not mcu_xml.exists():
        return {"status": "error", "error": {"code": "MCU_NOT_FOUND", "message": f"MCU XML for '{mcu_name}' not found"}}
    parser = McuParser(mcu_xml)
    chip_info = parser.parse()
    peripherals = chip_info.get("peripherals", {})
    periph_type_upper = peripheral_type.upper()
    matching_periphs = []
    for ptype, instances in peripherals.items():
        if periph_type_upper in ptype.upper():
            matching_periphs.extend(instances)
    if not matching_periphs:
        for ptype, instances in peripherals.items():
            for inst in instances:
                if periph_type_upper in inst.upper():
                    matching_periphs.append(inst)
    if not matching_periphs:
        return {"status": "error", "error": {"code": "PERIPH_NOT_FOUND", "message": f"Peripheral '{peripheral_type}' not found"}}
    if instance:
        instance_upper = instance.upper()
        found = False
        for p in matching_periphs:
            if instance_upper in p.upper():
                found = True
                break
        if not found:
            return {"status": "error", "error": {"code": "INSTANCE_NOT_FOUND", "message": f"Instance '{instance}' not found"}}
        matching_periphs = [p for p in matching_periphs if instance_upper in p.upper()]
    results = []
    for periph_name in matching_periphs:
        info = parser.get_peripheral_info(periph_name)
        info["type"] = peripheral_type
        results.append(info)
    if len(results) == 1:
        results = results[0]
    output = {"status": "ok", "data": results}
    cache.set(cache_key, data=output)
    return output

def handle_peripheral_list(mcu_name, db_path=None, cache=None):
    if cache is None:
        cache = Cache()
    db_dir, dbsig = get_db_signature(db_path)
    if db_dir is None:
        return {"status": "error", "error": {"code": "DB_NOT_FOUND", "message": "CubeMX database not found"}}
    cache_key = f"periph_list_{dbsig}_{mcu_name}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    mcu_xml = get_mcu_xml_path(db_dir, mcu_name)
    if mcu_xml is None or not mcu_xml.exists():
        return {"status": "error", "error": {"code": "MCU_NOT_FOUND", "message": f"MCU XML for '{mcu_name}' not found"}}
    parser = McuParser(mcu_xml)
    chip_info = parser.parse()
    peripherals = chip_info.get("peripherals", {})
    output = {"status": "ok", "data": peripherals}
    cache.set(cache_key, data=output)
    return output
