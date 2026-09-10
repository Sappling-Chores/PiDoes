import json
from datetime import datetime, date
import calendar
from pathlib import Path

try:
  from paths import TASK_JSON
except ImportError:
  from APP.paths import TASK_JSON


def get_task_file_path() -> Path:
  if TASK_JSON:
    return Path(TASK_JSON)
  return Path(__file__).parent / "task.json"


def load_task_data() -> dict:
  file_path = get_task_file_path()
  if not file_path.exists():
    default_data = {
      "name": "User",
      "diary": "pi",
      "day_date": {},
      "task": {},
      "incomplete_task": []
    }
    save_task_data(default_data)
    return default_data

  try:
    with open(file_path, "r", encoding="utf-8") as f:
      data = json.load(f)
      if isinstance(data, dict):
        data.setdefault("task", {})
        data.setdefault("incomplete_task", [])
        return data
  except Exception as e:
    print(f"[task_manager] Error loading task.json: {e}")

  return {"task": {}, "incomplete_task": []}


def save_task_data(data: dict) -> bool:
  file_path = get_task_file_path()
  try:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2)
    return True
  except Exception as e:
    print(f"[task_manager] Error saving task.json: {e}")
    return False


def fetch_task() -> dict:
  return load_task_data()


def fetch_tasks_for_view(view_mode: str) -> tuple[str, list[dict]]:
  file_content = load_task_data()
  current_day = datetime.now().strftime("%A")

  if view_mode == "important":
    important_tasks = []
    task_root = file_content.get("task", {})
    if isinstance(task_root, dict):
      for day_key, task_list in task_root.items():
        if isinstance(task_list, list):
          for task in task_list:
            if task.get("priority", False) or task.get("important", False):
              task_copy = dict(task)
              task_copy["_day_key"] = day_key
              important_tasks.append(task_copy)
    return "Important", important_tasks

  elif view_mode in ("old_tasks", "last_week", "older"):
    old_tasks = []
    incomplete = file_content.get("incomplete_task", [])
    now = datetime.now()

    def parse_task_date(date_val):
      if isinstance(date_val, list):
        if len(date_val) == 3 and all(isinstance(x, int) for x in date_val):
          try:
            return datetime(date_val[2], date_val[1], date_val[0])
          except ValueError:
            pass
        if len(date_val) >= 2:
          date_val = date_val[1]
        elif len(date_val) == 1:
          date_val = date_val[0]
        else:
          return None
      if not isinstance(date_val, str):
        return None
      date_val = date_val.strip()
      for fmt in ("%Y-%m-%d", "%d %B, %Y"):
        try:
          return datetime.strptime(date_val, fmt)
        except ValueError:
          pass
      return None

    if isinstance(incomplete, list):
      for idx, item in enumerate(incomplete):
        if isinstance(item, list) and len(item) >= 2:
          task_name = item[0]
          date_val = item[1]
          schedule_str = "  ".join(str(x) for x in date_val) if isinstance(date_val, list) else str(date_val)

          task_dict = {
            "id": idx,
            "task": task_name,
            "done": False,
            "priority": False,
            "important": False,
            "schedule_text_override": schedule_str,
            "_day_key": "incomplete_task",
            "_original_date_val": date_val
          }

          dt = parse_task_date(date_val)
          days_diff = (now - dt).days if dt else 999

          if view_mode == "old_tasks":
            old_tasks.append(task_dict)
          elif view_mode == "last_week" and days_diff <= 7:
            old_tasks.append(task_dict)
          elif view_mode == "older" and days_diff > 7:
            old_tasks.append(task_dict)

    title_map = {
      "old_tasks": "Old Tasks",
      "last_week": "Last Week Tasks",
      "older": "Older Tasks"
    }
    return title_map.get(view_mode, "Old Tasks"), old_tasks

  else:
    task_root = file_content.get("task", {})
    if isinstance(task_root, dict):
      day_tasks = task_root.get(current_day, [])
      if isinstance(day_tasks, list):
        sorted_tasks = sorted(
          day_tasks,
          key=lambda x: not (x.get("priority", False) or x.get("important", False))
        )
        return current_day, sorted_tasks
    return current_day, []


