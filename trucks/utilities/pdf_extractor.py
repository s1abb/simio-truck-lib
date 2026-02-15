"""
PDF Text Extraction Utility

Extracts text from equipment specification PDFs and saves to .txt files.
This facilitates easier searching, data extraction, and reference.

Usage:
    python pdf_extractor.py --all                    # Extract all PDFs
    python pdf_extractor.py --pdf "CAT 794 AC.pdf"   # Extract specific PDF
"""

import os
import sys
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(pdf_path: Path, output_path: Optional[Path] = None) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path for output .txt file. If None, uses same name as PDF
        
    Returns:
        Extracted text content
        
    Raises:
        ImportError: If PyPDF2 is not installed
        FileNotFoundError: If PDF file doesn't exist
    """
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        print("Error: PyPDF2 not installed. Install with: pip install PyPDF2")
        raise
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Read PDF
    reader = PdfReader(str(pdf_path))
    text_content = []
    
    print(f"Extracting text from: {pdf_path.name}")
    print(f"  Pages: {len(reader.pages)}")
    
    # Extract text from each page
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        text_content.append(f"{'='*80}\n")
        text_content.append(f"PAGE {page_num}\n")
        text_content.append(f"{'='*80}\n\n")
        text_content.append(text)
        text_content.append("\n\n")
    
    full_text = "".join(text_content)
    
    # Determine output path
    if output_path is None:
        output_path = pdf_path.with_suffix('.txt')
    
    # Write to file
    output_path.write_text(full_text, encoding='utf-8')
    print(f"  Saved to: {output_path.name}")
    print(f"  Characters extracted: {len(full_text):,}")
    
    return full_text


def extract_all_pdfs(specs_dir: Path) -> dict:
    """
    Extract text from all PDFs in the specifications directory.
    
    Args:
        specs_dir: Path to specifications directory
        
    Returns:
        Dictionary mapping PDF names to extraction status
    """
    if not specs_dir.exists():
        raise FileNotFoundError(f"Specifications directory not found: {specs_dir}")
    
    pdf_files = list(specs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {specs_dir}")
        return {}
    
    print(f"\nFound {len(pdf_files)} PDF file(s)\n")
    
    results = {}
    for pdf_path in sorted(pdf_files):
        try:
            extract_text_from_pdf(pdf_path)
            results[pdf_path.name] = "Success"
        except Exception as e:
            print(f"  Error: {e}")
            results[pdf_path.name] = f"Failed: {e}"
        print()
    
    # Summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    successful = sum(1 for v in results.values() if v == "Success")
    print(f"Successful: {successful}/{len(results)}")
    
    if successful < len(results):
        print("\nFailed extractions:")
        for pdf, status in results.items():
            if status != "Success":
                print(f"  - {pdf}: {status}")
    
    return results


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract text from equipment specification PDFs"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Extract all PDFs in specifications directory"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        help="Extract specific PDF file (name or path)"
    )
    parser.add_argument(
        "--specs-dir",
        type=str,
        default="../specifications",
        help="Path to specifications directory (default: ../specifications)"
    )
    
    args = parser.parse_args()
    
    # Determine specifications directory
    specs_dir = Path(__file__).parent / args.specs_dir
    specs_dir = specs_dir.resolve()
    
    if args.all:
        extract_all_pdfs(specs_dir)
    elif args.pdf:
        pdf_path = specs_dir / args.pdf
        if not pdf_path.exists():
            # Try as direct path
            pdf_path = Path(args.pdf)
        extract_text_from_pdf(pdf_path)
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python pdf_extractor.py --all")
        print('  python pdf_extractor.py --pdf "CAT 794 AC Tech Specs.pdf"')


if __name__ == "__main__":
    main()
