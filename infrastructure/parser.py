import ast
import os
from typing import List

from domain.models import Signal


def parse_signals(project_root: str) -> List[Signal]:
    """
    Recursively parses Python files in the given project root to extract Django signal receivers.
    Returns a list of Signal domain objects.
    """
    signals = []
    for dirpath, _, filenames in os.walk(project_root):
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    tree = ast.parse(file.read(), filename=filename)
            except Exception:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                for deco in node.decorator_list:
                    if not (isinstance(deco, ast.Call) and getattr(deco.func, "id", "") == "receiver"):
                        continue
                    signal = None
                    sender = None
                    if deco.args:
                        signal = getattr(deco.args[0], "id", None)
                    for kw in deco.keywords:
                        if kw.arg == "sender":
                            sender = getattr(kw.value, "id", None)
                            if sender is None and hasattr(kw.value, "attr"):
                                sender = kw.value.attr
                    if signal and sender:
                        signals.append(Signal(signal, sender, node.name, filepath))
    return signals
