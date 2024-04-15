# Synthetic Data Generators!

Welcome to my Synthetic Data Generators Project! This project utilizes GPT-4-Turbo to generate synthetic data from textual content extracted from PDF, TXT, and MD files. This project comprises two main scripts: `dpo.py` and `qa.py`, each tailored to generate specific types of data outputs.

<p align="center">
  <a href="https://postimg.cc/V0XBktX5">
    <img src="https://i.postimg.cc/ZnMfjFRP/DALL-E-2024-04-15-14-01-18-A-cute-and-whimsical-image-of-a-small-robot-looking-surprised-as-it-gen.webp" alt="DALL-E-2024-04-15-14-01-18-A-cute-and-whimsical-image-of-a-small-robot-looking-surprised">
  </a>
</p>

## Overview

- `dpo.py`: Generates data with prompts, informative answers, and intentionally incorrect answers to simulate decision-making processes.
- `qa.py`: Produces pairs of in-depth questions and comprehensive answers based on the context of the provided text.

This is a new project and we are excited to see how it evolves. We welcome any recommendations, enhancements, or bug fixes to improve the functionality and utility of these tools.

## Features

- **PDF Text Extraction**: Read and process text from PDF files.
- **Text Chunking**: Break down large texts into manageable chunks suitable for processing.
- **Synthetic Question and Answer Generation**: Leverage OpenAI's GPT models to generate realistic and contextually relevant questions and answers.
- **Concurrency**: Handle multiple files concurrently to optimize processing time.
- **Customizability**: Easily adjust key parameters like the model version or data chunk size according to your needs.

## Installation

To set up this project, clone the repository and install the required Python packages:

```bash
git clone <repository-url>
cd synthetic-data-generation
pip install -r requirements.txt
```
## Usage
Both scripts are command-line tools that require specific arguments to run. Here's how you can use each tool:

##### export OpenAI API Key
```bash
export <openai-api-key>
```

#### dpo.py
```bash
python dpo.py --data_directory <path_to_data_directory> --output_path <path_to_output> --filetype jsonl --force
```
#### qa.py
```bash
python qa.py --data_directory <path_to_data_directory> --output_path <path_to_output> --filetype csv
```

### Arguments:

--data_directory: The directory containing your source text files.
--output_path: The directory where the output will be saved. (Optional: defaults to current directory)
--filetype: The output file format (csv, json, jsonl).
--force: Force reprocessing of all files, ignoring the processed files list.

### Contributing
I'm seeking community contributions!

Feedback: Share your feedback and suggestions to enhance the tool.
Code Contributions: Submit pull requests with bug fixes or new features.
Documentation: Help me improve or correct the existing documentation.

## THANKS AND GET GENERATING!
