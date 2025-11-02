import sys, os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QIcon, QColor, QTextCursor
from titlebar import TitleBarHandler, NoteTitleBarHandler
from data import update_note, load_data, delete_note, reset_all_data

if getattr(sys, 'frozen', False):
  os.chdir(sys._MEIPASS)

class NoteWindow(QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)
    loadUi("ui/note.ui", self)
    self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    self.setFixedSize(self.size())

    self.textBox.setFixedSize(400, 270)

    self.max_lines = 12 #hard coded the max num of lines because no matter what I did it kept expanding vertically
    self.textBox.installEventFilter(self)

    self.note_id = f"note_{id(self)}" # give this note a unique id
    self.textBox.textChanged.connect(self.save_note) # connect live text saving

    self.color_map = {
      "Peach": ("#fae0ad", "#efd5a5", "#d5be93"),
      "Chestnut": ("#f0adb0", "#e7a7aa", "#d1979a"),
      "Rose": ("#f5c2ab", "#e6b5a1", "#c19787"),
      "PaleGreen": ("#c6d7b2", "#bacaa7", "#a0ad8f"),
      "LightBlue": ("#c4def0", "#b8d1e2", "#a2b7c6"),
    }

    self._color_names = list(self.color_map.keys())
    self._color_idx = 0

    self.clearNote.clicked.connect(self.textBox.clear) #clear note

    self.pickColor.clicked.connect(self._cycle_color)
    self._apply_color(self._color_names[self._color_idx]) #initial apply

    self.pickColor.clicked.connect(self.save_note) #color state save

    self.notebar = NoteTitleBarHandler(self) #dragging logic

    self.pinNote.setCheckable(True) #pinning logic
    self.pinNote.toggled.connect(self.notebar.setPinned)

  def mousePressEvent(self, event):
    self.notebar.mousePressEvent(event)

  def mouseMoveEvent(self, event):
    self.notebar.mouseMoveEvent(event)

  def mouseReleaseEvent(self, event):
    self.notebar.mouseReleaseEvent(event)

  def eventFilter(self, obj, ev):
    if obj is self.textBox and ev.type() == QEvent.KeyPress:
      doc = self.textBox.document()
      blocks = doc.blockCount()

      cursor = self.textBox.textCursor()
      current_line = cursor.block().text()
      current_len = len(current_line)

      # block Enter if above line limit
      if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
        if blocks >= self.max_lines:
          return True 

      if current_len >= 48 and ev.key() not in (
        Qt.Key_Backspace,
        Qt.Key_Delete,
        Qt.Key_Left,
        Qt.Key_Right,
        Qt.Key_Up,
        Qt.Key_Down,
        Qt.Key_Home,
        Qt.Key_End,
      ):
        if blocks < self.max_lines:
          cursor.insertBlock()
        else:
          return True

      if ev.modifiers() == Qt.ControlModifier and ev.key() == Qt.Key_V:
        clip = QtWidgets.QApplication.clipboard().text()
        lines = clip.splitlines()
        add_blocks = len(lines)
        if (blocks + add_blocks) > self.max_lines:
          return True
        trimmed_lines = []
        for i, line in enumerate(lines):
          if len(line) > 48:
            if (blocks + i) < self.max_lines:
              chunks = [line[j:j+48] for j in range(0, len(line), 48)]
              trimmed_lines.extend(chunks[: self.max_lines - (blocks + i)])
            else:
              trimmed_lines.append(line[:48])
          else:
            trimmed_lines.append(line)
          self.textBox.insertPlainText("\n".join(trimmed_lines))
          return True
    return super().eventFilter(obj, ev)

  def _cycle_color(self):
    self._color_idx = (self._color_idx + 1) % len(self._color_names)
    name = self._color_names[self._color_idx]
    self._apply_color(name)

  def _apply_color(self, name: str):
    body_hex, title_hex, hover_hex = self.color_map[name]
    self.noteMainFrame.setStyleSheet(f"background-color: {body_hex};")
    self.noteTitleFrame.setStyleSheet(f"background-color: {title_hex};")
    self.pickColor.setStyleSheet(f"""
      QPushButton {{
        background-color: {title_hex};
        border: none;
      }}
      QPushButton:hover {{
        background-color: {hover_hex};
      }}
      """)
    self.minimizeNote.setStyleSheet(f"""
      QPushButton {{
        background-color: {title_hex};
        border: none;
      }}
      QPushButton:hover {{
        background-color: {hover_hex};
      }}
      """)
    self.closeNote.setStyleSheet(f"""
      QPushButton {{
        background-color: {title_hex};
        border: none;
        border-top-right-radius: 8px;
      }}
      QPushButton:hover {{
        background-color: {hover_hex};
      }}
      """)
    self.pinNote.setStyleSheet(f"""
      QPushButton {{
        background-color: {title_hex};
        border: none;
        border-top-left-radius: 8px;
      }}
      QPushButton:hover {{
        background-color: {hover_hex};
      }}
      """)
    self.clearNote.setStyleSheet(f"""
      QPushButton {{
        background-color: {body_hex};
        border: none;
        border-bottom-right-radius: 8px;
      }}
      QPushButton:hover {{
        background-color: {hover_hex};
      }}
      """)
    self.textBox.setStyleSheet(f"""
      QPlainTextEdit {{
        background-color: {body_hex};
        border: none;
      }}
      """)
    
  def save_note(self):
    text = self.textBox.toPlainText()
    colors = {
      "body": self.color_map[self._color_names[self._color_idx]][0],
      "title_bar": self.color_map[self._color_names[self._color_idx]][1],
      "hover": self.color_map[self._color_names[self._color_idx]][2]
    }
    update_note(self.note_id, text, colors)

    
