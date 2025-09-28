import os
from typing import List

from graphviz import Digraph

from domain.models import Signal


def generate_signals_graph(signals: List[Signal], output_path: str = None) -> str:
    """
    Generate a Graphviz diagram from the list of signals and receivers.
    Returns the path to the generated PNG file.
    """
    dot = Digraph(comment="Django Signals Flow", format="png")
    dot.attr(rankdir="LR")
    for s in signals:
        sender_id = f"sender_{s.sender}_{os.path.basename(s.file)}"
        receiver_id = f"receiver_{s.receiver}_{os.path.basename(s.file)}"
        signal_id = f"signal_{s.name}_{s.sender}_{s.receiver}_{os.path.basename(s.file)}"
        sender_label = f"{s.sender}\n({os.path.basename(s.file)})"
        receiver_label = f"{s.receiver}\n({os.path.basename(s.file)})"
        signal_label = s.name
        dot.node(sender_id, sender_label, shape="box", style="filled", fillcolor="#e0f7fa")
        dot.node(receiver_id, receiver_label, shape="ellipse", style="filled", fillcolor="#ffe0b2")
        dot.node(signal_id, signal_label, shape="diamond", style="filled", fillcolor="#c8e6c9")
        dot.edge(sender_id, signal_id, label="send")
        dot.edge(signal_id, receiver_id, label="calls")
    output_file = output_path or "signals_flow_diagram"
    png_path = dot.render(output_file, view=False)
    return png_path


def generate_signals_dot(signals: List[Signal]) -> str:
    """
    Generate a Graphviz DOT string from the list of signals and receivers.
    Returns the DOT source as a string.
    """
    dot = Digraph(comment="Django Signals Flow", format="dot")
    dot.attr(rankdir="LR")
    for s in signals:
        sender_id = f"sender_{s.sender}_{os.path.basename(s.file)}"
        receiver_id = f"receiver_{s.receiver}_{os.path.basename(s.file)}"
        signal_id = f"signal_{s.name}_{s.sender}_{s.receiver}_{os.path.basename(s.file)}"
        sender_label = f"{s.sender}\n({os.path.basename(s.file)})"
        receiver_label = f"{s.receiver}\n({os.path.basename(s.file)})"
        signal_label = s.name
        dot.node(sender_id, sender_label, shape="box", style="filled", fillcolor="#e0f7fa")
        dot.node(receiver_id, receiver_label, shape="ellipse", style="filled", fillcolor="#ffe0b2")
        dot.node(signal_id, signal_label, shape="diamond", style="filled", fillcolor="#c8e6c9")
        dot.edge(sender_id, signal_id, label="send")
        dot.edge(signal_id, receiver_id, label="calls")

    # Use pydot to run Graphviz layout and get node positions
    import pydot

    graphs = pydot.graph_from_dot_data(dot.source)
    if graphs:
        graph = graphs[0]
        # Force layout with dot
        graph.set_prog("dot")
        laid_out_dot = graph.create_dot().decode("utf-8")
        return laid_out_dot
    return dot.source
