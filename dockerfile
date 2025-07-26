# Use a Python base image with explicit AMD64 platform

FROM python:3.10

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /Draft1

# Copy requirements file
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY d.pdf .

RUN python -c "import spacy; from spacy_layout import spaCyLayout; nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner', 'lemmatizer']); layout = spaCyLayout(nlp); layout('d.pdf')"

RUN pip install tqdm pdf2image pymupdf
RUN apt-get update && apt-get install -y poppler-utils
# Copy the Python script and any other necessary files

COPY main.py .

# Command to run the Python script
CMD ["python", "main.py"]