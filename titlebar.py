from PyQt5.QtCore import Qt, QPoint

class TitleBarHandler:
  def __init__(self, window):
    self.window = window
    self.old_pos = window.pos()
    self.mouse_pressed = False

    window.minimizeApp.clicked.connect(window.showMinimized)
    window.closeApp.clicked.connect(window.close)

  def mousePressEvent(self, event):
    self.old_pos = event.globalPos()
    self.mouse_pressed = True

  def mouseMoveEvent(self, event):
    if self.mouse_pressed:
      delta = QPoint(event.globalPos() - self.old_pos)
      self.window.move(self.window.x() + delta.x(), self.window.y() + delta.y())
      self.old_pos = event.globalPos()

  def mouseReleaseEvent(self, event):
    self.mouse_pressed = False

class NoteTitleBarHandler:
  def __init__(self, note):
    self.note = note
    self.old_pos = note.pos()
    self.mouse_pressed = False
    self.pinned = False

    note.minimizeNote.clicked.connect(note.showMinimized)
    note.closeNote.clicked.connect(note.close)

  def setPinned(self, v = bool):
    self.pinned = v

  def mousePressEvent(self, event):
    if self.pinned:
      return
    self.old_pos = event.globalPos()
    self.mouse_pressed = True

  def mouseMoveEvent(self, event):
    if self.pinned or not self.mouse_pressed:
      return
    if self.mouse_pressed:
      delta = QPoint(event.globalPos() - self.old_pos)
      self.note.move(self.note.x() + delta.x(), self.note.y() + delta.y())
      self.old_pos = event.globalPos()

  def mouseReleaseEvent(self, event):
    self.mouse_pressed = False
