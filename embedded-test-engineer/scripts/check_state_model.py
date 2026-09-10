#!/usr/bin/env python3
"""Lint an explicit finite transition graph; this is not a liveness prover."""

from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
import sys


class ModelError(ValueError):
    """The document does not satisfy this tool's input contract."""


def _object(value, location, required, optional=()):
    if not isinstance(value, dict):
        raise ModelError(f"{location}: expected an object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise ModelError(f"{location}: missing={sorted(missing)}, unknown={sorted(extra)}")


def _text(value, location):
    if not isinstance(value, str) or not value.strip():
        raise ModelError(f"{location}: expected nonempty text")


def validate(model):
    _object(model, "model", ("version", "initial", "states", "transitions"),
            ("description",))
    if type(model["version"]) is not int or model["version"] != 1:
        raise ModelError("version: expected integer 1")
    if "description" in model:
        _text(model["description"], "description")
    _text(model["initial"], "initial")
    states = model["states"]
    if not isinstance(states, dict) or not states:
        raise ModelError("states: expected a nonempty object")
    if len(states) > 1000:
        raise ModelError("states: limit is 1000; reduce or partition the abstraction")
    for name, state in states.items():
        _text(name, "state name")
        _object(state, name, ("kind",), ("timeout", "description", "source_ref"))
        if state["kind"] not in ("stable", "transient", "terminal"):
            raise ModelError(f"{name}.kind: expected stable, transient, or terminal")
        for field in ("description", "source_ref"):
            if field in state:
                _text(state[field], f"{name}.{field}")
        if "timeout" in state:
            if state["kind"] != "transient":
                raise ModelError(f"{name}: timeout is only allowed on transient states")
            timeout = state["timeout"]
            _object(timeout, f"{name}.timeout", ("after_ms", "to"))
            if type(timeout["after_ms"]) is not int or timeout["after_ms"] <= 0:
                raise ModelError(f"{name}.timeout.after_ms: expected a positive integer")
            _text(timeout["to"], f"{name}.timeout.to")
            if timeout["to"] not in states:
                raise ModelError(f"{name}.timeout.to: unknown state {timeout['to']}")
    if model["initial"] not in states:
        raise ModelError("initial: unknown state")
    transitions = model["transitions"]
    if not isinstance(transitions, list) or len(transitions) > 20000:
        raise ModelError("transitions: expected an array with at most 20000 entries")
    seen = set()
    for i, edge in enumerate(transitions):
        loc = f"transitions[{i}]"
        _object(edge, loc, ("from", "event", "to"), ("guard", "source_ref"))
        for key, value in edge.items():
            _text(value, f"{loc}.{key}")
        if edge["from"] not in states or edge["to"] not in states:
            raise ModelError(f"{loc}: unknown source or target")
        if edge["event"] == "@timeout":
            raise ModelError(f"{loc}: @timeout is reserved; use state.timeout")
        pair = (edge["from"], edge["event"])
        if pair in seen:
            raise ModelError(f"{loc}: duplicate source/event; expand guarded branches")
        seen.add(pair)


def _reachable(initial, graph):
    parent = {initial: None}
    pending = deque([initial])
    while pending:
        node = pending.popleft()
        for event, target in graph[node]:
            if target not in parent:
                parent[target] = (node, event)
                pending.append(target)
    return parent


def _witness(target, parent):
    if target not in parent:
        return []
    path = []
    while parent[target] is not None:
        source, event = parent[target]
        path.append({"from": source, "event": event, "to": target})
        target = source
    return list(reversed(path))


def _components(nodes, graph):
    """Iterative Kosaraju: no recursion limit dependence on a long model."""
    adjacency = {n: [t for _, t in graph[n] if t in nodes] for n in nodes}
    reverse = {n: [] for n in nodes}
    for source, targets in adjacency.items():
        for target in targets:
            reverse[target].append(source)
    seen, order = set(), []
    for root in sorted(nodes):
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, iter(adjacency[root]))]
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                order.append(node)
            elif child not in seen:
                seen.add(child)
                stack.append((child, iter(adjacency[child])))
    assigned = set()
    for root in reversed(order):
        if root in assigned:
            continue
        group, stack = [], [root]
        assigned.add(root)
        while stack:
            node = stack.pop()
            group.append(node)
            for other in reverse[node]:
                if other not in assigned:
                    assigned.add(other)
                    stack.append(other)
        yield sorted(group)


