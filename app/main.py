import services.downloadBill as dwldB
import services.OCRTesseract as OCRT
import services.OCRFormat as OCRF
import services.dataBaseFormat as dbF
from pathlib import Path

# Define the current working directory
current_directory = Path.cwd()

# Define a relative path (relative to the current directory)
relative_path = Path("data/FAC_2018_0001-654Traitement.png")

# Combine the current directory with the relative path
full_path = current_directory / relative_path

print("Full path:", full_path)

# Check if the relative path exists
if full_path.exists():
    print("File exists!")
    ocr = OCRT.OCRPath(str(full_path))
    transcript = OCRF.SimpleTreatments(ocr)
else:
    print("File does not exist.")
