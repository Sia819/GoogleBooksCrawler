"""
Google Books Crawler GUI Application
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import os
import sys
from datetime import datetime

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.scraper import GoogleBooksScraper
from modules.image_converter import ImageConverter
from modules.file_reorder import FileReorder


class GoogleBooksCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Books Crawler GUI")
        self.root.geometry("900x700")

        # Initialize modules
        self.scraper = None
        self.converter = ImageConverter()
        self.reorder = FileReorder()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.create_scraper_tab()
        self.create_converter_tab()
        self.create_reorder_tab()
        self.create_pdf_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_scraper_tab(self):
        """Create the scraper tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Scraper")

        # URL input
        url_frame = ttk.LabelFrame(tab, text="Book URL", padding="10")
        url_frame.pack(fill="x", padx=10, pady=5)

        self.url_var = tk.StringVar(value="https://play.google.com/books/reader?id=")
        ttk.Label(url_frame, text="URL:").pack(side="left")
        ttk.Entry(url_frame, textvariable=self.url_var, width=70).pack(side="left", padx=5, fill="x", expand=True)

        # Download path
        path_frame = ttk.LabelFrame(tab, text="Download Path", padding="10")
        path_frame.pack(fill="x", padx=10, pady=5)

        self.download_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "Downloads"))
        ttk.Label(path_frame, text="Path:").pack(side="left")
        ttk.Entry(path_frame, textvariable=self.download_path_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_download_path).pack(side="left", padx=5)

        # Start number
        start_frame = ttk.LabelFrame(tab, text="Start Number", padding="10")
        start_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(start_frame, text="Force Start Number (-1 for default):").pack(side="left")
        self.start_num_var = tk.IntVar(value=-1)
        ttk.Spinbox(start_frame, from_=-1, to=9999, textvariable=self.start_num_var, width=10).pack(side="left", padx=5)

        # Control buttons
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.init_driver_btn = ttk.Button(control_frame, text="Initialize Driver", command=self.init_driver)
        self.init_driver_btn.pack(side="left", padx=5)

        self.navigate_btn = ttk.Button(control_frame, text="Navigate to Book", command=self.navigate_to_book, state="disabled")
        self.navigate_btn.pack(side="left", padx=5)

        self.start_scraping_btn = ttk.Button(control_frame, text="Start Scraping", command=self.start_scraping, state="disabled")
        self.start_scraping_btn.pack(side="left", padx=5)

        self.stop_scraping_btn = ttk.Button(control_frame, text="Stop Scraping", command=self.stop_scraping, state="disabled")
        self.stop_scraping_btn.pack(side="left", padx=5)

        ttk.Button(control_frame, text="Close Driver", command=self.close_driver).pack(side="left", padx=5)

        # Progress
        self.scraper_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.scraper_progress.pack(fill="x", padx=10, pady=5)

        # Log output
        log_frame = ttk.LabelFrame(tab, text="Log", padding="10")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.scraper_log = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.scraper_log.pack(fill="both", expand=True)

    def create_converter_tab(self):
        """Create the converter tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="PNG Converter")

        # Directory selection
        dir_frame = ttk.LabelFrame(tab, text="Directory", padding="10")
        dir_frame.pack(fill="x", padx=10, pady=5)

        self.convert_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "Downloads"))
        ttk.Label(dir_frame, text="Directory:").pack(side="left")
        ttk.Entry(dir_frame, textvariable=self.convert_dir_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_convert_dir).pack(side="left", padx=5)

        # Convert to PNG
        png_frame = ttk.LabelFrame(tab, text="Convert to PNG", padding="10")
        png_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(png_frame, text="Convert All to PNG", command=self.convert_to_png, width=30).pack(pady=5)

        # Convert to JPEG
        jpeg_frame = ttk.LabelFrame(tab, text="Convert PNG to JPEG", padding="10")
        jpeg_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(jpeg_frame, text="Output Directory:").grid(row=0, column=0, sticky="w")
        self.jpeg_output_var = tk.StringVar()
        ttk.Entry(jpeg_frame, textvariable=self.jpeg_output_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(jpeg_frame, text="Browse", command=self.browse_jpeg_output).grid(row=0, column=2)

        self.apply_sharpness_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(jpeg_frame, text="Apply Sharpness Enhancement", variable=self.apply_sharpness_var).grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(jpeg_frame, text="Convert to JPEG", command=self.convert_to_jpeg, width=30).grid(row=2, column=0, columnspan=3, pady=5)

        # Progress
        self.converter_progress = ttk.Progressbar(tab, maximum=100)
        self.converter_progress.pack(fill="x", padx=10, pady=5)

        # Log
        log_frame = ttk.LabelFrame(tab, text="Log", padding="10")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.converter_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.converter_log.pack(fill="both", expand=True)

    def create_reorder_tab(self):
        """Create the reorder tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="File Reorder")

        # Directory selection
        dir_frame = ttk.LabelFrame(tab, text="Directory", padding="10")
        dir_frame.pack(fill="x", padx=10, pady=5)

        self.reorder_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "Downloads"))
        ttk.Label(dir_frame, text="Directory:").pack(side="left")
        ttk.Entry(dir_frame, textvariable=self.reorder_dir_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_reorder_dir).pack(side="left", padx=5)

        # Options
        options_frame = ttk.LabelFrame(tab, text="Options", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(options_frame, text="File Extension:").grid(row=0, column=0, sticky="w")
        self.reorder_ext_var = tk.StringVar(value=".png")
        ttk.Entry(options_frame, textvariable=self.reorder_ext_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(options_frame, text="Start Number:").grid(row=1, column=0, sticky="w")
        self.reorder_start_var = tk.IntVar(value=0)
        ttk.Spinbox(options_frame, from_=0, to=9999, textvariable=self.reorder_start_var, width=10).grid(row=1, column=1, padx=5)

        # Preview and execute
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="Preview Files", command=self.preview_files, width=20).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Rename Files", command=self.rename_files, width=20).pack(side="left", padx=5)

        # Progress
        self.reorder_progress = ttk.Progressbar(tab, maximum=100)
        self.reorder_progress.pack(fill="x", padx=10, pady=5)

        # File list
        list_frame = ttk.LabelFrame(tab, text="File List", padding="10")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.file_listbox = tk.Listbox(list_frame)
        self.file_listbox.pack(fill="both", expand=True)

    def create_pdf_tab(self):
        """Create the PDF tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="PDF Creator")

        # Source directory
        source_frame = ttk.LabelFrame(tab, text="Source Directory", padding="10")
        source_frame.pack(fill="x", padx=10, pady=5)

        self.pdf_source_var = tk.StringVar(value=os.path.join(os.getcwd(), "Downloads"))
        ttk.Label(source_frame, text="Directory:").pack(side="left")
        ttk.Entry(source_frame, textvariable=self.pdf_source_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(source_frame, text="Browse", command=self.browse_pdf_source).pack(side="left", padx=5)

        # Output file
        output_frame = ttk.LabelFrame(tab, text="Output PDF", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)

        self.pdf_output_var = tk.StringVar(value=os.path.join(os.getcwd(), "output.pdf"))
        ttk.Label(output_frame, text="Output File:").pack(side="left")
        ttk.Entry(output_frame, textvariable=self.pdf_output_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_pdf_output).pack(side="left", padx=5)

        # Options
        options_frame = ttk.LabelFrame(tab, text="Options", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)

        self.enhance_color_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Enhance Colors", variable=self.enhance_color_var).grid(row=0, column=0, sticky="w")

        ttk.Label(options_frame, text="Color Factor:").grid(row=1, column=0, sticky="w")
        self.color_factor_var = tk.DoubleVar(value=1.5)
        ttk.Scale(options_frame, from_=1.0, to=2.0, variable=self.color_factor_var, orient="horizontal", length=200).grid(row=1, column=1, padx=5)
        ttk.Label(options_frame, textvariable=self.color_factor_var).grid(row=1, column=2)

        # Create PDF button
        ttk.Button(tab, text="Create PDF", command=self.create_pdf, width=30).pack(pady=10)

        # Progress
        self.pdf_progress = ttk.Progressbar(tab, maximum=100)
        self.pdf_progress.pack(fill="x", padx=10, pady=5)

        # Log
        log_frame = ttk.LabelFrame(tab, text="Log", padding="10")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.pdf_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.pdf_log.pack(fill="both", expand=True)

    # Scraper methods
    def init_driver(self):
        """Initialize Chrome driver"""
        self.log_message(self.scraper_log, "Initializing Chrome driver...")
        self.scraper = GoogleBooksScraper(self.download_path_var.get())

        if self.scraper.init_driver():
            self.log_message(self.scraper_log, "Driver initialized successfully")
            self.navigate_btn.config(state="normal")
            self.init_driver_btn.config(state="disabled")
        else:
            self.log_message(self.scraper_log, "Failed to initialize driver")

    def navigate_to_book(self):
        """Navigate to book URL"""
        if not self.scraper:
            return

        url = self.url_var.get()
        self.log_message(self.scraper_log, f"Navigating to: {url}")

        if self.scraper.navigate_to_book(url):
            self.log_message(self.scraper_log, "Navigation successful. Please login if required.")
            self.start_scraping_btn.config(state="normal")
        else:
            self.log_message(self.scraper_log, "Navigation failed")

    def start_scraping(self):
        """Start scraping in a separate thread"""
        if not self.scraper:
            return

        self.scraper.force_startnum = self.start_num_var.get()
        self.start_scraping_btn.config(state="disabled")
        self.stop_scraping_btn.config(state="normal")
        self.scraper_progress.start(10)

        def scrape_callback(new_images):
            for url, index in new_images:
                self.log_message(self.scraper_log, f"Downloaded: {index}.png")

        thread = threading.Thread(target=self.scraper.start_scraping, args=(scrape_callback,))
        thread.daemon = True
        thread.start()

        self.log_message(self.scraper_log, "Scraping started...")

    def stop_scraping(self):
        """Stop scraping"""
        if self.scraper:
            self.scraper.stop_scraping()
            self.scraper_progress.stop()
            self.start_scraping_btn.config(state="normal")
            self.stop_scraping_btn.config(state="disabled")
            self.log_message(self.scraper_log, "Scraping stopped")

    def close_driver(self):
        """Close Chrome driver"""
        if self.scraper:
            self.scraper.close()
            self.scraper = None
            self.init_driver_btn.config(state="normal")
            self.navigate_btn.config(state="disabled")
            self.start_scraping_btn.config(state="disabled")
            self.stop_scraping_btn.config(state="disabled")
            self.log_message(self.scraper_log, "Driver closed")

    # Converter methods
    def convert_to_png(self):
        """Convert images to PNG"""
        directory = self.convert_dir_var.get()
        if not os.path.exists(directory):
            messagebox.showerror("Error", "Directory does not exist")
            return

        self.converter_progress['value'] = 0
        self.converter_log.delete(1.0, tk.END)

        def callback(message, current=None, total=None):
            self.log_message(self.converter_log, message)
            if current and total:
                progress = (current / total) * 100
                self.converter_progress['value'] = progress
                self.root.update_idletasks()

        def run_conversion():
            file_count, converted, misnamed = self.converter.convert_to_png(directory, callback)
            self.log_message(self.converter_log, f"\nConversion complete: {converted}/{file_count} files")
            if misnamed:
                self.log_message(self.converter_log, f"Fixed {len(misnamed)} misnamed files")

        thread = threading.Thread(target=run_conversion)
        thread.daemon = True
        thread.start()

    def convert_to_jpeg(self):
        """Convert PNG to JPEG"""
        source = self.convert_dir_var.get()
        output = self.jpeg_output_var.get()

        if not os.path.exists(source):
            messagebox.showerror("Error", "Source directory does not exist")
            return

        if not output:
            messagebox.showerror("Error", "Please specify output directory")
            return

        self.converter_progress['value'] = 0

        def callback(message, current=None, total=None):
            self.log_message(self.converter_log, message)
            if current and total:
                progress = (current / total) * 100
                self.converter_progress['value'] = progress
                self.root.update_idletasks()

        def run_conversion():
            processed = self.converter.convert_png_to_jpeg(
                source, output,
                self.apply_sharpness_var.get(),
                callback
            )
            self.log_message(self.converter_log, f"\nConverted {processed} files to JPEG")

        thread = threading.Thread(target=run_conversion)
        thread.daemon = True
        thread.start()

    # Reorder methods
    def preview_files(self):
        """Preview files in directory"""
        directory = self.reorder_dir_var.get()
        if not os.path.exists(directory):
            messagebox.showerror("Error", "Directory does not exist")
            return

        extension = self.reorder_ext_var.get()
        files = self.reorder.get_file_list(directory, extension)

        self.file_listbox.delete(0, tk.END)
        for i, file in enumerate(files):
            new_name = f"{self.reorder_start_var.get() + i}{extension}"
            self.file_listbox.insert(tk.END, f"{file} -> {new_name}")

    def rename_files(self):
        """Rename files"""
        directory = self.reorder_dir_var.get()
        if not os.path.exists(directory):
            messagebox.showerror("Error", "Directory does not exist")
            return

        if not messagebox.askyesno("Confirm", "Are you sure you want to rename all files?"):
            return

        self.reorder_progress['value'] = 0

        def callback(message, current=None, total=None):
            self.file_listbox.insert(tk.END, message)
            self.file_listbox.see(tk.END)
            if current and total:
                progress = (current / total) * 100
                self.reorder_progress['value'] = progress
                self.root.update_idletasks()

        def run_rename():
            self.file_listbox.delete(0, tk.END)
            count = self.reorder.rename_files(
                directory,
                self.reorder_ext_var.get(),
                self.reorder_start_var.get(),
                callback
            )
            messagebox.showinfo("Complete", f"Renamed {count} files")

        thread = threading.Thread(target=run_rename)
        thread.daemon = True
        thread.start()

    # PDF methods
    def create_pdf(self):
        """Create PDF from images"""
        source = self.pdf_source_var.get()
        output = self.pdf_output_var.get()

        if not os.path.exists(source):
            messagebox.showerror("Error", "Source directory does not exist")
            return

        if not output:
            messagebox.showerror("Error", "Please specify output file")
            return

        self.pdf_progress['value'] = 0
        self.pdf_log.delete(1.0, tk.END)

        def callback(message, current=None, total=None):
            self.log_message(self.pdf_log, message)
            if current and total:
                progress = (current / total) * 100
                self.pdf_progress['value'] = progress
                self.root.update_idletasks()

        def run_create():
            success = self.converter.convert_to_pdf(
                source, output,
                self.enhance_color_var.get(),
                self.color_factor_var.get(),
                callback
            )
            if success:
                messagebox.showinfo("Complete", f"PDF created: {output}")
            else:
                messagebox.showerror("Error", "Failed to create PDF")

        thread = threading.Thread(target=run_create)
        thread.daemon = True
        thread.start()

    # Browse methods
    def browse_download_path(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path_var.set(path)

    def browse_convert_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.convert_dir_var.set(path)

    def browse_jpeg_output(self):
        path = filedialog.askdirectory()
        if path:
            self.jpeg_output_var.set(path)

    def browse_reorder_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.reorder_dir_var.set(path)

    def browse_pdf_source(self):
        path = filedialog.askdirectory()
        if path:
            self.pdf_source_var.set(path)

    def browse_pdf_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_output_var.set(path)

    # Utility methods
    def log_message(self, text_widget, message):
        """Log message to text widget"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        text_widget.insert(tk.END, f"[{timestamp}] {message}\n")
        text_widget.see(tk.END)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = GoogleBooksCrawlerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()