def analyze(model):
    validate(model)
    states = model["states"]
    graph = {name: [] for name in states}
    for edge in model["transitions"]:
        graph[edge["from"]].append((edge["event"], edge["to"]))
    for name, state in states.items():
        if "timeout" in state:
            graph[name].append(("@timeout", state["timeout"]["to"]))
    parent = _reachable(model["initial"], graph)
    issues = []

    def issue(level, code, names, message, **extra):
        item = {"level": level, "code": code, "states": names, "message": message,
                "witness": _witness(names[0], parent)}
        item.update(extra)
        issues.append(item)

    for name, state in states.items():
        if name not in parent:
            issue("warning", "UNREACHABLE", [name], "Unreachable in the declared graph.")
        if state["kind"] == "terminal" and graph[name]:
            issue("error", "TERMINAL_OUTGOING", [name],
                  "A request terminal must not transition; model later work separately.")
        if state["kind"] == "transient" and "timeout" not in state:
            issue("error", "MISSING_TIMEOUT", [name],
                  "Transient state has no explicit timeout fallback.")

    boundaries = {n for n, s in states.items() if s["kind"] != "transient"}
    reverse = {n: [] for n in states}
    for source, edges in graph.items():
        for _, target in edges:
            reverse[target].append(source)
    can_exit = set(boundaries)
    pending = deque(sorted(boundaries))
    while pending:
        target = pending.popleft()
        for source in reverse[target]:
            if source not in can_exit:
                can_exit.add(source)
                pending.append(source)
    for name in parent:
        if name not in can_exit:
            issue("error", "NO_BOUNDARY_PATH", [name],
                  "No declared path to a stable or request-terminal boundary.")

    budgets, reported_cycles = {}, set()
    for origin in parent:
        if states[origin]["kind"] != "transient":
            continue
        node, chain, visited, total = origin, [], {}, 0
        while states[node]["kind"] == "transient":
            if node in visited:
                cycle = chain[visited[node]:]
                key = tuple(sorted(cycle))
                if key not in reported_cycles:
                    reported_cycles.add(key)
                    issue("error", "TIMEOUT_CYCLE", [node],
                          "Timeout-only recovery loops without reaching a boundary.",
                          cycle=cycle + [node])
                break
            visited[node] = len(chain)
            chain.append(node)
            timeout = states[node].get("timeout")
            if timeout is None:
                break
            total += timeout["after_ms"]
            node = timeout["to"]
        else:
            budgets[origin] = {"to": node, "declared_wait_ms": total}

    transient = {n for n in parent if states[n]["kind"] == "transient"}
    for group in _components(transient, graph):
        cyclic = len(group) > 1 or any(t == group[0] for _, t in graph[group[0]])
        if cyclic:
            issue("warning", "TRANSIENT_CYCLE", group,
                  "Possible nontermination: expand retry budgets or verify a non-resetting "
                  "operation deadline and its scheduling. Guards are not evaluated.")

    guard_count = sum("guard" in edge for edge in model["transitions"])
    if guard_count:
        issues.append({"level": "warning", "code": "GUARDS_ABSTRACTED", "states": [],
                       "message": f"{guard_count} guard labels ignored; all edges treated as possible.",
                       "witness": []})
    return {
        "status": "fail" if any(i["level"] == "error" for i in issues) else "pass",
        "scope": "Declared graph only; no runtime, guard, scheduling, or hardware proof.",
        "states": len(states), "reachable_states": len(parent), "issues": issues,
        "timeout_chain_budgets": budgets,
        "budget_scope": "Sum of declared waits along timeout-only paths; excludes actions, "
                        "scheduling, and event-driven loops. Not an end-to-end bound.",
    }


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ModelError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit structured output")
    parser.add_argument("--strict", action="store_true",
                        help="Fail the gate on warnings as well as structural errors")
    args = parser.parse_args(argv)
    try:
        raw = args.model.read_text(encoding="utf-8-sig")
        model = json.loads(raw, object_pairs_hook=_unique_object)
        report = analyze(model)
        code = 0 if report["status"] == "pass" else 1
        if args.strict and report["issues"]:
            code = 1
        report["gate_status"] = "pass" if code == 0 else "fail"
        report["warnings_as_errors"] = args.strict
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        report = {"status": "invalid", "error": str(exc)}
        code = 2
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    elif code == 2:
        print(f"INVALID: {report['error']}")
    else:
        print(f"{report['status'].upper()}: {report['reachable_states']}/{report['states']} states reachable")
        print(f"GATE {report['gate_status'].upper()} (warnings_as_errors={args.strict})")
        print(report["scope"])
        for item in report["issues"]:
            print(f"{item['level'].upper()} {item['code']} {item['states']}: {item['message']}")
            if item["witness"]:
                print("  witness: " + " ; ".join(
                    f"{e['from']} --{e['event']}--> {e['to']}" for e in item["witness"]))
            if "cycle" in item:
                print("  cycle: " + " -> ".join(item["cycle"]))
    return code


if __name__ == "__main__":
    sys.exit(main())
