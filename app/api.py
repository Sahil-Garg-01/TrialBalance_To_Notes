from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional
from app.notes import generate_notes
from app.utils import clean_value
import pandas as pd
import os
from app.pnl import generate_pnl_report
import shutil
from app.extract import extract_trial_balance_data, analyze_and_save_results
from app.new_main import FlexibleFinancialNoteGenerator  
import json
from app.main16_23 import process_json
from app.json_xlsx import json_to_xlsx
import json as pyjson
from app.utils_normalize import normalize_llm_note_json
from app.bs import generate_balance_sheet_report
from app.cashflow import generate_cashflow_report
import subprocess


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

@router.post("/cf")
async def generate_cashflow():
    try:
        generate_cashflow_report()
        return {"message": "Cash Flow report generated successfully as 'cashflow_excel/cashflow_report.xlsx'."}
    except Exception as e:
        return {"error": f"Failed to generate Cash Flow report: {str(e)}"}
    

@router.post("/bs")
async def generate_balancesheet():
    """
    Generates the Balance Sheet Excel file from the notes in generated_notes/notes.json.
    Returns a message with the output file location.
    """
    try:
        generate_balance_sheet_report()
        return {"message": "Balance Sheet report generated successfully as 'balance_sheet_report.xlsx'."}
    except Exception as e:
        return {"error": f"Failed to generate Balance Sheet: {str(e)}"}

@router.post("/pnl")
async def generate_pnl():
    
    try:
        generate_pnl_report()
        return {"message": "P&L report generated successfully as 'pnl_report.xlsx'."}
    except Exception as e:
        return {"error": f"Failed to generate P&L report: {str(e)}"}
    
    
@router.post("/new")
async def llm_generate_and_excel(
    file: UploadFile = File(...),
    note_number: Optional[str] = Form(None)
):
    import os
    import json
    import shutil
    from app.utils_normalize import normalize_llm_note_json, normalize_llm_notes_json

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

    wrapped_json_path = "generated_notes/notes_wrapped.json"

    if note_number:
        # Support multiple note numbers (comma-separated)
        note_numbers = [n.strip() for n in note_number.split(",")]
        all_notes = []
        for n in note_numbers:
            success = generator.generate_note(n, trial_balance_path=output_json)
            if success:
                # Read the just-generated note
                with open("generated_notes/notes.json", "r", encoding="utf-8") as f:
                    note_json = json.load(f)
                all_notes.append(note_json)
        # Now write all notes together
        with open("generated_notes/notes.json", "w", encoding="utf-8") as f:
            json.dump({"notes": all_notes}, f, indent=2, ensure_ascii=False)
        # --- Normalize all notes ---
        wrapped = normalize_llm_notes_json({"notes": all_notes})
        with open(wrapped_json_path, "w", encoding="utf-8") as f2:
            json.dump(wrapped, f2, ensure_ascii=False, indent=2)
        # --------------------------
        excel_path = f"generated_notes_excel/notes.xlsx"
        json_to_xlsx(wrapped_json_path, excel_path)
        return {"message": f"Notes {', '.join(note_numbers)} generated. Excel saved at {excel_path}."}
    else:
        # Generate all notes
        results = generator.generate_all_notes(trial_balance_path=output_json)
        if not any(results.values()):
            raise HTTPException(status_code=500, detail="Failed to generate any notes. LLM API may be down or unreachable.")
        # Read all notes.json
        with open("generated_notes/notes.json", "r", encoding="utf-8") as f:
            notes_json = json.load(f)
        # --- Normalize all notes ---
        wrapped = normalize_llm_notes_json(notes_json)
        with open(wrapped_json_path, "w", encoding="utf-8") as f2:
            json.dump(wrapped, f2, ensure_ascii=False, indent=2)
        # --------------------------
        excel_path = f"generated_notes_excel/notes.xlsx"
        json_to_xlsx(wrapped_json_path, excel_path)
        return {"message": f"All notes generated. Excel saved at {excel_path}."}
        


