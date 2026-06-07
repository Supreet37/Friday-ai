from ddgs import DDGS

def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                output = []
                for i, r in enumerate(results, 1):
                    title = r.get('title', 'No title')
                    body = r.get('body', '')[:200]
                    output.append(f"{i}. {title}\n   {body}")
                return "\n\n".join(output)
            return "No results found."
    except Exception as e:
        return f"Search error: {e}"