class Window(QWidget):
  def __init__(self):
    super().__init__()
    loadUi("ui/main.ui", self)
    self.setWindowFlag(Qt.WindowType.FramelessWindowHint) #borderless frame
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) #translucent bg
    self.setFixedSize(self.size())

    self.titlebar = TitleBarHandler(self) #dragging logic
    
    self.newNote.clicked.connect(self.addNote)
    self.notes = [] #for the notes

    self.toggleNote.clicked.connect(self.toggle_notes)
    self.resetAll.clicked.connect(self.reset_all_notes)
    self.notes_visible = False

    self.exitApp.clicked.connect(self.exit_application) #exit app

  def mousePressEvent(self, event):
    self.titlebar.mousePressEvent(event)

  def mouseMoveEvent(self, event):
    self.titlebar.mouseMoveEvent(event)

  def mouseReleaseEvent(self, event):
    self.titlebar.mouseReleaseEvent(event)

  def addNote(self):
    note = NoteWindow()
    note.show()
    self.notes.append(note)

  def reset_all_notes(self):
    for note in self.notes:
      if note.isVisible():
        note.close()
    self.notes.clear()
    self.notes_visible = False

    reset_all_data()

  def exit_application(self):
    for note in self.notes:
      if note.isVisible():
        note.close()
    self.notes.clear()
    self.notes_visible = False
    self.close()
    QApplication.quit()


  def toggle_notes(self):
    if self.notes_visible:
      for note in self.notes:
        if note.isVisible():
          note.close()
      self.notes.clear()
      self.notes_visible = False
      return

    data = load_data()

    for note_id, note_data in data.items():
      text = note_data.get("text", "")
      colors = note_data.get("colors", {})
      if not text.strip():
        continue  

      note = NoteWindow()
      note.note_id = note_id
      note.textBox.setPlainText(text)

      body = colors.get("body")
      title = colors.get("title_bar")
      hover = colors.get("hover")
      if body and title and hover:
        for name, vals in note.color_map.items():
          if vals == (body, title, hover):
            note._apply_color(name)
            note._color_idx = note._color_names.index(name)
            break

      note.show()
      self.notes.append(note)

    self.notes_visible = True


if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = Window()
  window.show()
  sys.exit(app.exec_())