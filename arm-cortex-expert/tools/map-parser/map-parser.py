#!/usr/bin/env python3
import re
import sys
import json
import argparse
import os
from pathlib import Path

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

TYPE_MAP = {
    "Data": "DATA",
    "Thumb Code": "CODE",
    "Thumb": "CODE",
    "ARM Code": "CODE",
    "Code": "CODE",
    "Number": "NUMBER",
    "Section": "SECTION",
    "PAD": "PAD",
    "Undefined": "UNDEF",
}

def output_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

def error(msg):
    output_json({"status": "error", "error": {"message": msg}})
    sys.exit(1)

def parse_map(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        error(f"Map file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    local_symbols_start = None
    global_symbols_start = None
    memory_map_start = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "Local Symbols":
            local_symbols_start = i
        elif stripped == "Global Symbols":
            global_symbols_start = i
        elif stripped == "Memory Map of the image":
            memory_map_start = i

    return lines, local_symbols_start, global_symbols_start, memory_map_start

def parse_symbol_section(lines, start, end):
    symbols = []
    header_pattern = re.compile(r"^\s{4,}Symbol Name\s+Value\s+Ov Type\s+Size\s+Object\(Section\)")
    data_start = None
    for i in range(start + 1, min(start + 10, len(lines))):
        if header_pattern.match(lines[i]):
            data_start = i + 2
            break

    if data_start is None:
        return symbols

    for i in range(data_start, end):
        line = lines[i]
        stripped = line.rstrip("\n\r")
        if not stripped.strip():
            continue
        if "Symbol Name" in stripped and "Value" in stripped:
            continue
        if not stripped.startswith("    "):
            continue
        parts = stripped.split()
        if len(parts) < 5:
            continue

        name = parts[0]
        value = parts[1]

        size_idx = None
        for j in range(2, len(parts)):
            try:
                int(parts[j])
                size_idx = j
                break
            except ValueError:
                if parts[j].startswith("0x"):
                    try:
                        int(parts[j], 16)
                        size_idx = j
                        break
                    except ValueError:
                        continue

        if size_idx is None or size_idx < 3:
            continue

        sym_type = " ".join(parts[2:size_idx])
        size_str = parts[size_idx]
        obj_section = " ".join(parts[size_idx+1:]) if size_idx+1 < len(parts) else ""

        size = 0
        try:
            size = int(size_str, 16) if size_str.startswith("0x") else int(size_str)
        except ValueError:
            size = 0

        addr = None
        if value.startswith("0x"):
            try:
                addr = int(value, 16)
            except ValueError:
                addr = None

        symbols.append({
            "name": name,
            "address": value if value == "-" else value,
            "address_int": addr,
            "type": sym_type,
            "type_norm": TYPE_MAP.get(sym_type, sym_type.upper()),
            "size": size,
            "object_section": obj_section
        })

    return symbols

def parse_all_symbols(lines, local_start, global_start, memory_map_start):
    map_end = memory_map_start if memory_map_start else len(lines)
    local_symbols = []
    global_symbols = []

    if local_start is not None:
        end = global_start if global_start else map_end
        local_symbols = parse_symbol_section(lines, local_start, end)

    if global_start is not None:
        global_symbols = parse_symbol_section(lines, global_start, map_end)

    return local_symbols + global_symbols

def parse_memory_map(lines, memory_map_start):
    regions = []
    if memory_map_start is None:
        return regions

    current_region = None
    exec_region_pattern = re.compile(
        r"^\s{4}Execution Region\s+(\S+)\s+\(Exec base:\s+(0x[0-9a-fA-F]+),\s+Load base:\s+(0x[0-9a-fA-F]+),\s+Size:\s+(0x[0-9a-fA-F]+),"
    )
    load_region_pattern = re.compile(
        r"^\s{2}Load Region\s+(\S+)\s+\(Base:\s+(0x[0-9a-fA-F]+),\s+Size:\s+(0x[0-9a-fA-F]+),"
    )
    entry_pattern = re.compile(
        r"^\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)\s+(\S+)\s+(\S+)"
    )

    for i in range(memory_map_start, len(lines)):
        line = lines[i]
        stripped = line.strip()

        load_match = load_region_pattern.match(line)
        if load_match:
            current_region = {
                "type": "load",
                "name": load_match.group(1),
                "base": load_match.group(2),
                "size": load_match.group(3),
                "exec_regions": []
            }
            regions.append(current_region)
            continue

        exec_match = exec_region_pattern.match(line)
        if exec_match:
            er = {
                "type": "exec",
                "name": exec_match.group(1),
                "exec_base": exec_match.group(2),
                "load_base": exec_match.group(3),
                "size": exec_match.group(4),
                "entries": []
            }
            if current_region and current_region["type"] == "load":
                current_region["exec_regions"].append(er)
            else:
                regions.append(er)
            current_region = er
            continue

        entry_match = entry_pattern.match(line)
        if entry_match and current_region:
            entry = {
                "exec_addr": entry_match.group(1),
                "load_addr": entry_match.group(2),
                "size": entry_match.group(3),
                "type": entry_match.group(4),
                "attr": entry_match.group(5),
                "section": "",
                "object": ""
            }

            rest = line[entry_match.end():].strip()
            if rest:
                parts = rest.split(None, 2)
                if len(parts) >= 3:
                    entry["section"] = parts[1]
                    entry["object"] = parts[2]
                elif len(parts) == 2:
                    entry["section"] = parts[0]
                    entry["object"] = parts[1]
                elif len(parts) == 1:
                    entry["section"] = parts[0]

            current_region["entries"].append(entry)

    return regions

def find_symbols(symbols, pattern):
    pattern_lower = pattern.lower().replace("*", ".*").replace("?", ".")
    try:
        regex = re.compile(f"^{pattern_lower}$", re.IGNORECASE)
    except re.error:
        regex = re.compile(re.escape(pattern_lower), re.IGNORECASE)

    results = []
    for sym in symbols:
        if regex.search(sym["name"].lower()) or re.search(pattern_lower, sym["name"].lower()):
            results.append(sym)

    return results

def filter_symbols(symbols, data_only, type_filter):
    if not data_only and not type_filter:
        return symbols
    filtered = []
    for s in symbols:
        if data_only and s.get("type") != "Data":
            continue
        if type_filter and s.get("type") not in type_filter:
            continue
        filtered.append(s)
    return filtered

def compact_output(symbols):
    return [{"n": s["name"], "a": s.get("address"), "s": s.get("size"), "o": s.get("object_section")} for s in symbols]

def find_symbol_containing(symbols, target_addr):
    candidates = []
    for s in symbols:
        addr = s.get("address_int")
        size = s.get("size", 0)
        if addr is not None and size > 0 and addr <= target_addr < addr + size:
            candidates.append(s)
    return min(candidates, key=lambda x: x.get("size", float("inf"))) if candidates else None

def find_memory_region(regions, target):
    def _search(region):
        if region.get("type") == "exec":
            base_str = region.get("exec_base", "0")
            size_str = region.get("size", "0")
        elif region.get("type") == "load":
            base_str = region.get("base", "0")
            size_str = region.get("size", "0")
        else:
            return None
        try:
            base = int(base_str, 16)
            size = int(size_str, 16)
            in_range = base <= target < base + size
        except ValueError:
            return None

        for er in region.get("exec_regions", []):
            result = _search(er)
            if result:
                return result

        if in_range:
            return region
        return None

    for r in regions:
        result = _search(r)
        if result:
            return result
    return None

def flatten_regions(regions):
    flat = []
    def _walk(r):
        info = {
            "type": r.get("type"),
            "name": r.get("name"),
        }
        if r.get("type") == "load":
            info["base"] = r.get("base")
            info["size"] = r.get("size")
        elif r.get("type") == "exec":
            info["exec_base"] = r.get("exec_base")
            info["load_base"] = r.get("load_base")
            info["size"] = r.get("size")
        flat.append(info)
        for er in r.get("exec_regions", []):
            _walk(er)
    for r in regions:
        _walk(r)
    return flat

def collect_entries(regions):
    entries = []
    def _walk(r):
        for e in r.get("entries", []):
            entries.append(e)
        for er in r.get("exec_regions", []):
            _walk(er)
    for r in regions:
        _walk(r)
    return entries

def extract_object_name(raw):
    raw = raw.strip()
    if not raw:
        return None
    parts = raw.split()
    return parts[-1] if parts else None

def region_range_str(region):
    if region.get("type") == "exec":
        base = region.get("exec_base", "0")
        size = region.get("size", "0")
    else:
        base = region.get("base", "0")
        size = region.get("size", "0")
    try:
        b = int(base, 16)
        s = int(size, 16)
        return f"{base} - 0x{b+s:08X}"
    except ValueError:
        return f"{base} + {size}"

def cmd_find(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    symbols = parse_all_symbols(lines, ls, gs, mm)

    patterns = [p.strip() for p in args.pattern.split(",")]
    all_results = []
    seen = set()
    for p in patterns:
        if not p:
            continue
        res = find_symbols(symbols, p)
        for r in res:
            key = (r["name"], r.get("address"))
            if key not in seen:
                seen.add(key)
                all_results.append(r)

    all_results = filter_symbols(all_results, args.data, args.type)

    name_counts = {}
    for s in all_results:
        name_counts[s["name"]] = name_counts.get(s["name"], 0) + 1
    for s in all_results:
        if name_counts[s["name"]] > 1:
            s["ambiguous"] = True

    total = len(all_results)

    if args.compact or total > 50:
        out = compact_output(all_results)
        output_json({"status": "ok", "count": total, "compact": True, "symbols": out})
    else:
        output_json({"status": "ok", "count": total, "symbols": all_results})

def cmd_section(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    regions = parse_memory_map(lines, mm)

    target = args.section_name.lower()
    for r in regions:
        if r.get("name", "").lower() == target or r.get("name", "").lower().endswith(target):
            output_json({"status": "ok", "region": r})
            return

    output_json({"status": "ok", "message": f"Section '{args.section_name}' not found", "regions": regions})

def cmd_range(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    symbols = parse_all_symbols(lines, ls, gs, mm)

    try:
        target = int(args.address, 16)
    except ValueError:
        error(f"Invalid address: {args.address}")

    exact = [s for s in symbols if s["address_int"] == target]
    surrounding = [s for s in symbols if s["address_int"] is not None and abs(s["address_int"] - target) <= 256]

    regions = parse_memory_map(lines, mm)
    region = find_memory_region(regions, target)

    result = {
        "status": "ok",
        "address": args.address,
        "exact": exact,
        "surrounding": surrounding,
        "memory_region": region
    }
    if region is None:
        result["valid"] = False
        result["warning"] = "address not in any execution region"
    output_json(result)

def cmd_info(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    all_symbols = parse_all_symbols(lines, ls, gs, mm)

    data_symbols = [s for s in all_symbols if s["type"] == "Data" and s["address_int"] is not None]
    code_symbols = [s for s in all_symbols if s["type"] in ("Thumb Code", "Thumb", "Code", "ARM Code")]
    undefined = [s for s in all_symbols if s["type"] == "Undefined"]

    total_flash = 0
    total_ram = 0
    regions = parse_memory_map(lines, mm)
    for r in flatten_regions(regions):
        if r.get("type") == "exec":
            try:
                base = int(r.get("exec_base", "0"), 16)
                size = int(r.get("size", "0"), 16)
                if base >= 0x08000000 and base < 0x10000000:
                    total_flash += size
                elif base >= 0x20000000 and base < 0x40000000:
                    total_ram += size
            except ValueError:
                pass

    output_json({
        "status": "ok",
        "path": args.map_file,
        "total_symbols": len(all_symbols),
        "data_symbols": len(data_symbols),
        "code_symbols": len(code_symbols),
        "undefined_refs": len(undefined),
        "flash_usage_bytes": total_flash,
        "ram_usage_bytes": total_ram
    })

def cmd_sections(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    regions = parse_memory_map(lines, mm)

    if args.summary:
        flat = flatten_regions(regions)
        output_json({"status": "ok", "count": len(flat), "regions": flat, "summary": True})
    else:
        entry_count = 0
        def _count_entries(r):
            nonlocal entry_count
            entry_count += len(r.get("entries", []))
            for er in r.get("exec_regions", []):
                _count_entries(er)
        for r in regions:
            _count_entries(r)
        if entry_count > 500:
            flat = flatten_regions(regions)
            output_json({
                "status": "ok",
                "count": len(flat),
                "regions": flat,
                "summary": True,
                "note": f"Full output suppressed ({entry_count} entries). Use --summary for compact view or specify section name."
            })
        else:
            output_json({"status": "ok", "count": len(regions), "regions": regions})

def cmd_fault(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    symbols = parse_all_symbols(lines, ls, gs, mm)
    regions = parse_memory_map(lines, mm)

    try:
        pc = int(args.pc, 16)
    except ValueError:
        error(f"Invalid PC address: {args.pc}")

    pc_sym = find_symbol_containing(symbols, pc)
    pc_region = find_memory_region(regions, pc)

    result = {
        "status": "ok",
        "pc": args.pc,
        "pc_function": pc_sym["name"] if pc_sym else None,
        "pc_offset": f"0x{pc - pc_sym['address_int']:X}" if pc_sym else None,
        "pc_section": pc_sym.get("object_section") if pc_sym else None,
        # 事实：PC 是否被某个执行/加载区域覆盖（不假设代码必须位于 Flash）
        "pc_in_mapped_execution_region": pc_region is not None,
        "pc_region": f"{pc_region['name']} ({region_range_str(pc_region)})" if pc_region else None,
    }
    heuristic_warnings = []
    if pc_region is not None:
        try:
            exec_base = int(pc_region.get("exec_base", pc_region.get("base", "0")), 16)
            if exec_base < 0x08000000:
                heuristic_warnings.append(
                    "PC maps into a non-flash execution region (ITCM/SRAM executing code?) "
                    "- confirm this matches your platform's memory plan")
        except (ValueError, TypeError):
            pass
    else:
        heuristic_warnings.append(
            "PC not mapped by any execution region in the map file - likely invalid jump")

    if args.lr:
        try:
            lr = int(args.lr, 16)
            lr_sym = find_symbol_containing(symbols, lr)
            result["lr"] = args.lr
            result["lr_function"] = lr_sym["name"] if lr_sym else None
        except ValueError:
            result["lr_error"] = f"Invalid LR address: {args.lr}"

    if args.addr:
        try:
            addr = int(args.addr, 16)
            addr_sym = find_symbol_containing(symbols, addr)
            addr_region = find_memory_region(regions, addr)
            result["addr"] = args.addr
            result["addr_variable"] = f"{addr_sym['name']} + 0x{addr - addr_sym['address_int']:X}" if addr_sym else None
            result["addr_region"] = f"{addr_region['name']} ({region_range_str(addr_region)})" if addr_region else None
            result["addr_in_region"] = addr_region is not None
        except ValueError:
            result["addr_error"] = f"Invalid access address: {args.addr}"

    if args.sp:
        try:
            sp = int(args.sp, 16)
            sp_region = find_memory_region(regions, sp)
            result["sp"] = args.sp
            # 事实：SP 是否被某个内存区域覆盖。是否真的越栈需要栈边界信息，
            # map 文件无法提供——不做"栈溢出"结论。
            result["sp_in_mapped_memory_region"] = sp_region is not None
            if sp_region:
                result["sp_region"] = f"{sp_region['name']} ({region_range_str(sp_region)})"
        except ValueError:
            result["sp_error"] = f"Invalid SP address: {args.sp}"

    if args.addr and not result.get("addr_in_region", True):
        heuristic_warnings.append("Access address not in any execution region - likely invalid access")
    result["heuristic_warnings"] = heuristic_warnings

    output_json(result)

def cmd_size_rank(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    regions = parse_memory_map(lines, mm)
    entries = collect_entries(regions)

    by = args.by if args.by else "object"
    top = args.top if args.top else 10

    groups = {}
    for e in entries:
        if by == "object":
            raw = e.get("object", "")
            key = extract_object_name(raw) or "(unknown)"
        else:
            key = e.get("section", "") or "(unknown)"

        try:
            size = int(e.get("size", "0"), 16)
        except ValueError:
            size = 0

        if key not in groups:
            groups[key] = {"size": 0, "entries": 0}
        groups[key]["size"] += size
        groups[key]["entries"] += 1

    sorted_groups = sorted(groups.items(), key=lambda x: x[1]["size"], reverse=True)[:top]

    rankings = []
    for i, (name, info) in enumerate(sorted_groups):
        rankings.append({
            "rank": i + 1,
            "name": name,
            "size": info["size"],
            "entries": info["entries"]
        })

    total_size = sum(g["size"] for g in groups.values())

    output_json({
        "status": "ok",
        "by": by,
        "top": top,
        "total_entries": len(entries),
        "total_size_bytes": total_size,
        "rankings": rankings
    })

def cmd_mpu_check(args):
    lines, ls, gs, mm = parse_map(args.map_file)
    regions = parse_memory_map(lines, mm)
    all_symbols = parse_all_symbols(lines, ls, gs, mm)

    try:
        base = int(args.base, 16)
    except ValueError:
        error(f"Invalid base address: {args.base}")

    try:
        size = int(args.size, 10)
    except ValueError:
        error(f"Invalid size: {args.size}")

    target_region = None
    flat = flatten_regions(regions)
    for r in flat:
        if r.get("name", "").lower() == args.region.lower():
            target_region = r
            break

    if target_region is None:
        error(f"Region '{args.region}' not found in map file")

    if target_region.get("type") == "exec":
        region_base = int(target_region.get("exec_base", "0"), 16)
        region_size = int(target_region.get("size", "0"), 16)
    else:
        region_base = int(target_region.get("base", "0"), 16)
        region_size = int(target_region.get("size", "0"), 16)

    is_power_of_two = (size & (size - 1)) == 0 and size > 0
    base_aligned = (base % size == 0) if is_power_of_two else False

    symbols_in = []
    symbols_out = []
    for s in all_symbols:
        addr = s.get("address_int")
        if addr is None or s.get("size", 0) == 0:
            continue
        if region_base <= addr < region_base + region_size:
            if base <= addr < base + size:
                symbols_in.append(s)
            else:
                symbols_out.append(s)

    violations = []
    if not is_power_of_two:
        violations.append(f"Size {size} (0x{size:X}) is not a power of 2 - MPU requires power-of-2 region size")
    if is_power_of_two and not base_aligned:
        violations.append(f"Base 0x{base:X} is not aligned to size {size} (0x{size:X}) - MPU requires base % size == 0")
    # 覆盖关系判定：MPU 区间必须完整覆盖与之相交的每个链接区域。
    # 一个 MPU 区域可以保护多个更小的链接区（完全相等既不必要也不常见）；
    # 部分相交会把一个链接区劈成受保护/不受保护两半——这才是要抓的错。
    def _range_of(r):
        try:
            if r.get("type") == "exec":
                b = int(r.get("exec_base", "0"), 16)
            else:
                b = int(r.get("base", "0"), 16)
            s = int(r.get("size", "0"), 16)
        except (ValueError, TypeError):
            return None
        return (b, b + s) if s > 0 else None

    mpu_lo, mpu_hi = base, base + size
    for r in flat:
        rng = _range_of(r)
        if rng is None:
            continue
        rb, rend = rng
        if rb < mpu_hi and mpu_lo < rend:      # 与 MPU 区间相交
            if not (mpu_lo <= rb and rend <= mpu_hi):
                violations.append(
                    f"Region '{r.get('name')}' [{rb:#x}-{rend:#x}) is only partially inside "
                    f"MPU range [0x{mpu_lo:X}-0x{mpu_hi:X}) - MPU would split it")
    for s in symbols_out:
        violations.append(f"Symbol '{s['name']}' at {s['address']} is in region but outside MPU range [0x{base:X} - 0x{base+size:X})")

    output_json({
        "status": "ok",
        "coverage_model": "containment",
        "region": args.region,
        "region_base": f"0x{region_base:08X}",
        "region_size": region_size,
        "mpu_base": f"0x{base:08X}",
        "mpu_size": size,
        "base_aligned": base_aligned,
        "is_power_of_two": is_power_of_two,
        "symbols_in_range": len(symbols_in),
        "symbols_out_of_range": len(symbols_out),
        "violations": violations
    })

def main():
    parser = argparse.ArgumentParser(description="Keil MDK-ARM .map file parser for AI")
    subparsers = parser.add_subparsers(dest="command")

    find_parser = subparsers.add_parser("find", help="Find symbols by name pattern (comma-separated for multiple)")
    find_parser.add_argument("map_file", help="Path to .map file")
    find_parser.add_argument("pattern", help="Symbol name pattern (supports *, ? and commas for multi-pattern)")
    find_parser.add_argument("--data", action="store_true", help="Show Data symbols only (variables, not functions)")
    find_parser.add_argument("--type", nargs="*", help="Filter by type(s): Data, Thumb, Code, Section, Number")
    find_parser.add_argument("--compact", action="store_true", help="Compact output (always used when >50 results)")

    info_parser = subparsers.add_parser("info", help="Show map file summary")
    info_parser.add_argument("map_file", help="Path to .map file")

    section_parser = subparsers.add_parser("section", help="Show memory section details")
    section_parser.add_argument("map_file", help="Path to .map file")
    section_parser.add_argument("section_name", help="Section name (e.g. .bss, .data, ER_IROM1)")

    range_parser = subparsers.add_parser("range", help="Find symbols near an address")
    range_parser.add_argument("map_file", help="Path to .map file")
    range_parser.add_argument("address", help="Target address (e.g. 0x20004ddc)")

    sections_parser = subparsers.add_parser("sections", help="List all memory sections")
    sections_parser.add_argument("map_file", help="Path to .map file")
    sections_parser.add_argument("--summary", action="store_true", help="Show compact summary without entries")

    fault_parser = subparsers.add_parser("fault", help="HardFault address analysis")
    fault_parser.add_argument("map_file", help="Path to .map file")
    fault_parser.add_argument("--pc", required=True, help="Fault PC address (required)")
    fault_parser.add_argument("--addr", help="Access address from BFAR/MMFAR (optional)")
    fault_parser.add_argument("--lr", help="Link Register value (optional)")
    fault_parser.add_argument("--sp", help="Stack Pointer value (optional)")

    rank_parser = subparsers.add_parser("size-rank", help="Rank memory usage by object or section")
    rank_parser.add_argument("map_file", help="Path to .map file")
    rank_parser.add_argument("--by", choices=["object", "section"], default="object", help="Group by object file or section")
    rank_parser.add_argument("--top", type=int, default=10, help="Number of top entries to show")

    mpu_parser = subparsers.add_parser("mpu-check", help="Check MPU region alignment and symbol placement")
    mpu_parser.add_argument("map_file", help="Path to .map file")
    mpu_parser.add_argument("--region", required=True, help="Execution region name (e.g. RW_IRAM2)")
    mpu_parser.add_argument("--base", required=True, help="MPU region base address (e.g. 0x24000000)")
    mpu_parser.add_argument("--size", required=True, help="MPU region size in bytes (e.g. 65536)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "find":
        cmd_find(args)
    elif args.command == "info":
        cmd_info(args)
    elif args.command == "section":
        cmd_section(args)
    elif args.command == "range":
        cmd_range(args)
    elif args.command == "sections":
        cmd_sections(args)
    elif args.command == "fault":
        cmd_fault(args)
    elif args.command == "size-rank":
        cmd_size_rank(args)
    elif args.command == "mpu-check":
        cmd_mpu_check(args)

if __name__ == "__main__":
    main()
