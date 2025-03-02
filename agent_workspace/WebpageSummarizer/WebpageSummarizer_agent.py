
def visit_webpage(url):
    try:
        import urllib.request
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error fetching the webpage: {e}"

def summarize_webpage(url):
    try:
        webpage_content = visit_webpage(url=url)
        summary = webpage_content[:500] + "..." # Basic summarization (first 500 chars)
        return summary
    except Exception as e:
        return f"Error: {e}"

def run(task, *args, **kwargs):
  url = task.split("webpage: ")[-1]
  return summarize_webpage(url)

tools = []
