"""Утилита для извлечения текста из PDF."""
import sys
from pathlib import Path


def extract_text_from_pdf(pdf_path: str, output_path: str = None) -> str:
    """Извлекает текст из PDF файла."""
    try:
        import pypdf
    except ImportError:
        print("Установите pypdf: pip install pypdf")
        return ""

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"Файл не найден: {pdf_path}")
        return ""

    text = ""
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Ошибка чтения PDF: {e}")
        return ""

    if output_path:
        output = Path(output_path)
        output.write_text(text, encoding="utf-8")
        print(f"Сохранено в: {output}")

    return text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pdf_tool.py <pdf_file> [output_txt_file]")
    else:
        pdf_file = sys.argv[1]
        out_file = sys.argv[2] if len(sys.argv) > 2 else None
        extract_text_from_pdf(pdf_file, out_file)