def normalize_llm_note_json(llm_json):
    note_number = llm_json.get("note_number") or llm_json.get("metadata", {}).get("note_number", "")
    note_title = llm_json.get("note_title") or llm_json.get("title", "")
    full_title = llm_json.get("full_title") or f"{note_number}. {note_title}" if note_number else note_title

    table_data = []

    def is_date_label(label):
        import re
        return bool(re.match(r"^(March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}$", label)) \
            or bool(re.match(r"^\d{4}-\d{2}-\d{2}$", label))

    if "structure" in llm_json and llm_json["structure"]:
        for item in llm_json["structure"]:
            if "subcategories" in item and item["subcategories"]:
                for sub in item["subcategories"]:
                    label = sub.get("label", "")
                    if not is_date_label(label):
                        row = {
                            "particulars": label,
                            "current_year": sub.get("value", ""),
                            "previous_year": sub.get("previous_value", "-"),
                        }
                        table_data.append(row)
            if "category" in item and ("total" in item or "previous_total" in item):
                row = {
                    "particulars": f"Total {item.get('category', '')}",
                    "current_year": item.get("total", ""),
                    "previous_year": item.get("previous_total", "-"),
                }
                table_data.append(row)

    # Optionally, add a header row
    if table_data:
        table_data.insert(0, {
            "particulars": "Particulars",
            "current_year": "March 31, 2024",
            "previous_year": "March 31, 2023"
        })

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


def normalize_llm_notes_json(llm_json):
    """
    Accepts {"notes": [ ... ]} and returns {"notes": [ ...normalized... ]}
    """
    notes = llm_json.get("notes", [])
    normalized_notes = [normalize_llm_note_json(note) for note in notes]
    return {"notes": normalized_notes}