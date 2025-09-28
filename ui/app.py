import sys
from typing import List

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from domain.models import Signal
from ui.widgets.details import SignalDetailsWidget
from ui.widgets.graph_scene import SignalsGraphScene
from ui.widgets.graphics import ZoomableGraphicsView


class SignalsViewerApp:
    """Main application class for Django Signals Explorer UI."""

    def __init__(self, signals: List[Signal]):
        self.signals = signals
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle("Django Signals Explorer")
        self.window.resize(1000, 600)
        self.tree = self._create_tree()
        self.search, self.case_btn, self.word_btn, search_widget = self._create_search_widgets()
        self.graph_view = ZoomableGraphicsView()
        self.graph_scene = SignalsGraphScene(self.signals)
        self.graph_view.setScene(self.graph_scene)
        self.graph_view.setVisible(False)
        self.detail_label = SignalDetailsWidget()
        self.detail_label.setVisible(False)
        self.toggle_button = QPushButton("Show Graph")
        self.toggle_button.clicked.connect(self.toggle_view)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Django Signals Explorer"))
        layout.addWidget(self.toggle_button)
        layout.addWidget(search_widget)
        layout.addWidget(self.tree)
        layout.addWidget(self.graph_view)
        layout.addWidget(self.detail_label)
        container = QWidget()
        container.setLayout(layout)
        self.window.setCentralWidget(container)
        self.is_graph_view = False
        self.populate_tree(self.signals)

    @staticmethod
    def _match(val: str, text: str, case_sensitive: bool, word_match: bool) -> bool:
        cmp_val = val if case_sensitive else val.lower()
        cmp_text = text if case_sensitive else text.lower()
        if word_match:
            return cmp_val == cmp_text
        return cmp_text in cmp_val

    def _create_tree(self) -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderLabels(["Signal", "Sender", "Receiver", "File"])
        return tree

    def _create_search_widgets(self):
        search = QLineEdit()
        search.setPlaceholderText("Search signals, senders, receivers, or files...")
        case_btn = QPushButton("Aa")
        case_btn.setCheckable(True)
        case_btn.setToolTip("Case sensitive search")
        case_btn.setFixedWidth(32)
        word_btn = QPushButton("ab|")
        word_btn.setCheckable(True)
        word_btn.setToolTip("Whole word match")
        word_btn.setFixedWidth(32)
        search_layout = QHBoxLayout()
        search_layout.addWidget(search)
        search_layout.addWidget(case_btn)
        search_layout.addWidget(word_btn)
        search_widget = QWidget()
        search_widget.setLayout(search_layout)
        search.textChanged.connect(self.filter_tree)
        case_btn.clicked.connect(self.filter_tree)
        word_btn.clicked.connect(self.filter_tree)
        return search, case_btn, word_btn, search_widget

    def toggle_view(self):
        if not self.is_graph_view:
            # When switching to graph, filter signals and update graph scene
            filtered_signals = self._get_filtered_signals()
            self.graph_scene.signals = filtered_signals
            self.graph_scene.draw_graph()
            self.graph_view.setVisible(True)
            self.tree.setVisible(False)
            self.search.setVisible(True)
            self.toggle_button.setText("Show Table")
            self.is_graph_view = True
        else:
            self.graph_view.setVisible(False)
            self.tree.setVisible(True)
            self.search.setVisible(True)
            self.toggle_button.setText("Show Graph")
            self.is_graph_view = False
            self.graph_scene.clearSelection()
            self.detail_label.setVisible(False)
            self.populate_tree(self.signals)

    def filter_tree(self, _=None):
        text = self.search.text()
        case_sensitive = self.case_btn.isChecked()
        word_match = self.word_btn.isChecked()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            visible = any(self._match(item.text(col), text, case_sensitive, word_match) for col in range(4))
            item.setHidden(not visible)
        # Update graph scene signals and redraw if in graph view
        if self.is_graph_view:
            filtered_signals = self._get_filtered_signals()
            self.graph_scene.signals = filtered_signals
            self.graph_scene.draw_graph()
        self._filter_graph(text, case_sensitive, word_match)

    def _get_filtered_signals(self):
        text = self.search.text()
        case_sensitive = self.case_btn.isChecked()
        word_match = self.word_btn.isChecked()
        if not text:
            return self.signals
        filtered = []
        for s in self.signals:
            if (
                self._match(s.name, text, case_sensitive, word_match)
                or self._match(s.sender, text, case_sensitive, word_match)
                or self._match(s.receiver, text, case_sensitive, word_match)
                or self._match(s.file, text, case_sensitive, word_match)
            ):
                filtered.append(s)
        return filtered

    def _filter_graph(self, text: str, case_sensitive: bool, word_match: bool):
        if not self.is_graph_view:
            return
        if not text:
            for item in self.graph_scene.items():
                item.setOpacity(1.0)
            return
        matched_senders = set()
        for item in self.graph_scene.items():
            if item.data(0) and item.data(0)[0] == "group_label":
                sender = item.data(0)[1]
                if self._match(sender, text, case_sensitive, word_match):
                    matched_senders.add(sender)
        for item in self.graph_scene.items():
            if item.data(0) and item.data(0)[0] == "group_rect":
                sender = item.data(0)[1]
                item.setOpacity(1.0 if sender in matched_senders else 0.15)
            elif item.data(0) and item.data(0)[0] == "group_label":
                sender = item.data(0)[1]
                item.setOpacity(1.0 if sender in matched_senders else 0.15)
            elif hasattr(item, "boundingRect") and hasattr(item, "pos"):
                in_matched = False
                for group in self.graph_scene.items():
                    if group.data(0) and group.data(0)[0] == "group_rect":
                        sender = group.data(0)[1]
                        if sender in matched_senders:
                            group_rect = group.rect()
                            node_rect = item.mapRectToScene(item.boundingRect())
                            if group_rect.contains(node_rect.center()):
                                in_matched = True
                                break
                item.setOpacity(1.0 if in_matched else 0.15)
            elif hasattr(item, "line"):
                in_matched = False
                for group in self.graph_scene.items():
                    if group.data(0) and group.data(0)[0] == "group_rect":
                        sender = group.data(0)[1]
                        if sender in matched_senders:
                            group_rect = group.rect()
                            line = item.line()
                            if group_rect.contains(line.p1()) and group_rect.contains(line.p2()):
                                in_matched = True
                                break
                item.setOpacity(1.0 if in_matched else 0.15)

    def populate_tree(self, signals: List[Signal]):
        self.tree.clear()
        for s in signals:
            item = QTreeWidgetItem([s.name, s.sender, s.receiver, s.file])
            self.tree.addTopLevelItem(item)
        self.tree.expandAll()
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        self.tree.resizeColumnToContents(2)
        self.tree.resizeColumnToContents(3)

    def draw_graph(self):
        self.graph_scene.draw_graph()
        self.graph_scene.selectionChanged.connect(self.on_node_selected)

    def on_node_selected(self):
        selected = [item for item in getattr(self.graph_scene, "node_items", []) if item.isSelected()]
        if selected:
            node_type, node_value = selected[0].data(0)
            self.detail_label.show_details(node_type, node_value, self.signals)
        else:
            self.detail_label.setVisible(False)

    def run(self) -> int:
        self.window.show()
        return self.app.exec()
