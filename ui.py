"""Bilingual PySide6 interface with light and dark themes."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QDialog, QFileDialog, QFrame, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from file_scanner import scan_media
from history_db import (
    clear_last_history, history_is_undoable, initialize_database,
    load_last_history, load_preferences, save_last_history, save_preferences,
)
from rename_logic import RenameOperation, build_rename_plan, execute_rename, undo_rename

PATH_ROLE = Qt.ItemDataRole.UserRole

TEXT = {
    "en": {
        "window": "Jellyfin Batch Renamer", "title": "Jellyfin Library Organizer",
        "subtitle": "Match video and subtitle files, preview, then rename safely.",
        "language": "العربية", "theme_dark": "Dark mode", "theme_light": "Light mode",
        "choose": "Choose folder", "refresh": "Refresh", "recursive": "Search subfolders",
        "no_folder": "No folder selected", "videos": "Video files", "subtitles": "Subtitle files",
        "count": "{n} files", "season": "Season", "season_hint": "e.g. S02 or season 2",
        "series": "Series name (optional)", "series_hint": "e.g. The Expanse",
        "undo": "Undo last rename", "rename": "Rename files", "folder_dialog": "Choose series folder",
        "scan_error": "Could not scan folder", "no_files_title": "No files",
        "no_files": "Choose a folder containing video or subtitle files first.",
        "mismatch_title": "File counts do not match",
        "mismatch": "Videos: {v}\nSubtitles: {s}\n\nFiles will be matched by position. Extra items will be renamed without a matching file. Continue?",
        "check": "Check your input", "preview_window": "Preview changes",
        "preview_title": "Review names before renaming", "preview_note": "{n} files will be renamed. Files will not be moved.",
        "type": "Type", "old": "Old name", "new": "New name", "cancel": "Cancel",
        "confirm": "Confirm and rename", "video": "Video", "subtitle": "Subtitle",
        "success": "Success", "success_msg": "Successfully renamed {n} files.",
        "error": "An error occurred", "undo_title": "Confirm undo",
        "undo_question": "Restore all files from the last operation to their previous names?",
        "undo_done": "Undo complete", "undo_done_msg": "Files were restored to their previous names.",
        "undo_error": "Could not undo",
    },
    "ar": {
        "window": "إعادة تسمية ملفات Jellyfin", "title": "منظّم مكتبة Jellyfin",
        "subtitle": "طابق الفيديو والترجمة، راجع النتيجة، ثم غيّر الأسماء بأمان.",
        "language": "English", "theme_dark": "الوضع الليلي", "theme_light": "الوضع النهاري",
        "choose": "اختيار المجلد", "refresh": "تحديث", "recursive": "البحث في المجلدات الفرعية",
        "no_folder": "لم يتم اختيار مجلد بعد", "videos": "ملفات الفيديو", "subtitles": "ملفات الترجمة",
        "count": "{n} ملف", "season": "الموسم", "season_hint": "مثال: S02 أو season 2",
        "series": "اسم المسلسل (اختياري)", "series_hint": "مثال: The Expanse",
        "undo": "تراجع عن آخر عملية", "rename": "تغيير الأسماء", "folder_dialog": "اختر مجلد المسلسل",
        "scan_error": "تعذر فحص المجلد", "no_files_title": "لا توجد ملفات",
        "no_files": "اختر مجلدًا يحتوي على فيديو أو ترجمة أولًا.",
        "mismatch_title": "العدد غير متطابق",
        "mismatch": "عدد الفيديو: {v}\nعدد الترجمة: {s}\n\nستتم المطابقة حسب الموضع، وستُعاد تسمية العناصر الزائدة دون مقابل. هل تريد المتابعة؟",
        "check": "تحقق من البيانات", "preview_window": "معاينة التغييرات",
        "preview_title": "راجع الأسماء قبل التنفيذ", "preview_note": "سيتم تغيير {n} ملف. لن يتم نقل الملفات.",
        "type": "النوع", "old": "الاسم القديم", "new": "الاسم الجديد", "cancel": "إلغاء",
        "confirm": "تأكيد وإعادة التسمية", "video": "فيديو", "subtitle": "ترجمة",
        "success": "تم بنجاح", "success_msg": "تمت إعادة تسمية {n} ملف بنجاح.",
        "error": "حدث خطأ", "undo_title": "تأكيد التراجع",
        "undo_question": "هل تريد إعادة جميع ملفات آخر عملية إلى أسمائها السابقة؟",
        "undo_done": "تم التراجع", "undo_done_msg": "عادت الملفات إلى أسمائها السابقة.",
        "undo_error": "تعذر التراجع",
    },
}


def make_style(dark: bool) -> str:
    """Return a compact light or dark stylesheet."""
    if dark:
        c = dict(canvas="#08111F", surface="#101C2E", raised="#17263B", hover="#20344D", text="#EAF2FF",
                 muted="#9DB0CB", border="#2B405D", accent="#27C7B8",
                 accent_hover="#20AFA3", selected="#173E4A", warning="#C7A6FF", warning_bg="#251D3D")
    else:
        c = dict(canvas="#F6F7FB", surface="#FFFFFF", raised="#F9FAFB", hover="#F2F4F7", text="#20232A",
                 muted="#667085", border="#DDE1E7", accent="#2783DE", accent_hover="#1F72C5",
                 selected="#E5F2FC", warning="#B54708", warning_bg="#FFF7ED")
    return f"""
