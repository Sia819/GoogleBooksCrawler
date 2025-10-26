# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GoogleBooksCrawler is a Python-based web scraping tool that downloads book pages from Google Play Books using Selenium and undetected-chromedriver. The project processes downloaded images through a pipeline: download → PNG conversion → JPEG conversion → PDF compilation.

## Development Environment

- **Python Version**: 3.11.8
- **Environment**: Windows with Python virtual environment (venv)
- **Key Dependencies**: selenium, undetected-chromedriver, Pillow, requests

### Virtual Environment Setup

```bash
# Activate virtual environment (Windows)
Scripts\activate

# Deactivate
deactivate
```

## Project Structure

- **Source/**: Contains Jupyter notebooks for each stage of the pipeline
  - `book.ipynb`: Main scraping logic using Selenium to download book pages
  - `book_to_png.ipynb`: Converts downloaded images to PNG format with validation
  - `png_to_pdf.ipynb`: Converts PNG images to PDF with color enhancement
  - `reorder.ipynb`: Renumbers files in natural sort order
  - `test_*.ipynb`: Testing notebooks for specific functionality

- **Downloads/**: Default output directory for scraped images (not in git)
- **Scripts/**: Python virtual environment scripts

## Core Workflow

The tool follows a multi-stage pipeline:

1. **Scraping** (book.ipynb): Uses Selenium to navigate Google Play Books reader, extract blob URLs from iframe content, and download images via JavaScript injection
2. **Format Conversion** (book_to_png.ipynb): Validates and converts all images to PNG format, detecting misnamed files
3. **Enhancement** (book_to_png.ipynb): Converts PNG to JPEG with sharpness enhancement (quality=100)
4. **File Ordering** (reorder.ipynb): Renumbers files in natural numeric order (handles decimals)
5. **PDF Generation** (png_to_pdf.ipynb): Compiles images into single PDF with color enhancement

## Key Technical Details

### Web Scraping Strategy

- Uses undetected-chromedriver to bypass bot detection
- Navigates within iframe (`.-gb-display`) to access book content
- Extracts blob URLs from dynamically loaded `<img>` elements
- Downloads via JavaScript `fetch()` and blob URL creation to bypass CORS
- Maintains session cookies for authenticated access
- Auto-scrolls virtual scroll container to load more pages

### Image Processing

- Validates PNG format even if extension is .png (detects JPEG-as-PNG)
- Applies sharpness enhancement (factor 1.2) before JPEG conversion
- Optional UnsharpMask filter for additional sharpness
- Color enhancement (factor 1.5) when creating PDFs
- Always converts to RGB mode before JPEG/PDF operations

### File Management

- Uses natural sorting that handles numeric sequences (1, 2, 10, 11 not 1, 10, 11, 2)
- Handles decimal numbering (1.1, 1.2, etc.)
- Two-phase rename (temp names → final names) to avoid conflicts
- Configurable `force_startnum` to offset page numbering

## Running the Pipeline

Each notebook is designed to run in Jupyter. Typical execution order:

1. Run `book.ipynb` to scrape pages (requires manual login to Google account)
2. Run `book_to_png.ipynb` to validate/convert formats
3. Optionally run `reorder.ipynb` if files need renumbering
4. Run `png_to_pdf.ipynb` to generate final PDF

### Important Configuration

Before running, update paths in notebooks:
- `directory_path` in conversion scripts
- `download_path` in book.ipynb
- `force_startnum` if starting from non-zero page number

## Notes

- Browser must allow popups for download functionality
- Scraping runs in infinite loop (manually interrupt when complete)
- Cookie-based authentication requires interactive browser login
- PIL's `ImageFile.LOAD_TRUNCATED_IMAGES = True` handles incomplete downloads
- Download directory must exist before running scripts
