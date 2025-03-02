
def run(task, search_func, *args, **kwargs):
    search_results = search_func(task)
    return search_results
