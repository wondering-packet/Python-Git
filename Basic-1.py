with open("tasks.txt", "w") as tasks:
    all_tasks = {}
    n = 1
    while True:
        each_task = {}
        each_task_name = input("Please enter a task: ")
        each_task_day = input(
            "Please enter when you want to finish this task: ")
        each_task["Task Name"] = each_task_name.strip().title()
        each_task["Task Day"] = each_task_day.strip().title()
        all_tasks[f"Task {n}"] = each_task
        print(each_task)
        tasks.write(str(each_task))
        tasks.write("\n")
        more_task = input("Do you want to add more tasks (y/n)? ")
        if more_task.lower().strip() == "n":
            break
        n += 1
    print(all_tasks)
with open("tasks.txt", "r") as tasks:
    print(type(tasks))
    # for each_task in tasks:
    #     print(
    #         f"Task Name: {each_task["Task Name"]} \t Task Day: {each_task["Task Day"]}")
