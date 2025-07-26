# PDF Outline Extractor

This project provides a robust Python script to automatically extract a structured outline (like a table of contents) from a batch of PDF files. It leverages **spaCy** and **spacy-layout** for content analysis and uses **multiprocessing** to process files in parallel for high efficiency. The entire application is containerized with **Docker** for easy setup and consistent execution.

---

## Features

- **Structured Extraction**: Identifies document titles and hierarchical headers (H1, H2, H3) based on text patterns and font sizes
- **Parallel Processing**: Uses multiple CPU cores (default: 4 workers) to process large numbers of PDFs quickly
- **JSON Output**: Saves the extracted outline for each PDF as a clean, machine-readable JSON file
- **Smart Skipping**: Automatically skips PDFs that have already been processed (existing JSON outputs)
- **Progress Tracking**: Real-time progress bar showing processing status
- **Robust & Resilient**: Designed to handle problematic or large PDF files without crashing the entire batch
- **Memory Efficient**: Uses optimized spaCy pipeline with disabled unused components for faster processing
- **Dockerized**: Fully containerized for simple, dependency-free deployment

---

## Requirements

- Docker Desktop installed and running
- PDF files to process

---

## Project Structure

```
Adobe_round1a/
├── input/          # Place your PDF files here
├── output/         # Generated JSON files will appear here
├── main.py         # Main processing script
├── dockerfile      # Docker configuration
├── requirements.txt # Python dependencies
├── readme.md       # This file
└── torun.md        # Quick reference commands
```

---

## How to Use

### 1. Prepare Your Files

Create an `input` directory in the project root and place all the PDF files you want to process into it:

```bash
mkdir input
# Copy your PDF files to the input directory
```

### 2. Build the Docker Image

Open your terminal and run the following command from the project's root directory:

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

**Note**: The build process includes downloading the spaCy English model and pre-warming the system with a test PDF.

### 3. Run the Extractor

Execute the following command to run the script inside a container:

```bash
docker run --rm -v ${PWD}/input:/Draft1/input -v ${PWD}/output:/Draft1/output --network none mysolutionname:somerandomidentifier
```

**For Windows PowerShell users**, use:
```powershell
docker run --rm -v ${PWD}/input:/Draft1/input -v ${PWD}/output:/Draft1/output --network none mysolutionname:somerandomidentifier
```

Upon completion, you will find a corresponding `.json` file for each processed PDF in the `output` directory.

---

## Configuration

You can configure the script by editing the [`main.py`](main.py) file before building the Docker image.

### Number of Workers

To change the number of parallel processes, modify the `num_processes` variable in the `main()` function:

```python
# In main() function (line ~124)
num_processes = 4  # Change this value
```

### Worker Stability vs Speed

The script uses `maxtasksperchild=1` to ensure stability by restarting worker processes after each task.
To speed up processing (at the cost of some stability), you can modify this parameter:

```python
# Current (stable):
with multiprocessing.Pool(processes=num_processes, initializer=init_worker, maxtasksperchild=1) as pool:

# Faster but less stable:
with multiprocessing.Pool(processes=num_processes, initializer=init_worker) as pool:
```

### Header Detection Logic

The script identifies headers using two methods:
1. **Pattern matching**: Detects numbered sections (1., 1.1, 1.1.1, etc.)
2. **Font size analysis**: Uses relative font heights to determine hierarchy

You can modify the `get_level()` function in [`main.py`](main.py) to adjust header detection logic.

---

## Output Format

The script generates a JSON file for each input PDF with the following structure:

```json
{
    "title": "The Main Title of the Document",
    "outline": [
        {
            "level": "H1",
            "text": "1. First Main Section",
            "page": 2
        },
        {
            "level": "H2",
            "text": "1.1 A Subsection",
            "page": 3
        },
        {
            "level": "H1",
            "text": "2. Another Main Section",
            "page": 5
        }
    ]
}
```

**Notes**:
- The `title` is extracted from the first H1 header found (or first header if no H1 exists)
- The title header is removed from the outline to avoid duplication
- Page numbers are 1-indexed
- Headers are sorted by page number and vertical position

---

## Dependencies

The project uses the following Python packages (see [`requirements.txt`](requirements.txt)):

- `spacy` - Natural language processing library
- `spacy-layout` - Layout analysis extension for spaCy
- `tqdm` - Progress bar library
- `pdf2image` - PDF to image conversion (installed in Docker)
- `pymupdf` - PDF processing library (installed in Docker)

The Docker image also includes:
- `poppler-utils` - PDF utilities
- `en_core_web_sm` - spaCy English language model

---

## Troubleshooting

### Common Issues

1. **No PDFs found**: Ensure PDF files are in the `input` directory
2. **Permission errors**: Make sure Docker has access to your file system
3. **Out of memory**: Reduce `num_processes` for large PDFs or limited RAM
4. **Empty outputs**: Some PDFs may not have detectable headers - check the original document structure

### Performance Tips

- For large batches: Increase `num_processes` up to your CPU core count
- For memory-constrained systems: Keep `maxtasksperchild=1` and reduce `num_processes`
- The script automatically skips already-processed files, so you can safely re-run it

---

## Quick Reference

See [`torun.md`](torun.md) for quick copy-paste commands:

```bash
# Build
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .

# Run
docker run --rm -v ${PWD}/input:/Draft1/input -v ${PWD}/output:/Draft1/output --network none mysolutionname:somerandomidentifier
```
