import json

# loading json to maintain data structure.
with open("tasks.txt", "r") as tasks_file:
    all_tasks = json.load(tasks_file)

print("Displaying all existing tasks:\n")

for task_num, task_details in all_tasks.items():
    print(
        f"{task_num} => Task Name: {task_details['Task Name']} | Task Day: {task_details['Task Day']}")

print("\nTask filtering by day:\n")

day_filter = input(
    "Enter the day to filter tasks: ").strip().title()

tasks_filterd = {}
n = 1
found = False       # used to report if no tasks are found.

print(f"\n{day_filter} Tasks:\n")
for task_num, task_details in all_tasks.items():
    if task_details["Task Day"] == day_filter:
        print(
            f"Task {n} => Task Name: {task_details['Task Name']} | Task Day: {task_details['Task Day']}")
        n += 1
        found = True    # setting True means if loop below will not execute.

if not found:
    print(f"No tasks found for {day_filter}")
