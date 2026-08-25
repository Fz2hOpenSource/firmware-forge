#!/usr/bin/env python3
"""STM32 CLI Tool for AI - query CubeMX database (chip/peripheral/DMA/pin/clock/irq)."""
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import get_db_signature
from cache import Cache
from commands.chip import handle_chip, handle_chip_list
from commands.peripheral import handle_peripheral, handle_peripheral_list
from commands.dma import handle_dma, handle_dma_list
from commands.pin import handle_pin, handle_pin_list
from commands.clock import handle_clock
from commands.irq import handle_irq, handle_irq_list

def output_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))
    # 结构化错误统一以非零退出码返回，便于脚本与 AI 判断成败
    if isinstance(data, dict) and data.get("status") == "error":
        sys.exit(1)

def _run(args, cache):
    db_path = getattr(args, "db_path", None)

    if getattr(args, "clear_cache", False):
        cache.clear()
        output_json({"status": "ok", "message": "Cache cleared"})
        return

    if args.command == "chip":
        if args.list:
            result = handle_chip_list(family=args.family, core=args.core, db_path=db_path, cache=cache)
        elif args.mcu_name:
            result = handle_chip(args.mcu_name, db_path=db_path, cache=cache)
        else:
            result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name required"}}
        output_json(result)

    elif args.command in ["peripheral", "spi", "adc", "uart", "i2c", "tim", "eth", "usb", "can"]:
        periph_type = args.command if args.command != "peripheral" else None
        if args.list:
            if not args.mcu_name:
                result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name required"}}
            else:
                result = handle_peripheral_list(args.mcu_name, db_path=db_path, cache=cache)
        elif args.mcu_name:
            if periph_type is None:
                if args.instance:
                    periph_type = args.instance
                else:
                    result = handle_peripheral_list(args.mcu_name, db_path=db_path, cache=cache)
                    output_json(result)
                    return
            result = handle_peripheral(periph_type, args.mcu_name, instance=args.instance, db_path=db_path, cache=cache)
        else:
            result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name required"}}
        output_json(result)

    elif args.command == "dma":
        if args.list:
            if not args.mcu_name:
                result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name required"}}
            else:
                result = handle_dma_list(args.mcu_name, db_path=db_path, cache=cache)
        elif args.mcu_name and args.request:
            result = handle_dma(args.request, args.mcu_name, db_path=db_path, cache=cache)
        else:
            result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name and request required"}}
        output_json(result)

    elif args.command == "pin":
        if args.list:
            if not args.mcu_name:
                result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name required"}}
            else:
                result = handle_pin_list(args.mcu_name, db_path=db_path, cache=cache)
        elif args.mcu_name and args.peripheral:
            result = handle_pin(args.peripheral, args.mcu_name, db_path=db_path, cache=cache)
        else:
            result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name and peripheral required"}}
        output_json(result)

    elif args.command == "clock":
        if not args.mcu_name:
            result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name required"}}
        else:
            result = handle_clock(args.mcu_name, db_path=db_path, cache=cache)
        output_json(result)

    elif args.command == "irq":
        if args.list:
            if not args.mcu_name:
                result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name required"}}
            else:
                result = handle_irq_list(args.mcu_name, db_path=db_path, cache=cache)
        elif args.mcu_name and args.peripheral:
            result = handle_irq(args.peripheral, args.mcu_name, db_path=db_path, cache=cache)
        else:
            result = {"status": "error", "error": {"code": "MISSING_ARG", "message": "MCU name and peripheral required"}}
        output_json(result)

def main():
    # 公共选项通过 parents 同时挂在主解析器与每个子命令上，
    # 使 `--db-path X chip Y` 与 `chip Y --db-path X` 两种写法都合法。
    # default=SUPPRESS 防止子解析器用默认值覆盖主解析器已解析到的值。
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db-path", default=argparse.SUPPRESS,
                        help="Path to CubeMX database")
    common.add_argument("--clear-cache", action="store_true",
                        default=argparse.SUPPRESS, help="Clear cache and exit")

    parser = argparse.ArgumentParser(description="STM32 CLI Tool for AI", parents=[common])
    subparsers = parser.add_subparsers(dest="command")

    def add_subparser(name, help_text, aliases=None):
        sp = subparsers.add_parser(name, help=help_text, aliases=aliases or [], parents=[common])
        return sp

    chip_parser = add_subparser("chip", "Chip info")
    chip_parser.add_argument("mcu_name", nargs="?", help="MCU name")
    chip_parser.add_argument("--list", action="store_true", help="List MCUs")
    chip_parser.add_argument("--family", help="Filter by family")
    chip_parser.add_argument("--core", help="Filter by core")

    periph_parser = add_subparser("peripheral", "Peripheral info",
                                  aliases=["spi", "adc", "uart", "i2c", "tim", "eth", "usb", "can"])
    periph_parser.add_argument("mcu_name", nargs="?", help="MCU name")
    periph_parser.add_argument("instance", nargs="?", help="Peripheral instance")
    periph_parser.add_argument("--list", action="store_true", help="List peripherals")

    dma_parser = add_subparser("dma", "DMA info")
    dma_parser.add_argument("mcu_name", nargs="?", help="MCU name")
    dma_parser.add_argument("request", nargs="?", help="DMA request")
    dma_parser.add_argument("--list", action="store_true", help="List DMA channels")

    pin_parser = add_subparser("pin", "Pin info")
    pin_parser.add_argument("mcu_name", nargs="?", help="MCU name")
    pin_parser.add_argument("peripheral", nargs="?", help="Peripheral name")
    pin_parser.add_argument("--list", action="store_true", help="List all pins")

    clock_parser = add_subparser("clock", "Clock info")
    clock_parser.add_argument("mcu_name", nargs="?", help="MCU name")

    irq_parser = add_subparser("irq", "Interrupt info")
    irq_parser.add_argument("mcu_name", nargs="?", help="MCU name")
    irq_parser.add_argument("peripheral", nargs="?", help="Peripheral name")
    irq_parser.add_argument("--list", action="store_true", help="List all interrupts")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cache = Cache()
    try:
        _run(args, cache)
    except SystemExit:
        raise
    except Exception as e:
        # FileNotFoundError / XML 解析错误等统一转为结构化 JSON 输出，非零退出
        output_json({"status": "error",
                     "error": {"code": "INTERNAL_ERROR",
                               "message": f"{type(e).__name__}: {e}"}})

if __name__ == "__main__":
    main()
