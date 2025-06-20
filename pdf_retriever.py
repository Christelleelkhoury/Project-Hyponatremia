import fitz  # PyMuPDF

def load_pocket_text(pdf_path="Hyponatremia_PocketNephrology_Pages218_225.pdf"):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
