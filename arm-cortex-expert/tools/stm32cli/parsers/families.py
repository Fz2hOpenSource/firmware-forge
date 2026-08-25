import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.xml_parser import parse_xml, get_element_text, get_element_int

class FamiliesParser:
    def __init__(self, families_xml_path):
        self.path = families_xml_path
        self.root = None

    def _load(self):
        if self.root is None:
            self.root = parse_xml(self.path)

    def find_mcu(self, mcu_name):
        self._load()
        for family in self.root.findall(".//Family"):
            for subfamily in family.findall("SubFamily"):
                for mcu in subfamily.findall("Mcu"):
                    ref_name = mcu.get("RefName", "")
                    if ref_name == mcu_name:
                        return self._parse_mcu(mcu, family.get("Name"), subfamily.get("Name"))
                    rpn = mcu.get("RPN", "")
                    if rpn and mcu_name.startswith(rpn):
                        return self._parse_mcu(mcu, family.get("Name"), subfamily.get("Name"))
        return None

    def _parse_mcu(self, mcu_elem, family_name, subfamily_name):
        core = get_element_text(mcu_elem, "Core", "")
        freq = get_element_int(mcu_elem, "Frequency", 0)
        ram = get_element_int(mcu_elem, "Ram", 0)
        flash = get_element_int(mcu_elem, "Flash", 0)
        io_nb = get_element_int(mcu_elem, "IONb", 0)
        package = mcu_elem.get("PackageName", "")
        ref_name = mcu_elem.get("RefName", "")
        rpn = mcu_elem.get("RPN", "")

        voltage_elem = mcu_elem.find("Voltage")
        voltage = {}
        if voltage_elem is not None:
            voltage = {
                "min": float(voltage_elem.get("Min", 0)),
                "max": float(voltage_elem.get("Max", 0))
            }

        temp_elem = mcu_elem.find("Temperature")
        temperature = {}
        if temp_elem is not None:
            temperature = {
                "min": float(temp_elem.get("Min", 0)),
                "max": float(temp_elem.get("Max", 0))
            }

        peripherals = []
        for periph in mcu_elem.findall("Peripheral"):
            peripherals.append({
                "type": periph.get("Type", ""),
                "max": int(periph.get("MaxOccurs", 1))
            })

        return {
            "name": ref_name,
            "rpn": rpn,
            "family": family_name,
            "subfamily": subfamily_name,
            "core": core,
            "freq_mhz": freq,
            "ram_kb": ram,
            "flash_kb": flash,
            "io_count": io_nb,
            "package": package,
            "voltage": voltage,
            "temperature": temperature,
            "peripherals": peripherals
        }

    def list_mcus(self, family_filter=None, core_filter=None):
        self._load()
        result = []
        for family in self.root.findall(".//Family"):
            family_name = family.get("Name", "")
            if family_filter and family_filter.upper() not in family_name.upper():
                continue
            for subfamily in family.findall("SubFamily"):
                for mcu in subfamily.findall("Mcu"):
                    core = get_element_text(mcu, "Core", "")
                    if core_filter and core_filter.upper() not in core.upper():
                        continue
                    result.append({
                        "name": mcu.get("RefName", ""),
                        "family": family_name,
                        "core": core,
                        "ram_kb": get_element_int(mcu, "Ram", 0),
                        "flash_kb": get_element_int(mcu, "Flash", 0)
                    })
        return result
