from typing import List

from PyQt6.QtWidgets import QLabel

from domain.models import Signal


class SignalDetailsWidget(QLabel):
    """Widget to display details of a selected signal, sender, or receiver."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setVisible(False)

    def show_details(self, node_type: str, node_value: str, signals: List[Signal]):
        sender_group = None
        for s in signals:
            if node_type == "sender" and s.sender == node_value:
                sender_group = s.sender
                break
            elif node_type == "signal" and s.name == node_value:
                sender_group = s.sender
                break
            elif node_type == "receiver" and s.receiver == node_value:
                sender_group = s.sender
                break
        group_signals = [s for s in signals if s.sender == sender_group] if sender_group else signals
        if node_type == "signal":
            details = f"<b>Signal:</b> {node_value}<br>"
            related = [s for s in group_signals if s.name == node_value]
            details += f"<b>Senders:</b> {', '.join(set(s.sender for s in related))}<br>"
            details += f"<b>Receivers:</b> {', '.join(set(s.receiver for s in related))}"
        elif node_type == "sender":
            details = f"<b>Sender:</b> {node_value}<br>"
            related = [s for s in group_signals if s.sender == node_value]
            details += f"<b>Signals:</b> {', '.join(set(s.name for s in related))}<br>"
            details += f"<b>Receivers:</b> {', '.join(set(s.receiver for s in related))}"
        elif node_type == "receiver":
            details = f"<b>Receiver:</b> {node_value}<br>"
            related = [s for s in group_signals if s.receiver == node_value]
            details += f"<b>Signals:</b> {', '.join(set(s.name for s in related))}<br>"
            details += f"<b>Senders:</b> {', '.join(set(s.sender for s in related))}"
        else:
            details = ""
        self.setText(details)
        self.setVisible(True if details else False)
