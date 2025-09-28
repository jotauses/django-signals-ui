from typing import List

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPen
from PyQt6.QtWidgets import QGraphicsScene

from domain.models import Signal


class SignalsGraphScene(QGraphicsScene):
    """Custom QGraphicsScene for rendering Django signals graph."""

    def __init__(self, signals: List[Signal], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signals = signals
        self.node_items = []
        self.font = QFont()
        self.font.setPointSize(12)
        self.font.setBold(True)
        self.draw_graph()

    def draw_graph(self):
        self.clear()
        self.node_items = []
        font = self.font
        # Group signals by sender
        grouped = {}
        for s in self.signals:
            grouped.setdefault(s.sender, []).append(s)
        current_y = 100
        for sender, group in grouped.items():
            signals = list({s.name for s in group})
            receivers = list({s.receiver for s in group})
            max_nodes = max(1, len(signals), len(receivers))
            node_vsep = 70
            group_height = max_nodes * node_vsep + 60

            def node_size(name: str, shape: str):
                lines = name.split("\n")
                temp_texts = []
                max_width = 0
                total_height = 0
                for line in lines:
                    text = self.addText(line)
                    text.setFont(font)
                    rect = text.boundingRect()
                    max_width = max(max_width, rect.width())
                    total_height += rect.height()
                    temp_texts.append(text)
                base_pad_x = 20
                base_pad_y = 20
                if shape == "ellipse":
                    pad_x = base_pad_x + 20
                    pad_y = base_pad_y + 10
                    node_width = max(80, max_width + pad_x) * 1.15
                    node_height = max(40, total_height + pad_y)
                else:
                    pad_x = base_pad_x
                    pad_y = base_pad_y
                    node_width = max(80, max_width + pad_x)
                    node_height = max(40, total_height + pad_y)
                for t in temp_texts:
                    self.removeItem(t)
                return node_width, node_height

            sender_width, _ = node_size(sender, "box")
            max_signal_width = max((node_size(sig, "diamond")[0] for sig in signals), default=0)
            max_receiver_width = max((node_size(rec, "ellipse")[0] for rec in receivers), default=0)
            x0 = 100
            x_sender = x0 + sender_width / 2
            x_signal = x_sender + sender_width / 2 + 60 + max_signal_width / 2
            x_receiver = x_signal + max_signal_width / 2 + 60 + max_receiver_width / 2
            # Draw group box
            min_y = current_y
            max_y = current_y + group_height
            group_rect = QRectF(x0 - 60, min_y, (x_receiver + max_receiver_width / 2 + 60) - (x0 - 60), group_height)
            group_box = self.addRect(
                group_rect, QPen(Qt.GlobalColor.darkGray, 2, Qt.PenStyle.DashLine), QBrush(QColor(240, 240, 255, 60))
            )
            group_box.setZValue(0)
            group_box.setData(0, ("group_rect", sender))
            label = self.addText(sender)
            label.setFont(font)
            label.setDefaultTextColor(QColor(80, 100, 180))
            label.setPos(x0 - 50, min_y - 30)
            label.setZValue(1)
            label.setData(0, ("group_label", sender))
            # Draw sender, signal, and receiver nodes
            node_pos = {}
            node_shapes = {}
            # Sender node
            lines = sender.split("\n")
            temp_texts = []
            max_width = 0
            total_height = 0
            for line in lines:
                text = self.addText(line)
                text.setFont(font)
                rect = text.boundingRect()
                max_width = max(max_width, rect.width())
                total_height += rect.height()
                temp_texts.append(text)
            node_width = sender_width
            node_height = max(40, total_height + 20)
            for t in temp_texts:
                self.removeItem(t)
            color = "#e0f7fa"
            item = self.addRect(
                x_sender - node_width / 2,
                current_y + group_height // 2 - node_height / 2,
                node_width,
                node_height,
                QPen(Qt.GlobalColor.black),
                QBrush(QColor(color)),
            )
            item.setData(0, ("sender", sender))
            item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, True)
            item.setZValue(1)
            self.node_items.append(item)
            y_offset = current_y + group_height // 2 - total_height / 2
            for line in lines:
                text = self.addText(line)
                text.setFont(font)
                text.setDefaultTextColor(Qt.GlobalColor.black)
                rect = text.boundingRect()
                text.setPos(x_sender - rect.width() / 2, y_offset)
                text.setZValue(2)
                y_offset += rect.height()
            node_pos[sender] = (x_sender, current_y + group_height // 2)
            node_shapes[sender] = "box"
            # Signal nodes
            for i, sig in enumerate(signals):
                y_sig = current_y + 40 + i * node_vsep
                lines = sig.split("\n")
                temp_texts = []
                max_width = 0
                total_height = 0
                for line in lines:
                    text = self.addText(line)
                    text.setFont(font)
                    rect = text.boundingRect()
                    max_width = max(max_width, rect.width())
                    total_height += rect.height()
                    temp_texts.append(text)
                node_width = max_signal_width
                node_height = max(40, total_height + 20)
                for t in temp_texts:
                    self.removeItem(t)
                from PyQt6.QtCore import QPointF
                from PyQt6.QtGui import QPolygonF

                color = "#c8e6c9"
                points = [
                    QPointF(x_signal, y_sig - node_height / 2),
                    QPointF(x_signal + node_width / 2, y_sig),
                    QPointF(x_signal, y_sig + node_height / 2),
                    QPointF(x_signal - node_width / 2, y_sig),
                ]
                item = self.addPolygon(QPolygonF(points), QPen(Qt.GlobalColor.black), QBrush(QColor(color)))
                item.setData(0, ("signal", sig))
                item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, True)
                item.setZValue(1)
                self.node_items.append(item)
                y_offset = y_sig - total_height / 2
                for line in lines:
                    text = self.addText(line)
                    text.setFont(font)
                    text.setDefaultTextColor(Qt.GlobalColor.black)
                    rect = text.boundingRect()
                    text.setPos(x_signal - rect.width() / 2, y_offset)
                    text.setZValue(2)
                    y_offset += rect.height()
                node_pos[sig] = (x_signal, y_sig)
                node_shapes[sig] = "diamond"
            # Receiver nodes
            for i, rec in enumerate(receivers):
                y_rec = current_y + 40 + i * node_vsep
                lines = rec.split("\n")
                temp_texts = []
                max_width = 0
                total_height = 0
                for line in lines:
                    text = self.addText(line)
                    text.setFont(font)
                    rect = text.boundingRect()
                    max_width = max(max_width, rect.width())
                    total_height += rect.height()
                    temp_texts.append(text)
                node_width = max_receiver_width
                node_height = max(40, total_height + 20)
                for t in temp_texts:
                    self.removeItem(t)
                color = "#ffe0b2"
                item = self.addEllipse(
                    x_receiver - node_width / 2,
                    y_rec - node_height / 2,
                    node_width,
                    node_height,
                    QPen(Qt.GlobalColor.black),
                    QBrush(QColor(color)),
                )
                item.setData(0, ("receiver", rec))
                item.setFlag(item.GraphicsItemFlag.ItemIsSelectable, True)
                item.setZValue(1)
                self.node_items.append(item)
                y_offset = y_rec - total_height / 2
                for line in lines:
                    text = self.addText(line)
                    text.setFont(font)
                    text.setDefaultTextColor(Qt.GlobalColor.black)
                    rect = text.boundingRect()
                    text.setPos(x_receiver - rect.width() / 2, y_offset)
                    text.setZValue(2)
                    y_offset += rect.height()
                node_pos[rec] = (x_receiver, y_rec)
                node_shapes[rec] = "ellipse"
            # Draw edges for this group
            edge_pen = QPen(QColor(120, 160, 255), 2)
            for s in group:
                src = s.sender
                sig = s.name
                rec = s.receiver
                if src in node_pos and sig in node_pos:
                    x1, y1 = node_pos[src]
                    x2, y2 = node_pos[sig]
                    self.addLine(x1, y1, x2, y2, edge_pen)
                if sig in node_pos and rec in node_pos:
                    x1, y1 = node_pos[sig]
                    x2, y2 = node_pos[rec]
                    self.addLine(x1, y1, x2, y2, edge_pen)
            # Next group y
            current_y += group_height + 60