def add_task(task_text: str, selected_date=None, selected_time=None) -> bool:
  text = task_text.strip()
  if not text or text in (".", ","):
    return False

  file_content = load_task_data()
  today_date = date.today()

  if selected_date and len(selected_date) == 3:
    try:
      target_day = date(selected_date[2], selected_date[1], selected_date[0]).strftime("%A")
      date_list = selected_date
    except ValueError:
      target_day = today_date.strftime("%A")
      date_list = [today_date.day, today_date.month, today_date.year]
  else:
    target_day = today_date.strftime("%A")
    date_list = [today_date.day, today_date.month, today_date.year]

  task_root = file_content.setdefault("task", {})
  day_tasks = task_root.setdefault(target_day, [])

  next_id = max((t.get("id", 0) for t in day_tasks), default=0) + 1
  new_task = {
    "id": next_id,
    "task": text,
    "date": date_list,
    "time": selected_time if selected_time else [],
    "created_at": datetime.now().isoformat(timespec="seconds"),
    "done": False,
    "priority": False,
    "important": False,
  }
  day_tasks.append(new_task)
  return save_task_data(file_content)


def update_task_field(day: str, task_id: int, field: str, value) -> bool:
  if task_id is None:
    return False

  file_content = load_task_data()

  if day == "incomplete_task":
    if field == "done" and value:
      incomplete = file_content.get("incomplete_task", [])
      if 0 <= task_id < len(incomplete):
        incomplete.pop(task_id)
        return save_task_data(file_content)
    return False

  task_root = file_content.get("task", {})
  if not isinstance(task_root, dict):
    return False

  found = False
  day_tasks = task_root.get(day, [])
  if isinstance(day_tasks, list):
    for t in day_tasks:
      if t.get("id") == task_id:
        t[field] = value
        if field in ("priority", "important"):
          t["priority"] = value
          t["important"] = value
        found = True
        break

  if not found:
    for d_key, d_tasks in task_root.items():
      if isinstance(d_tasks, list):
        for t in d_tasks:
          if t.get("id") == task_id:
            t[field] = value
            if field in ("priority", "important"):
              t["priority"] = value
              t["important"] = value
            found = True
            break
        if found:
          break

  if found:
    return save_task_data(file_content)
  return False


def remove_task(day: str, task_id: int) -> bool:
  if task_id is None:
    return False

  file_content = load_task_data()

  if day == "incomplete_task":
    incomplete = file_content.get("incomplete_task", [])
    if isinstance(incomplete, list) and 0 <= task_id < len(incomplete):
      incomplete.pop(task_id)
      return save_task_data(file_content)

  task_root = file_content.get("task", {})
  if isinstance(task_root, dict):
    for d_key, day_tasks in task_root.items():
      if isinstance(day_tasks, list):
        file_content["task"][d_key] = [t for t in day_tasks if t.get("id") != task_id]

  return save_task_data(file_content)


def manage_old_task() -> dict:
  task_data = load_task_data()
  date_time = datetime.now()
  day = date_time.strftime("%A")
  date_list = [int(d) for d in date_time.strftime("%d/%m/%Y").split("/")]

  day_date_map = task_data.setdefault("day_date", {})
  if day_date_map.get(day) != date_list:
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day_name in week:
      day_tasks = task_data.get("task", {}).get(day_name, [])
      if isinstance(day_tasks, list):
        for date_task in day_tasks:
          task_date_tuple = date_task.get("date", [1, 1, 2026])
          if len(task_date_tuple) == 3:
            task_date, task_month, task_year = task_date_tuple
            month_name = calendar.month_name[task_month] if 1 <= task_month <= 12 else ""
            date_str = f"{task_date} {month_name}, {task_year}"
          else:
            date_str = str(task_date_tuple)
          task_data.setdefault("incomplete_task", []).append([date_task.get("task", ""), [day_name, date_str]])

    day_date_map[day] = date_list
    save_task_data(task_data)

  return task_data


def manage_task():
  return load_task_data()


if __name__ == "__main__":
  manage_task()
