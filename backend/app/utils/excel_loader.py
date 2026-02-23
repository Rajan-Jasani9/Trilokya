import pandas as pd
from typing import List, Dict


def load_trl_definitions_from_excel(file_path: str) -> List[Dict]:
    """
    Load TRL definitions from Excel file.
    Expected format:
    - Sheet: TRL Definitions
      Columns: Level, Name, Description, Evidence Required, Min Confidence
    - Sheet: TRL Questions
      Columns: TRL Level, Question Order, Question Text, Is Required, Evidence Required, Weight
    """
    try:
        # Load TRL definitions
        definitions_df = pd.read_excel(file_path, sheet_name="TRL Definitions")
        questions_df = pd.read_excel(file_path, sheet_name="TRL Questions")
        
        definitions = []
        
        for _, row in definitions_df.iterrows():
            level = int(row["Level"])
            name = str(row["Name"])
            description = row.get("Description", "")
            # Evidence is required by default unless explicitly configured otherwise
            evidence_required = bool(row.get("Evidence Required", True))
            min_confidence = row.get("Min Confidence")
            if pd.notna(min_confidence):
                min_confidence = float(min_confidence)
            else:
                min_confidence = None
            
            # Get questions for this TRL level
            level_questions = questions_df[questions_df["TRL Level"] == level]
            questions = []
            
            for _, q_row in level_questions.iterrows():
                questions.append({
                    "order": int(q_row["Question Order"]),
                    "text": str(q_row["Question Text"]),
                    "is_required": bool(q_row.get("Is Required", True)),
                    # Evidence is required by default for all questions unless explicitly disabled
                    "evidence_required": bool(q_row.get("Evidence Required", True)),
                    "weight": float(q_row.get("Weight", 1.0))
                })
            
            definitions.append({
                "level": level,
                "name": name,
                "description": description,
                "evidence_required": evidence_required,
                "min_confidence": min_confidence,
                "questions": sorted(questions, key=lambda x: x["order"])
            })
        
        return definitions
    except Exception as e:
        raise ValueError(f"Error loading Excel file: {str(e)}")
