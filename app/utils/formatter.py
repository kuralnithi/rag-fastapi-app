def format_docs(docs):
    parts = []
    for i, doc in enumerate(docs, 1):
        dl_meta = doc.metadata.get("dl_meta", {})
        headings = dl_meta.get("headings", [])
        source = " > ".join(headings) if headings else "Unknown"

        parts.append(f"[{i}] {source}\n{doc.page_content}")

    return "\n\n---\n\n".join(parts)
