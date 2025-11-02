import os
import json

# find path to AppData\Roaming\<YourAppName>\notes.json
APPDATA_DIR = os.getenv("APPDATA")
APP_FOLDER = os.path.join(APPDATA_DIR, "StickyNotesApp")
os.makedirs(APP_FOLDER, exist_ok=True)

JSON_PATH = os.path.join(APP_FOLDER, "notes.json")


def load_data():
  if not os.path.exists(JSON_PATH):
    return {}
  try:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
      return json.load(f)
  except json.JSONDecodeError:
    return {}


def save_data(data):
  with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)


def update_note(note_id, text, colors):
  data = load_data()
  data[note_id] = {
    "text": text,
    "colors": colors
  }
  save_data(data)


def delete_note(note_id):
  data = load_data()
  if note_id in data:
    del data[note_id]
    save_data(data)

def reset_all_data():
  if os.path.exists(JSON_PATH):
    os.remove(JSON_PATH)
