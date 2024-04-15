import os
import json
import csv
import logging
import random
from pypdf import PdfReader
import tiktoken
from openai import OpenAI
import instructor
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel
from threading import Lock
from tqdm import tqdm
import argparse

logging.basicConfig(filename='pdf_processing.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')
write_lock = Lock()

'''CHANGE THESE VALUES ACCORDING TO YOUR NEEDS'''

model = "gpt-4-turbo"
KEY_Q = "question"
KEY_A = "answer"

DATA_CHUNK_SIZE = 2048 # Size of text chunks to generate data off of.

OpenAI.api_key = os.environ['OPENAI_API_KEY']
client = instructor.from_openai(OpenAI())

class QAData(BaseModel):
    question: str
    answer: str

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.txt', '.md']:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logging.error(f"Error reading text from {file_path}: {e}")
            return None
    else:
        logging.error(f"Unsupported file type {ext} for file {file_path}")
        return None
    
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            num_pages = len(reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text() or ''
            return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return None

def split_text_into_chunks(text, tokens_per_chunk=DATA_CHUNK_SIZE, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    chunks = [''.join(encoding.decode(tokens[i:i + tokens_per_chunk])) for i in range(0, len(tokens), tokens_per_chunk)]
    return chunks

def generate_qa_data(text_chunk):
    try:
        temperature = random.uniform(0.0, 0.7)
        
        qa_data = client.chat.completions.create(
            model=model,
            response_model=QAData,
            temperature=temperature,
            messages=[{"role": "system", "content": "You create an informative question, and a CoT answer based on the provided text."},
                      {"role": "user", "content": f"Context: {text_chunk}\\n Based on the previous text, please generate an incredibly in-depth question about the text (this will be question), a detailed and informative answer (this will be the answer value). Think your answer through step by step."}],
        )
        qa_data = qa_data.dict()
        modified_qa_data = {
            KEY_Q: qa_data['question'],
            KEY_A: qa_data['answer'],
        }
        print(modified_qa_data)
        return modified_qa_data
    except Exception as e:
        logging.error(f"Error generating QA data with OpenAI: {e}")
        return None

def write_data(file_format, data, output_file):
    logging.info(f"Writing data to {output_file}, format {file_format}")
    try:
            with open(output_file, 'a', encoding='utf-8', newline='') as file:
                if file_format == 'csv':
                    writer = csv.DictWriter(file, fieldnames=[KEY_Q, KEY_A])
                    if file.tell() == 0:
                        writer.writeheader()
                    writer.writerow(data)
                else:  # jsonl
                    json.dump(data, file)
                    file.write('\n')
            logging.info(f"Data written to {output_file} successfully.")
    except Exception as e:
            logging.error(f"Failed to write data to {output_file}: {e}")


def process_file(file_path, file_format, output_path, processed_files, processed_files_list):
    if os.path.basename(file_path) in processed_files:
        return False

    text = extract_text(file_path)
    if text:
        chunks = split_text_into_chunks(text)
        for chunk in chunks:
            qa_data = generate_qa_data(chunk)
            if qa_data:
                logging.info(f"Generated QA data for chunk: {qa_data}")
                with write_lock:
                    write_data(file_format, qa_data, output_path)
        with write_lock:
            with open(processed_files_list, 'a', encoding='utf-8') as pf:
                pf.write(os.path.basename(file_path) + '\n')
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Process PDF, TXT, or MD files to generate QA data in specified format.")
    parser.add_argument('--data_directory', type=str, required=True, help='Directory containing the text files.')
    parser.add_argument('--output_path', type=str, default=os.getcwd(), help='Path to save the output file. Defaults to the current directory.')
    parser.add_argument('--filetype', type=str, choices=['csv', 'json', 'jsonl'], default='jsonl',
                        help='The format of the output file (CSV or JSONL). Default is JSONL.')
    parser.add_argument('--force', action='store_true', help='Force reprocessing of all files, ignoring the processed files list.')

    args = parser.parse_args()

    os.makedirs(args.output_path, exist_ok=True)

    output_file = os.path.join(args.output_path, 'output_qa.' + ('csv' if args.filetype == 'csv' else 'jsonl'))
    processed_files_list = os.path.join(args.output_path, 'processed_files.txt')

    logging.info(f"Output will be saved to {output_file}")

    file_format = 'csv' if args.filetype == 'csv' else 'jsonl'
    processed_files = set()
    if not args.force and os.path.exists(processed_files_list):
        with open(processed_files_list, 'r', encoding='utf-8') as pf:
            processed_files.update(pf.read().splitlines())

    supported_types = ('.pdf', '.txt', '.md')
    files = [os.path.join(args.data_directory, f) for f in os.listdir(args.data_directory) if os.path.splitext(f)[1] in supported_types and (args.force or f not in processed_files)]
    logging.info(f"Found {len(files)} files to process.")

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_file, file, file_format, output_file, processed_files, processed_files_list): file for file in files}

        with tqdm(total=len(futures), desc="Processing Files", unit="file") as pbar:
            for future in as_completed(futures):
                try:
                    if future.result():
                        pbar.update(1)
                except Exception as e:
                    logging.error(f"Failed to process a file: {e}")

if __name__ == '__main__':
    try:
        logging.basicConfig(filename='pdf_processing.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
        main()
    except Exception as e:
        logging.error(f"An error occurred in main execution: {e}")