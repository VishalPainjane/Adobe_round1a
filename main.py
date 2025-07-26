import spacy
from spacy_layout import spaCyLayout
import re
import json
import os
from pathlib import Path
import multiprocessing
from tqdm import tqdm # For the progress bar

# Global variables for worker processes
nlp = None
layout = None

def init_worker():
    """
    Initializer for each worker process.
    OPTIMIZATION: Load spacy model once per process, but disable unused components
    to significantly speed up processing.
    """
    global nlp, layout
    # This is the single biggest speed improvement.
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner', 'tagger', 'lemmatizer', 'attribute_ruler'])
    layout = spaCyLayout(nlp)

def get_level(text, height, unique_heights):
    """Determines the header level based on text patterns and font size."""
    if re.match(r'^\d+\.\s', text):
        if re.match(r'^\d+\.\d+\.\d+', text):
            return "H3"
        elif re.match(r'^\d+\.\d+', text):
            return "H2"
        else:
            return "H1"
    elif unique_heights and height >= unique_heights[0] - 1:
        return "H1"
    return "H2"

def process_pdf(pdf_path, output_path):
    """Processes a single PDF file to extract its structure and saves it as JSON."""
    global layout

    try:
        doc = layout(str(pdf_path))

        headers = []
        for page in doc._.pages:
            # page is a tuple (page_number, list_of_sections)
            sections = page[1]
            for section in sections:
                if section.label_ == "section_header":
                    headers.append({
                        "text": section.text,
                        "x": section._.layout.x,
                        "y": section._.layout.y,
                        "height": section._.layout.height,
                        "layout": section._.layout
                    })

        if not headers:
            result = {"title": "", "outline": []}
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4)
            return # Exit successfully

        headers.sort(key=lambda h: (h['layout'].page_no, h['y']))
        heights = [h['height'] for h in headers]
        unique_heights = sorted(list(set(heights)), reverse=True)

        outline = []
        for header in headers:
            text = header['text'].strip()
            level = get_level(text, header['height'], unique_heights)
            page = header['layout'].page_no
            outline.append({"level": level, "text": text, "page": page})

        doc_title = ""
        if outline:
            first_h1 = next((item for item in outline if item['level'] == 'H1'), None)
            if first_h1:
                doc_title = first_h1['text']
                # Create a new outline list excluding the title element
                outline = [item for item in outline if item is not first_h1]
            else:
                # If no H1, take the first header as title and remove it
                doc_title = outline[0]['text']
                outline = outline[1:]

        document_structure = {
            "title": doc_title,
            "outline": outline
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(document_structure, f, indent=4)

    except Exception as e:
        # It's helpful to print which file failed
        print(f"\n--- FAILED to process {pdf_path.name}: {e} ---")

# FIX: Wrapper function for imap_unordered
def process_pdf_wrapper(args):
    """Helper function to unpack arguments for process_pdf."""
    process_pdf(*args)

def main():
    input_dir = Path(r'input')
    output_dir = Path(r'output')
    output_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    pdf_files = list(input_dir.glob('*.pdf'))

    print(f"Found {len(pdf_files)} PDF files in '{input_dir}'.")

    for pdf_file in pdf_files:
        output_file_path = output_dir / f"{pdf_file.stem}.json"
        if output_file_path.exists():
            continue # Silently skip existing files
        tasks.append((pdf_file, output_file_path))

    if not tasks:
        print("No new PDF files to process. All outputs are generated.")
        return

    # FIX: Set number of processes as requested
    num_processes = 4

    print(f"\nStarting processing of {len(tasks)} new files with {num_processes} workers...")

    # FIX: Use a more robust processing loop with pool.imap_unordered
    # with multiprocessing.Pool(processes=num_processes, initializer=init_worker) as pool:
    with multiprocessing.Pool(processes=num_processes, initializer=init_worker, maxtasksperchild=1) as pool:
        with tqdm(total=len(tasks), desc="Processing PDFs") as pbar:
            # imap_unordered gets results as they are completed, preventing hangs
            for _ in pool.imap_unordered(process_pdf_wrapper, tasks):
                pbar.update(1)

    print("\nProcessing complete.")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()