QWidget {{ color: {c['text']}; font-family: "Noto Sans Arabic", "Segoe UI", Arial; font-size: 12px; }}
QMainWindow {{ background: transparent; }}
QDialog {{ background: {c['canvas']}; }}
QWidget#appShell {{ background: {c['canvas']}; border: 1px solid {c['border']}; border-radius: 16px; }}
QFrame#card {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 11px; }}
QFrame#titleBar {{ background: transparent; border: 0; border-radius: 12px; }}
QLabel#title {{ color: {c['text']}; font-size: 21px; font-weight: 700; }}
QLabel#subtitle {{ color: {c['muted']}; }}
QLabel#sectionTitle {{ color: {c['text']}; font-size: 13px; font-weight: 700; }}
QLabel#counter {{ color: {c['muted']}; background: {c['raised']}; border-radius: 7px; padding: 3px 8px; }}
QLineEdit {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 7px; padding: 7px 9px; selection-background-color: {c['accent']}; }}
QLineEdit:focus {{ border: 2px solid {c['accent']}; padding: 6px 8px; }}
QListWidget, QTableWidget {{ background: {c['surface']}; border: 1px solid {c['border']}; border-radius: 7px; outline: none; alternate-background-color: {c['raised']}; }}
QListWidget::item {{ padding: 7px; border-bottom: 1px solid {c['border']}; }}
QListWidget::item:selected {{ background: {c['selected']}; color: {c['text']}; }}
QPushButton {{ min-height: 34px; border: 1px solid {c['border']}; border-radius: 7px; padding: 0 12px; background: {c['surface']}; color: {c['text']}; font-weight: 600; }}
QPushButton:hover {{ background: {c['hover']}; }}
QPushButton#windowButton, QPushButton#closeButton {{ min-width: 36px; max-width: 36px; min-height: 30px; max-height: 30px; padding: 0; border: 0; border-radius: 6px; background: transparent; color: {c['muted']}; font-size: 15px; font-weight: 500; }}
QPushButton#windowButton:hover {{ color: {c['text']}; background: {c['hover']}; }}
QPushButton#closeButton:hover {{ color: white; background: #E5484D; }}
QPushButton#primary {{ color: white; background: {c['accent']}; border-color: {c['accent']}; min-height: 42px; font-size: 14px; }}
QPushButton#primary:hover {{ background: {c['accent_hover']}; }}
QPushButton#undo {{ color: {c['warning']}; background: {c['warning_bg']}; }}
QPushButton:disabled {{ color: {c['muted']}; background: {c['raised']}; }}
QCheckBox {{ spacing: 7px; color: {c['muted']}; }}
QHeaderView::section {{ background: {c['raised']}; color: {c['muted']}; border: 0; border-bottom: 1px solid {c['border']}; padding: 7px; font-weight: 700; }}
QToolTip {{ background: {c['surface']}; color: {c['text']}; border: 1px solid {c['border']}; }}
"""


class TitleBar(QFrame):
    """Frameless in-app title bar with drag and window controls."""

    def __init__(self, window: QMainWindow) -> None:
        super().__init__(window)
        self.host_window = window
        self.drag_offset = None
        self.setObjectName("titleBar")
        self.setFixedHeight(58)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 5, 6, 5)
        layout.setSpacing(4)
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout, 1)

        self.minimize_button = QPushButton("−")
        self.minimize_button.setObjectName("windowButton")
        self.minimize_button.setToolTip("Minimize")
        self.minimize_button.clicked.connect(window.showMinimized)

        self.maximize_button = QPushButton("□")
        self.maximize_button.setObjectName("windowButton")
        self.maximize_button.setToolTip("Maximize / Restore")
        self.maximize_button.clicked.connect(self.toggle_maximize)

        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(window.close)

        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

    def toggle_maximize(self) -> None:
        """Toggle between maximized and normal window states."""
        if self.host_window.isMaximized():
            self.host_window.showNormal()
            self.maximize_button.setText("□")
        else:
            self.host_window.showMaximized()
            self.maximize_button.setText("❐")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Remember the pointer offset when title-bar dragging starts."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.host_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Move a normal window while the title bar is dragged."""
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            if not self.host_window.isMaximized():
                self.host_window.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Finish title-bar dragging."""
        self.drag_offset = None
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Maximize or restore on a title-bar double-click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()
            event.accept()


class MediaList(QListWidget):
    """Reorderable list retaining each absolute path in UserRole."""
    def __init__(self) -> None:
        super().__init__()
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)

    def set_paths(self, paths: list[Path]) -> None:
        """Display filenames while storing full paths."""
        self.clear()
        for path in paths:
            item = QListWidgetItem(path.name)
            item.setData(PATH_ROLE, str(path))
            item.setToolTip(str(path.parent))
            self.addItem(item)

    def paths(self) -> list[Path]:
        """Return paths in visible order."""
        return [Path(self.item(i).data(PATH_ROLE)) for i in range(self.count())]


class PreviewDialog(QDialog):
    """Localized confirmation table for a rename plan."""
    def __init__(self, plan: list[RenameOperation], language: str, dark: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        t = TEXT[language]
        self.setWindowTitle(t["preview_window"])
        self.setMinimumSize(700, 440)
        self.resize(760, 480)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if language == "ar" else Qt.LayoutDirection.LeftToRight)
        self.setStyleSheet(make_style(dark))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(11)
        title = QLabel(t["preview_title"])
        title.setObjectName("title")
        title.setFont(QFont(title.font().family(), 16, QFont.Weight.Bold))
        layout.addWidget(title)
        changed = sum(op.old_path != op.new_path for op in plan)
        note = QLabel(t["preview_note"].format(n=changed))
        note.setObjectName("subtitle")
        layout.addWidget(note)
        table = QTableWidget(len(plan), 3)
        table.setHorizontalHeaderLabels([t["type"], t["old"], t["new"]])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for row, op in enumerate(plan):
            kind = t["video"] if op.kind == "فيديو" else t["subtitle"]
            table.setItem(row, 0, QTableWidgetItem(kind))
            table.setItem(row, 1, QTableWidgetItem(op.old_path.name))
            table.setItem(row, 2, QTableWidgetItem(op.new_path.name))
            table.item(row, 1).setToolTip(str(op.old_path))
            table.item(row, 2).setToolTip(str(op.new_path))
        layout.addWidget(table, 1)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton(t["cancel"])
        confirm = QPushButton(t["confirm"])
        confirm.setObjectName("primary")
        cancel.clicked.connect(self.reject)
        confirm.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        layout.addLayout(buttons)


class MainWindow(QMainWindow):
    """Main bilingual application window."""
    def __init__(self) -> None:
        super().__init__()
        self.folder: Path | None = None
        initialize_database()
        loaded_history = load_last_history()
        if history_is_undoable(loaded_history):
            self.last_history = loaded_history
        else:
            self.last_history = []
            clear_last_history()
        # English/light are used only on first launch; later launches restore preferences.
        self.language, self.dark_mode = load_preferences()
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(840, 580)
        self.resize(960, 650)
        self._build_ui()
        self.undo_button.setEnabled(bool(self.last_history))
        self._apply_language()
        self._apply_theme()

    def _build_ui(self) -> None:
        """Construct the compact interface and keep text-bearing widgets as attributes."""
        root = QWidget()
        root.setObjectName("appShell")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(10, 8, 10, 10)
        outer.setSpacing(10)

        self.title_bar = TitleBar(self)
        headings = QVBoxLayout()
        headings.setSpacing(0)
        self.title_label = QLabel(objectName="title")
        self.subtitle_label = QLabel(objectName="subtitle")
        headings.addWidget(self.title_label)
        headings.addWidget(self.subtitle_label)
        self.title_bar.content_layout.addLayout(headings, 1)
        self.language_button = QPushButton()
        self.language_button.clicked.connect(self.toggle_language)
        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.title_bar.content_layout.addWidget(self.language_button)
        self.title_bar.content_layout.addWidget(self.theme_button)
        outer.addWidget(self.title_bar)

        folder_card = QFrame(objectName="card")
        folder_layout = QHBoxLayout(folder_card)
        folder_layout.setContentsMargins(12, 10, 12, 10)
        folder_layout.setSpacing(8)
        self.choose_button = QPushButton()
        self.choose_button.clicked.connect(self.choose_folder)
        self.refresh_button = QPushButton()
        self.refresh_button.setEnabled(False)
        self.refresh_button.clicked.connect(self.refresh_files)
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.recursive = QCheckBox()
        self.recursive.toggled.connect(self._recursive_changed)
        folder_layout.addWidget(self.choose_button)
        folder_layout.addWidget(self.refresh_button)
        folder_layout.addWidget(self.folder_edit, 1)
        folder_layout.addWidget(self.recursive)
        outer.addWidget(folder_card)

        lists = QHBoxLayout()
        lists.setSpacing(12)
        self.video_list, self.video_title, self.video_count = self._make_list_card(lists)
        self.subtitle_list, self.subtitle_title, self.subtitle_count = self._make_list_card(lists)
        outer.addLayout(lists, 1)

        settings = QFrame(objectName="card")
        settings_layout = QHBoxLayout(settings)
        settings_layout.setContentsMargins(12, 10, 12, 10)
        settings_layout.setSpacing(9)
        self.season_label = QLabel(objectName="sectionTitle")
        self.season_edit = QLineEdit()
        self.season_edit.setMaximumWidth(190)
        self.series_label = QLabel(objectName="sectionTitle")
        self.series_edit = QLineEdit()
        settings_layout.addWidget(self.season_label)
        settings_layout.addWidget(self.season_edit)
        settings_layout.addWidget(self.series_label)
        settings_layout.addWidget(self.series_edit, 1)
        outer.addWidget(settings)

        actions = QHBoxLayout()
        self.undo_button = QPushButton(objectName="undo")
        self.undo_button.setEnabled(False)
        self.undo_button.clicked.connect(self.undo_last)
        self.rename_button = QPushButton(objectName="primary")
        self.rename_button.clicked.connect(self.rename_files)
        actions.addWidget(self.undo_button)
        actions.addStretch()
        actions.addWidget(self.rename_button)
        outer.addLayout(actions)

    def _make_list_card(self, parent: QHBoxLayout) -> tuple[MediaList, QLabel, QLabel]:
        """Create a compact media-list card."""
        card = QFrame(objectName="card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 12)
        header = QHBoxLayout()
        title = QLabel(objectName="sectionTitle")
        count = QLabel(objectName="counter")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(count)
        media_list = MediaList()
        layout.addLayout(header)
        layout.addWidget(media_list)
        parent.addWidget(card, 1)
        return media_list, title, count

    def _apply_language(self) -> None:
        """Refresh all visible labels and switch layout direction."""
        t = TEXT[self.language]
        self.setWindowTitle(t["window"])
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.language == "ar" else Qt.LayoutDirection.LeftToRight)
        self.title_label.setText(t["title"])
        self.subtitle_label.setText(t["subtitle"])
        self.language_button.setText(t["language"])
        self.theme_button.setText(t["theme_light"] if self.dark_mode else t["theme_dark"])
        self.choose_button.setText(t["choose"])
        self.refresh_button.setText(t["refresh"])
        self.recursive.setText(t["recursive"])
        self.folder_edit.setPlaceholderText(t["no_folder"])
        self.video_title.setText(t["videos"])
        self.subtitle_title.setText(t["subtitles"])
        self.season_label.setText(t["season"])
        self.season_edit.setPlaceholderText(t["season_hint"])
        self.series_label.setText(t["series"])
        self.series_edit.setPlaceholderText(t["series_hint"])
        self.undo_button.setText(t["undo"])
        self.rename_button.setText(t["rename"])
        self._update_counts()

    def _apply_theme(self) -> None:
        """Apply the selected color theme and update the toggle label."""
        self.setStyleSheet(make_style(self.dark_mode))
        t = TEXT[self.language]
        self.theme_button.setText(t["theme_light"] if self.dark_mode else t["theme_dark"])

    def _update_counts(self) -> None:
        """Update localized list counters."""
        pattern = TEXT[self.language]["count"]
        self.video_count.setText(pattern.format(n=self.video_list.count()))
        self.subtitle_count.setText(pattern.format(n=self.subtitle_list.count()))

    def toggle_language(self) -> None:
        """Switch language instantly and persist the selection."""
        self.language = "ar" if self.language == "en" else "en"
        self._apply_language()
        save_preferences(self.language, self.dark_mode)

    def toggle_theme(self) -> None:
        """Switch theme instantly and persist the selection."""
        self.dark_mode = not self.dark_mode
        self._apply_theme()
        save_preferences(self.language, self.dark_mode)

    def choose_folder(self) -> None:
        """Select and scan a series folder."""
        selected = QFileDialog.getExistingDirectory(self, TEXT[self.language]["folder_dialog"], str(self.folder or Path.home()))
        if selected:
            self.folder = Path(selected).resolve()
            self.folder_edit.setText(str(self.folder))
            self.refresh_button.setEnabled(True)
            self.refresh_files()

    def _recursive_changed(self, _checked: bool) -> None:
        """Rescan automatically when recursive mode changes."""
        if self.folder:
            self.refresh_files()

    def refresh_files(self) -> None:
        """Rescan and naturally sort media files."""
        if not self.folder:
            return
        try:
            videos, subtitles = scan_media(self.folder, self.recursive.isChecked())
            self.video_list.set_paths(videos)
            self.subtitle_list.set_paths(subtitles)
            self._update_counts()
        except Exception as exc:
            QMessageBox.critical(self, TEXT[self.language]["scan_error"], str(exc))

    def rename_files(self) -> None:
        """Validate, preview, and execute a confirmed rename batch."""
        t = TEXT[self.language]
        videos, subtitles = self.video_list.paths(), self.subtitle_list.paths()
        if not videos and not subtitles:
            QMessageBox.warning(self, t["no_files_title"], t["no_files"])
            return
        if len(videos) != len(subtitles):
            answer = QMessageBox.warning(self, t["mismatch_title"], t["mismatch"].format(v=len(videos), s=len(subtitles)),
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            plan = build_rename_plan(videos, subtitles, self.season_edit.text(), self.series_edit.text())
        except Exception as exc:
            QMessageBox.warning(self, t["check"], str(exc))
            return
        if PreviewDialog(plan, self.language, self.dark_mode, self).exec() != QDialog.DialogCode.Accepted:
            return
        try:
            new_history = execute_rename(plan)
            if new_history:
                self.last_history = new_history
                save_last_history(self.last_history)
                self.undo_button.setEnabled(True)
            QMessageBox.information(self, t["success"], t["success_msg"].format(n=len(new_history)))
            self.refresh_files()
        except Exception as exc:
            QMessageBox.critical(self, t["error"], str(exc))

    def undo_last(self) -> None:
        """Restore paths from the most recent operation."""
        if not self.last_history:
            return
        t = TEXT[self.language]
        answer = QMessageBox.question(self, t["undo_title"], t["undo_question"],
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                      QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            undo_rename(self.last_history)
            clear_last_history()
            self.last_history = []
            self.undo_button.setEnabled(False)
            QMessageBox.information(self, t["undo_done"], t["undo_done_msg"])
            self.refresh_files()
        except Exception as exc:
            QMessageBox.critical(self, t["undo_error"], str(exc))
