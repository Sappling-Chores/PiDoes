import json
from datetime import datetime
import calendar

def fetch_task():
  task_file = "task.json"
  with open(task_file, "r") as f:
    data = json.load(f)
    return data

def write_task(task_data):
  with open("task.json", "w") as f:
    json.dump(task_data, f, indent=2)
    
def manage_old_task():
  task_data = fetch_task()
  date_time = datetime.now()
  time = date_time.strftime("%H:%M:%S")
  day = date_time.strftime("%A")
  date = [int(d) for d in date_time.strftime("%D").split("/")]
  print(time, day, date)
  if date != task_data["day_date"][day]:
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # Adding the empty task too 
    for day_list in week:
      for date_task in task_data["task"][day_list]: 
        [task_date, task_month, task_year] = date_task["date"]
        task_data["incomplete_task"].append([date_task["task"], [day_list, f"{task_date} {calendar.month_name[task_month]}, {task_year}"]])
      
    return task_data

def manage_task():
  task_data = fetch_task()
  week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  
  for days in week:
    for tasks in task_data["task"][days]:
      if task_data["task"][days][tasks]["important"] == True:
        
  
  print(type(task_data["task"]["Monday"]))
  
      

          
if __name__=="__main__":  
  # task_data = manage_old_task()
  # write_task(task_data)
  manage_task()
  