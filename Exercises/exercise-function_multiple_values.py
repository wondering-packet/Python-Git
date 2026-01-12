def student_stats(result):  # list
    return (min(result), max(result), sum(result)/len(result))


stat_values = [8, 7, 10]
# since we are passing a list as the argument, the parameter becomes a list.
print(student_stats(stat_values))


def student_stats(result):  # string
    return result


stat_values = "excellent"
# since we are passing a string as the argument, the paramter becomes a string. interesting.
print(student_stats(stat_values))
