import os
from dotenv import load_dotenv

load_dotenv()

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
EXCEL_FILES = {
    "A1": "A1.xlsx",
    "A2": "A2.xlsx",
    "B1": "B1.xlsx",
    "B2": "B2.xlsx",
    "C1": "C1.xlsx",
    "C2": "C2.xlsx"
}
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash" 