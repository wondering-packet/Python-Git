import json     # need to use json to maintain structured data in this case.
import os       # using for path.exists.

# below code block check if the tasts.txt file already exists - meaning we already have some tasks.
# in case it does, we are loading the existing tasks into all_tasks dictionary.
# it's important we use json here to maintain data structure. without json we will end up with
# unstructured data in string format.
if os.path.exists("tasks.txt"):
    with open("tasks.txt", "r") as temp_file:
        all_tasks = json.load(temp_file)
# if file doesn't exist then use an empty dictionary.
else:
    all_tasks = {}
# len(all_tasks) will be the length of the dictionary.
# since we would want to start with n+1 position in case n tasks already exists.
n = len(all_tasks) + 1
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
    # preserving code structure of the dictionary using json.
    json.dump(all_tasks, tasks_file, indent=4)
with open("tasks.txt", "r") as tasks_file:
    # reading back the data of the dictionary.
    tasks = json.load(tasks_file)
# print(type(tasks))        # <<-- type dictionary. clean structured code.
for task_num, task_detail in tasks.items():
    print(
        f"{task_num} Details: \n\tTask Name: {task_detail["Task Name"]} \n\tTask Day: {task_detail["Task Day"]}")
