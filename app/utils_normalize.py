def normalize_llm_note_json(llm_json):
    note_number = llm_json.get("note_number") or llm_json.get("metadata", {}).get("note_number", "")
    note_title = llm_json.get("note_title") or llm_json.get("title", "")
    full_title = llm_json.get("full_title") or f"{note_number}. {note_title}" if note_number else note_title

    table_data = []
    if "structure" in llm_json and llm_json["structure"]:
        for item in llm_json["structure"]:
            if "subcategories" in item and item["subcategories"]:
                for sub in item["subcategories"]:
                    row = {
                        "particulars": sub.get("label", ""),
                        "current_year": sub.get("value", ""),
                        "previous_year": sub.get("previous_value", ""),
                    }
                    table_data.append(row)
            if "category" in item and ("total" in item or "previous_total" in item):
                row = {
                    "particulars": f"Total {item.get('category', '')}",
                    "current_year": item.get("total", ""),
                    "previous_year": item.get("previous_total", ""),
                }
                table_data.append(row)

    normalized = {
        "note_number": note_number,
        "note_title": note_title,
        "full_title": full_title,
        "table_data": table_data,
        "breakdown": {},
        "matched_accounts": [],
        "total_amount": None,
        "total_amount_lakhs": None,
        "matched_accounts_count": None,
        "comparative_data": {},
        "notes_and_disclosures": [],
        "markdown_content": llm_json.get("markdown_content", ""),
    }
    return normalized