
def search_topic(topic):
    try:
        search_results = web_search(query=topic)
        return search_results
    except Exception as e:
        return f"Error: {e}"

def run(task, *args, **kwargs):
  topic = task.split("search for: ")[-1]
  return search_topic(topic)

tools = []
