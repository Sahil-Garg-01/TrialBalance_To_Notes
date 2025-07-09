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
    import json
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
async def generate_llm_note(
    file: UploadFile = File(...),
    note_number: Optional[str] = Form(None)
):
    
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
    if note_number:
        success = generator.generate_note(note_number, trial_balance_path=output_json)
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to generate note {note_number}. LLM API may be down or unreachable.")
        return JSONResponse({"message": f"Note {note_number} generated successfully."})
    else:
        results = generator.generate_all_notes(trial_balance_path=output_json)
        if not any(results.values()):
            raise HTTPException(status_code=500, detail="Failed to generate any notes. LLM API may be down or unreachable.")
        return JSONResponse({"results": results})