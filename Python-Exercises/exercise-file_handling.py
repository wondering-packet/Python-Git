import json     # need to use json to maintain structured data in this case.


all_tasks = {}      # holds all tasks into a dictionary.
n = 1
while True:
    each_task = {}      # holds only one task into a dictionary.
    each_task_name = input("Please enter a task: ")
    each_task_day = input(
        "Please enter when you want to finish this task: ")
    each_task["Task Name"] = each_task_name.strip().title()
    each_task["Task Day"] = each_task_day.strip().title()
    # inserting each task into the parent all tasks dictionary. each task becomes a value for task {n} key.
    all_tasks[f"Task {n}"] = each_task
    print(each_task)
    # more tasks.
    more_task = input("Do you want to add more tasks (y/n)? ")
    if more_task.lower().strip() == "n":
        break
    n += 1
# print(all_tasks)
print("----------------------------------------------------------------------\n")

with open("tasks.txt", "w") as tasks_file:
    # preserving code structure as a dictionary using json.
    json.dump(all_tasks, tasks_file, indent=4)
with open("tasks.txt", "r") as tasks_file:
    # reading back the data as a dictionary.
    tasks = json.load(tasks_file)
# print(type(tasks))        # <<-- type dictionary. clean structured code.
for task_num, task_detail in tasks.items():
    print(
        f"{task_num} Details: \n\tTask Name: {task_detail["Task Name"]} \n\tTask Day: {task_detail["Task Day"]}")
