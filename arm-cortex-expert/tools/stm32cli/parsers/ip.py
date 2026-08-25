import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.xml_parser import parse_xml

class IpParser:
    def __init__(self, ip_dir):
        self.ip_dir = Path(ip_dir)

    def find_ip_file(self, ip_name, mcu_family=None):
        ip_name_upper = ip_name.upper()
        candidates = []
        for f in self.ip_dir.glob("*.xml"):
            fname = f.name.upper()
            if ip_name_upper in fname:
                candidates.append(f)
        if not candidates:
            return None
        if mcu_family:
            family_upper = mcu_family.upper()
            for c in candidates:
                if family_upper in c.name.upper():
                    return c
        candidates.sort(key=lambda x: x.name, reverse=True)
        return candidates[0]

    def parse_modes(self, ip_file):
        try:
            root = parse_xml(ip_file)
        except Exception:
            return {}
        result = {
            "name": root.get("Name", ""),
            "version": root.get("Version", ""),
            "modes": {}
        }
        for mode in root.findall(".//Mode"):
            mode_name = mode.get("Name", "")
            if mode_name:
                params = {}
                for param in mode.findall("Parameter"):
                    param_name = param.get("Name", "")
                    if param_name:
                        params[param_name] = {
                            "value": param.get("Value", ""),
                            "default": param.get("Default", ""),
                            "description": param.get("Description", "")
                        }
                result["modes"][mode_name] = params
        return result

    def get_ip_info(self, ip_name, mcu_family=None):
        ip_file = self.find_ip_file(ip_name, mcu_family)
        if ip_file is None:
            return None
        return self.parse_modes(ip_file)
