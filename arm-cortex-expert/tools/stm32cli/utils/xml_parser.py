import xml.etree.ElementTree as ET
from pathlib import Path

def parse_xml(file_path):
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"XML parse error: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

def get_element_text(element, tag, default=None):
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return default

def get_element_int(element, tag, default=None):
    text = get_element_text(element, tag)
    if text is not None:
        try:
            return int(text)
        except ValueError:
            return default
    return default

def get_element_float(element, tag, default=None):
    text = get_element_text(element, tag)
    if text is not None:
        try:
            return float(text)
        except ValueError:
            return default
    return default

def get_attributes(element, attrs):
    result = {}
    for attr in attrs:
        if attr in element.attrib:
            result[attr] = element.attrib[attr]
    return result

def find_elements(root, xpath):
    return root.findall(xpath)

def find_element(root, xpath):
    return root.find(xpath)