@router.post("/hardcoded")
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



@router.post("/bs_from_notes")
async def bs_from_notes(file: UploadFile = File(...)):
    """
    Accepts an Excel file, runs the full pipeline (sircode.py -> csv_json.py -> bl_llm.py),
    and returns the path to the generated balance sheet Excel file.
    """
    import os

    # 1. Save uploaded Excel file
    os.makedirs("input", exist_ok=True)
    input_excel_path = os.path.join("input", file.filename)
    with open(input_excel_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"[DEBUG] Uploaded Excel saved to: {input_excel_path}")
    print(f"[DEBUG] Files in input/: {os.listdir('input')}")

    # Prepare environment for subprocesses
    env = os.environ.copy()
    if os.getenv("OPENROUTER_API_KEY"):
        env["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
    env["INPUT_FILE"] = "clean_financial_data.json"

    # 2. Run sircode.py with the uploaded Excel file
    try:
        print("[DEBUG] Running sircode.py...")
        result1 = subprocess.run(
            ["python", "pnlbs/sircode.py", input_excel_path],
            capture_output=True,
            text=True,
            check=True,
            env=env,
            cwd="C:/SAHIL/NOTES"
        )
        print("[DEBUG] sircode.py STDOUT:\n", result1.stdout)
        print("[DEBUG] sircode.py STDERR:\n", result1.stderr)
        print(f"[DEBUG] Files in csv_notes/: {os.listdir('csv_notes') if os.path.exists('csv_notes') else 'csv_notes does not exist'}")
    except subprocess.CalledProcessError as e:
        print("[ERROR] sircode.py failed")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise HTTPException(status_code=500, detail=f"sircode.py failed: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

    # 3. Run csv_json.py to generate clean_financial_data.json
    try:
        print("[DEBUG] Running csv_json.py...")
        result2 = subprocess.run(
            ["python", "pnlbs/csv_json.py"],
            capture_output=True,
            text=True,
            check=True,
            env=env,
            cwd="C:/SAHIL/NOTES"
        )
        print("[DEBUG] csv_json.py STDOUT:\n", result2.stdout)
        print("[DEBUG] csv_json.py STDERR:\n", result2.stderr)
        print(f"[DEBUG] clean_financial_data.json exists: {os.path.exists('clean_financial_data.json')}")
    except subprocess.CalledProcessError as e:
        print("[ERROR] csv_json.py failed")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise HTTPException(status_code=500, detail=f"csv_json.py failed: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

    # 4. Run bl_llm.py to generate the balance sheet Excel
    try:
        print("[DEBUG] Running bl_llm.py...")
        result3 = subprocess.run(
            ["python", "pnlbs/bl_llm.py"],
            capture_output=True,
            text=True,
            check=True,
            env=env,
            cwd="C:/SAHIL/NOTES"
        )
        print("[DEBUG] bl_llm.py STDOUT:\n", result3.stdout)
        print("[DEBUG] bl_llm.py STDERR:\n", result3.stderr)
        # Try to extract the output file path from the script output
        output_file = None
        for line in result3.stdout.splitlines():
            if "Output file:" in line:
                output_file = line.split("Output file:")[-1].strip()
                break
        if not output_file or not os.path.exists(output_file):
            debug_msg = f"\nSTDOUT:\n{result3.stdout}\nSTDERR:\n{result3.stderr}"
            print("[ERROR] Could not determine output file from bl_llm.py output.", debug_msg)
            raise Exception(f"Could not determine output file from bl_llm.py output.{debug_msg}")
    except subprocess.CalledProcessError as e:
        print("[ERROR] bl_llm.py failed")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"bl_llm.py failed: {e}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        )

    print(f"[DEBUG] Pipeline completed. Output file: {output_file}")
    return {"message": "Balance Sheet generated successfully.", "file": output_file}