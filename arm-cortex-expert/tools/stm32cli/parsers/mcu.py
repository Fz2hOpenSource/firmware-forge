import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.xml_parser import parse_xml

class McuParser:
    def __init__(self, mcu_xml_path):
        self.path = mcu_xml_path
        self.root = None
        self.ns = {'ns': 'http://mcd.rou.st.com/modules.php?name=mcu'}

    def _load(self):
        if self.root is None:
            self.root = parse_xml(self.path)

    def _find(self, element, tag):
        result = element.find(f'ns:{tag}', self.ns)
        if result is None:
            result = element.find(tag)
        return result

    def _findall(self, element, tag):
        result = element.findall(f'ns:{tag}', self.ns)
        if not result:
            result = element.findall(tag)
        return result

    def _get_text(self, element, tag, default=""):
        child = self._find(element, tag)
        if child is not None and child.text:
            return child.text.strip()
        return default

    def _get_int(self, element, tag, default=0):
        text = self._get_text(element, tag)
        if text:
            try:
                return int(text)
            except ValueError:
                return default
        return default

    def parse(self):
        self._load()
        mcu = self.root
        core = self._get_text(mcu, "Core")
        if not core:
            core = mcu.get("Core", "")
        result = {
            "name": mcu.get("RefName", mcu.get("Name", "")),
            "package": mcu.get("Package", ""),
            "core": core,
            "frequency": self._get_int(mcu, "Frequency"),
            "flash": self._get_int(mcu, "Flash"),
            "ram": self._parse_ram(mcu),
            "io_count": self._get_int(mcu, "IONb"),
            "voltage": self._parse_voltage(mcu),
            "temperature": self._parse_temperature(mcu),
            "peripherals": self._parse_peripherals(mcu),
            "pins": self._parse_pins(mcu),
            "dma_channels": self._parse_dma(mcu),
            "interrupts": self._parse_interrupts(mcu)
        }
        return result

    def _parse_ram(self, mcu):
        ram_total = self._get_int(mcu, "Ram")
        ram_sections = {}
        for mem in self._findall(mcu, "Memory"):
            name = mem.get("Name", "")
            if "RAM" in name.upper() or "SRAM" in name.upper() or "DTCM" in name.upper():
                size_str = mem.get("Size", "0")
                try:
                    size = int(size_str, 0) if size_str else 0
                    if size > 0:
                        ram_sections[name.lower()] = size // 1024
                except ValueError:
                    pass
        if not ram_sections and ram_total > 0:
            ram_sections["total"] = ram_total
        return ram_sections

    def _parse_voltage(self, mcu):
        v = self._find(mcu, "Voltage")
        if v is not None:
            return {
                "min": float(v.get("Min", 0)),
                "max": float(v.get("Max", 0))
            }
        return {}

    def _parse_temperature(self, mcu):
        t = self._find(mcu, "Temperature")
        if t is not None:
            return {
                "min": float(t.get("Min", 0)),
                "max": float(t.get("Max", 0))
            }
        return {}

    def _parse_peripherals(self, mcu):
        peripherals = {}
        for ip in self._findall(mcu, "IP"):
            name = ip.get("InstanceName", "")
            ip_type = ip.get("Name", "")
            if name and ip_type:
                if ip_type not in peripherals:
                    peripherals[ip_type] = []
                peripherals[ip_type].append(name)
        return peripherals

    def _parse_pins(self, mcu):
        pins = {}
        for pin in self._findall(mcu, "Pin"):
            pin_name = pin.get("Name", "")
            if not pin_name:
                continue
            pin_info = {
                "type": pin.get("Type", ""),
                "position": pin.get("Position", ""),
                "signals": []
            }
            for signal in self._findall(pin, "Signal"):
                sig_name = signal.get("Name", "")
                if sig_name:
                    pin_info["signals"].append(sig_name)
            if pin_info["signals"]:
                pins[pin_name] = pin_info
        return pins

    def _parse_dma(self, mcu):
        dma = {}
        for controller in self._findall(mcu, "DmaController"):
            ctrl_name = controller.get("Name", "")
            for request in self._findall(controller, "Request"):
                req_name = request.get("Name", "")
                if req_name:
                    channels = []
                    for channel in self._findall(request, "Channel"):
                        ch_name = channel.get("Name", "")
                        if ch_name:
                            channels.append(ch_name)
                    if channels:
                        dma[req_name] = {"controller": ctrl_name, "channels": channels}
        return dma

    def _parse_interrupts(self, mcu):
        interrupts = {}
        for irq in self._findall(mcu, "Interrupt"):
            name = irq.get("Name", "")
            if name:
                interrupts[name] = {
                    "position": irq.get("Position", ""),
                    "description": irq.get("Description", "")
                }
        return interrupts

    def get_peripheral_info(self, peripheral_name):
        self._load()
        result = {
            "name": peripheral_name,
            "dma": {"rx": [], "tx": []},
            "pins": {},
            "interrupts": []
        }
        dma = self._parse_dma(self.root)
        for req_name, req_info in dma.items():
            if peripheral_name.upper() in req_name.upper():
                if "RX" in req_name.upper() or "RECEIVE" in req_name.upper():
                    result["dma"]["rx"].extend(req_info["channels"])
                elif "TX" in req_name.upper() or "TRANSMIT" in req_name.upper():
                    result["dma"]["tx"].extend(req_info["channels"])
                else:
                    result["dma"]["rx"].extend(req_info["channels"])
        pins = self._parse_pins(self.root)
        for pin_name, pin_info in pins.items():
            for signal in pin_info["signals"]:
                if peripheral_name.upper() in signal.upper():
                    if signal not in result["pins"]:
                        result["pins"][signal] = []
                    result["pins"][signal].append(pin_name)
        interrupts = self._parse_interrupts(self.root)
        for irq_name, irq_info in interrupts.items():
            if peripheral_name.upper() in irq_name.upper():
                result["interrupts"].append({"name": irq_name, **irq_info})
        return result
