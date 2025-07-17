from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional
from app.notes import generate_notes
from app.utils import clean_value
import pandas as pd
import os

import shutil
from app.extract import extract_trial_balance_data, analyze_and_save_results
from app.new_main import FlexibleFinancialNoteGenerator  
import json
from app.main16_23 import process_json
from app.json_xlsx import json_to_xlsx
import json as pyjson
from app.utils_normalize import normalize_llm_note_json
router = APIRouter()

def process_uploaded_file(file: UploadFile):
    os.makedirs("input", exist_ok=True)
    file_location = f"input/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    structured_data = extract_trial_balance_data(file_location)
    output_file = "output1/parsed_trial_balance.json"
    analyze_and_save_results(structured_data, output_file)
    # Load DataFrame from the just-created JSON
    with open(output_file, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    tb_df = pd.DataFrame(parsed_data if isinstance(parsed_data, list) else parsed_data.get("trial_balance", parsed_data))
    tb_df['amount'] = tb_df['amount'].apply(clean_value)
    return tb_df

@router.post("/notes/json")
async def post_notes_json(
    file: UploadFile = File(...),
    note_number: Optional[str] = Form(None)  # Comma-separated string, e.g. "13,16"
):
    tb_df = process_uploaded_file(file)
    notes = generate_notes(tb_df)
    # Filter notes if note_number is provided
    if note_number:
        numbers = [n.strip() for n in note_number.split(",")]
        notes = [note for note in notes if any(note['Note'].startswith(f"{n}.") or note['Note'] == n for n in numbers)]
    return JSONResponse({"notes": notes})

@router.post("/notes/text")
async def post_notes_text(
    file: UploadFile = File(...),
    note_number: Optional[str] = Form(None)  # Comma-separated string, e.g. "13,16"
):
    tb_df = process_uploaded_file(file)
    notes = generate_notes(tb_df)
    # Filter notes if note_number is provided
    if note_number:
        numbers = [n.strip() for n in note_number.split(",")]
        notes = [note for note in notes if any(note['Note'].startswith(f"{n}.") or note['Note'] == n for n in numbers)]
    # Build markdown string
    md = "# Notes to Financial Statements for the Year Ended March 31, 2024\n\n"
    for note in notes:
        md += f"## {note['Note']}\n\n{note['Content']}\n\n"
    return PlainTextResponse(md, media_type="text/plain")




@router.post("/llm")
async def llm_generate_and_excel(
    file: UploadFile = File(...),
    note_number: Optional[str] = Form(None)
):
    import os
    import json
    import shutil

    # 1. Save uploaded Excel file
    os.makedirs("input", exist_ok=True)
    file_location = f"input/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Extract trial balance and save as JSON
    structured_data = extract_trial_balance_data(file_location)
    output_json = "output1/parsed_trial_balance.json"
    analyze_and_save_results(structured_data, output_json)

    # 3. Initialize the generator
    try:
        generator = FlexibleFinancialNoteGenerator()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generator init failed: {e}")

    # 4. Generate notes using the extracted JSON
    os.makedirs("generated_notes_excel", exist_ok=True)
    from app.json_xlsx import json_to_xlsx

    if note_number:
        # Generate single note
        success = generator.generate_note(note_number, trial_balance_path=output_json)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to generate note {note_number}. LLM API may be down or unreachable.")
        # Convert generated note JSON to Excel
        json_path = f"generated_notes/notes.json"
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail=f"Generated note file not found: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            note_json = json.load(f)
        if "error" in note_json:
            raise HTTPException(status_code=500, detail=f"LLM failed to generate valid JSON for note {note_number}: {note_json.get('error')}")
        
        # --- Normalize here ---
        normalized_note = normalize_llm_note_json(note_json)
        wrapped = {"notes": [normalized_note]}
        temp_json = f"generated_notes/notes_wrapped.json"
        with open(temp_json, "w", encoding="utf-8") as f2:
            json.dump(wrapped, f2, ensure_ascii=False, indent=2)
        # ----------------------

        excel_path = f"generated_notes_excel/notes.xlsx"
        json_to_xlsx(temp_json, excel_path)
        return {"message": f"Note {note_number} generated. Excel saved at {excel_path}."}
    else:
        # Generate all notes
        results = generator.generate_all_notes(trial_balance_path=output_json)
        if not any(results.values()):
            raise HTTPException(status_code=500, detail="Failed to generate any notes. LLM API may be down or unreachable.")
        # Combine all generated notes into one Excel
        notes = []
        for filename in os.listdir("generated_notes"):
            if filename.endswith(".json"):
                with open(os.path.join("generated_notes", filename), "r", encoding="utf-8") as f:
                    note_json = json.load(f)
                    if "error" not in note_json:
                        notes.append(note_json)
        if not notes:
            raise HTTPException(status_code=404, detail="No valid note JSON files found.")
        

@router.post("/new")
async def run_full_pipeline(
    file: UploadFile = File(...),
    note_number: Optional[str] = Form(None)  # Accepts comma-separated note numbers
):
    import json

    # 1. Save uploaded Excel file
    os.makedirs("input", exist_ok=True)
    file_location = f"input/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Run extract.py logic and save to output1
    os.makedirs("output1", exist_ok=True)
    structured_data = extract_trial_balance_data(file_location)
    output1_json = "output1/parsed_trial_balance.json"
    analyze_and_save_results(structured_data, output1_json)

    # 3. Run main16-23.py logic and save to output2
    os.makedirs("output2", exist_ok=True)
    try:
        from app.main16_23 import process_json
        process_json(output1_json)
    except ImportError:
        raise HTTPException(status_code=500, detail="main16_23.process_json not found. Please ensure 'app/main16_23.py' exists and is named correctly.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"main16_23.process_json failed: {e}")

    # 4. Filter notes if note_number is provided
    notes_json = "output2/notes_output.json"
    with open(notes_json, "r", encoding="utf-8") as f:
        notes_data = json.load(f)

    # If notes_data is a dict with a key (e.g. "notes"), extract the list
    if isinstance(notes_data, dict):
        for key in ["notes", "trial_balance"]:
            if key in notes_data:
                notes_data = notes_data[key]
                break

    # Always wrap as dict for Excel conversion
    def wrap_notes(notes):
        return {"notes": notes}

    # Filter notes if note_number is provided
    if note_number:
        numbers = [n.strip() for n in note_number.split(",")]
        notes_data = [
            note for note in notes_data
            if str(note.get('note_number', '')).strip() in numbers
        ]
        filtered_json = "output2/notes_output_filtered.json"
        with open(filtered_json, "w", encoding="utf-8") as f2:
            json.dump(wrap_notes(notes_data), f2, ensure_ascii=False, indent=2)
        json_input_for_excel = filtered_json
    else:
        temp_json = "output2/notes_output_wrapped.json"
        with open(temp_json, "w", encoding="utf-8") as f2:
            json.dump(wrap_notes(notes_data), f2, ensure_ascii=False, indent=2)
        json_input_for_excel = temp_json

    # 5. Run json-xlsx.py logic and save to output3
    os.makedirs("output3", exist_ok=True)
    try:
        from app.json_xlsx import json_to_xlsx
        output3_xlsx = "output3/final_output.xlsx"
        json_to_xlsx(json_input_for_excel, output3_xlsx)
    except ImportError:
        raise HTTPException(status_code=500, detail="json_xlsx.json_to_xlsx not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"json_xlsx.json_to_xlsx failed: {e}")

    return {"message": "Pipeline completed successfully. Excel file saved in output3."}