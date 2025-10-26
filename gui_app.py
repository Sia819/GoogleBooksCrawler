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
from modules.settings_manager import SettingsManager


class GoogleBooksCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Books Crawler GUI")
        self.root.geometry("900x700")

        # Initialize settings manager
        self.settings = SettingsManager()

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

        # Check profile status on startup
        self.root.after(100, self.check_profile_status)

    def create_scraper_tab(self):
        """Create the scraper tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Scraper")

        # Chrome Profile settings
        profile_frame = ttk.LabelFrame(tab, text="Chrome Profile Settings", padding="10")
        profile_frame.pack(fill="x", padx=10, pady=5)

        self.use_profile_var = tk.BooleanVar(value=self.settings.get_bool('Scraper', 'use_profile', True))
        profile_checkbox = ttk.Checkbutton(
            profile_frame,
            text="Use persistent Chrome profile (keeps login sessions)",
            variable=self.use_profile_var,
            command=self.on_profile_toggle
        )
        profile_checkbox.pack(side="left", padx=5)

        self.profile_status_var = tk.StringVar(value="")
        ttk.Label(profile_frame, textvariable=self.profile_status_var, foreground="green").pack(side="left", padx=20)

        ttk.Button(profile_frame, text="Clear Profile", command=self.clear_profile).pack(side="right", padx=5)

        # URL input
        url_frame = ttk.LabelFrame(tab, text="Book URL", padding="10")
        url_frame.pack(fill="x", padx=10, pady=5)

        self.url_var = tk.StringVar(value=self.settings.get('Scraper', 'book_url', 'https://play.google.com/books/reader?id='))
        self.url_var.trace('w', lambda *args: self.settings.set('Scraper', 'book_url', self.url_var.get()))
        ttk.Label(url_frame, text="URL:").pack(side="left")
        ttk.Entry(url_frame, textvariable=self.url_var, width=70).pack(side="left", padx=5, fill="x", expand=True)

        # Download path
        path_frame = ttk.LabelFrame(tab, text="Download Path", padding="10")
        path_frame.pack(fill="x", padx=10, pady=5)

        self.download_path_var = tk.StringVar(value=self.settings.get('Scraper', 'download_path', os.path.join(os.getcwd(), "Downloads")))
        self.download_path_var.trace('w', lambda *args: self.settings.set('Scraper', 'download_path', self.download_path_var.get()))
        ttk.Label(path_frame, text="Path:").pack(side="left")
        ttk.Entry(path_frame, textvariable=self.download_path_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=self.browse_download_path).pack(side="left", padx=5)

        # Start number
        start_frame = ttk.LabelFrame(tab, text="Start Number", padding="10")
        start_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(start_frame, text="Force Start Number (-1 for default):").pack(side="left")
        self.start_num_var = tk.IntVar(value=self.settings.get_int('Scraper', 'force_start_number', -1))
        self.start_num_var.trace('w', lambda *args: self.settings.set('Scraper', 'force_start_number', self.start_num_var.get()))
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

        # Zoom controls
        zoom_frame = ttk.LabelFrame(tab, text="Zoom Control", padding="10")
        zoom_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(zoom_frame, text="Zoom Out (-)", command=self.zoom_out, width=15).pack(side="left", padx=5)
        ttk.Button(zoom_frame, text="Reset (100%)", command=self.reset_zoom, width=15).pack(side="left", padx=5)
        ttk.Button(zoom_frame, text="Zoom In (+)", command=self.zoom_in, width=15).pack(side="left", padx=5)

        ttk.Label(zoom_frame, text="Custom Zoom:").pack(side="left", padx=10)
        self.zoom_level_var = tk.IntVar(value=self.settings.get_int('Scraper', 'zoom_level', 100))
        self.zoom_level_var.trace('w', lambda *args: self.settings.set('Scraper', 'zoom_level', self.zoom_level_var.get()))
        zoom_spinbox = ttk.Spinbox(zoom_frame, from_=25, to=300, textvariable=self.zoom_level_var, width=10, increment=10)
        zoom_spinbox.pack(side="left", padx=5)
        ttk.Label(zoom_frame, text="%").pack(side="left")
        ttk.Button(zoom_frame, text="Apply", command=self.apply_zoom, width=10).pack(side="left", padx=5)

        self.zoom_status_var = tk.StringVar(value="Zoom: 100%")
        ttk.Label(zoom_frame, textvariable=self.zoom_status_var, font=("Arial", 10, "bold")).pack(side="right", padx=10)

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

        self.convert_dir_var = tk.StringVar(value=self.settings.get('Converter', 'directory', os.path.join(os.getcwd(), "Downloads")))
        self.convert_dir_var.trace('w', lambda *args: self.settings.set('Converter', 'directory', self.convert_dir_var.get()))
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
        self.jpeg_output_var = tk.StringVar(value=self.settings.get('Converter', 'jpeg_output', ''))
        self.jpeg_output_var.trace('w', lambda *args: self.settings.set('Converter', 'jpeg_output', self.jpeg_output_var.get()))
        ttk.Entry(jpeg_frame, textvariable=self.jpeg_output_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(jpeg_frame, text="Browse", command=self.browse_jpeg_output).grid(row=0, column=2)

        self.apply_sharpness_var = tk.BooleanVar(value=self.settings.get_bool('Converter', 'apply_sharpness', True))
        self.apply_sharpness_var.trace('w', lambda *args: self.settings.set('Converter', 'apply_sharpness', str(self.apply_sharpness_var.get())))
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

        self.reorder_dir_var = tk.StringVar(value=self.settings.get('Reorder', 'directory', os.path.join(os.getcwd(), "Downloads")))
        self.reorder_dir_var.trace('w', lambda *args: self.settings.set('Reorder', 'directory', self.reorder_dir_var.get()))
        ttk.Label(dir_frame, text="Directory:").pack(side="left")
        ttk.Entry(dir_frame, textvariable=self.reorder_dir_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_reorder_dir).pack(side="left", padx=5)

        # Options
        options_frame = ttk.LabelFrame(tab, text="Options", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(options_frame, text="File Extension:").grid(row=0, column=0, sticky="w")
        self.reorder_ext_var = tk.StringVar(value=self.settings.get('Reorder', 'file_extension', '.png'))
        self.reorder_ext_var.trace('w', lambda *args: self.settings.set('Reorder', 'file_extension', self.reorder_ext_var.get()))
        ttk.Entry(options_frame, textvariable=self.reorder_ext_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(options_frame, text="Start Number:").grid(row=1, column=0, sticky="w")
        self.reorder_start_var = tk.IntVar(value=self.settings.get_int('Reorder', 'start_number', 0))
        self.reorder_start_var.trace('w', lambda *args: self.settings.set('Reorder', 'start_number', self.reorder_start_var.get()))
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

        self.pdf_source_var = tk.StringVar(value=self.settings.get('PDF', 'source_directory', os.path.join(os.getcwd(), "Downloads")))
        self.pdf_source_var.trace('w', lambda *args: self.settings.set('PDF', 'source_directory', self.pdf_source_var.get()))
        ttk.Label(source_frame, text="Directory:").pack(side="left")
        ttk.Entry(source_frame, textvariable=self.pdf_source_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(source_frame, text="Browse", command=self.browse_pdf_source).pack(side="left", padx=5)

        # Output file
        output_frame = ttk.LabelFrame(tab, text="Output PDF", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)

        self.pdf_output_var = tk.StringVar(value=self.settings.get('PDF', 'output_file', os.path.join(os.getcwd(), "output.pdf")))
        self.pdf_output_var.trace('w', lambda *args: self.settings.set('PDF', 'output_file', self.pdf_output_var.get()))
        ttk.Label(output_frame, text="Output File:").pack(side="left")
        ttk.Entry(output_frame, textvariable=self.pdf_output_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_pdf_output).pack(side="left", padx=5)

        # Options
        options_frame = ttk.LabelFrame(tab, text="Options", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)

        self.enhance_color_var = tk.BooleanVar(value=self.settings.get_bool('PDF', 'enhance_color', True))
        self.enhance_color_var.trace('w', lambda *args: self.settings.set('PDF', 'enhance_color', str(self.enhance_color_var.get())))
        ttk.Checkbutton(options_frame, text="Enhance Colors", variable=self.enhance_color_var).grid(row=0, column=0, sticky="w")

        ttk.Label(options_frame, text="Color Factor:").grid(row=1, column=0, sticky="w")
        self.color_factor_var = tk.DoubleVar(value=self.settings.get_float('PDF', 'color_factor', 1.5))
        self.color_factor_var.trace('w', lambda *args: self.settings.set('PDF', 'color_factor', self.color_factor_var.get()))
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
        self.check_profile_status()
        use_profile = self.use_profile_var.get()

        if use_profile:
            self.log_message(self.scraper_log, "Initializing Chrome driver with persistent profile...")
        else:
            self.log_message(self.scraper_log, "Initializing Chrome driver without profile...")

        self.scraper = GoogleBooksScraper(self.download_path_var.get(), use_profile=use_profile)

        if self.scraper.init_driver(use_existing_profile=use_profile):
            self.log_message(self.scraper_log, "Driver initialized successfully")
            if use_profile:
                self.log_message(self.scraper_log, "Profile loaded - previous login sessions should be preserved")
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

    # Zoom methods
    def zoom_in(self):
        """Zoom in the browser"""
        if self.scraper and self.scraper.zoom_in():
            self.update_zoom_status()
            self.log_message(self.scraper_log, "Zoomed in")
        else:
            self.log_message(self.scraper_log, "Failed to zoom in")

    def zoom_out(self):
        """Zoom out the browser"""
        if self.scraper and self.scraper.zoom_out():
            self.update_zoom_status()
            self.log_message(self.scraper_log, "Zoomed out")
        else:
            self.log_message(self.scraper_log, "Failed to zoom out")

    def reset_zoom(self):
        """Reset browser zoom to 100%"""
        if self.scraper and self.scraper.reset_zoom():
            self.zoom_level_var.set(100)
            self.zoom_status_var.set("Zoom: 100%")
            self.log_message(self.scraper_log, "Zoom reset to 100%")
        else:
            self.log_message(self.scraper_log, "Failed to reset zoom")

    def apply_zoom(self):
        """Apply custom zoom level"""
        zoom_level = self.zoom_level_var.get()
        if self.scraper and self.scraper.set_zoom(zoom_level):
            self.zoom_status_var.set(f"Zoom: {zoom_level}%")
            self.log_message(self.scraper_log, f"Zoom set to {zoom_level}%")
        else:
            self.log_message(self.scraper_log, "Failed to set zoom level")

    def update_zoom_status(self):
        """Update zoom status display"""
        if self.scraper and self.scraper.driver:
            try:
                current = self.scraper.driver.execute_script("return document.body.style.zoom || '100%'")
                current_value = int(current.replace('%', ''))
                self.zoom_level_var.set(current_value)
                self.zoom_status_var.set(f"Zoom: {current_value}%")
            except:
                pass

    # Profile management methods
    def check_profile_status(self):
        """Check if Chrome profile exists"""
        profile_dir = os.path.join(os.getcwd(), 'chrome_profile')
        if os.path.exists(profile_dir) and os.listdir(profile_dir):
            self.profile_status_var.set("✓ Profile exists")
            return True
        else:
            self.profile_status_var.set("")
            return False

    def on_profile_toggle(self):
        """Handle profile checkbox toggle"""
        use_profile = self.use_profile_var.get()
        self.settings.set('Scraper', 'use_profile', str(use_profile))
        if use_profile:
            self.log_message(self.scraper_log, "Profile will be used for next driver initialization")
        else:
            self.log_message(self.scraper_log, "Profile will NOT be used for next driver initialization")

    def clear_profile(self):
        """Clear Chrome profile data"""
        if messagebox.askyesno("Clear Profile", "This will delete all saved login sessions and cookies. Are you sure?"):
            profile_dir = os.path.join(os.getcwd(), 'chrome_profile')
            if os.path.exists(profile_dir):
                try:
                    # Close driver if it's running
                    if self.scraper:
                        self.close_driver()

                    # Remove profile directory
                    import shutil
                    shutil.rmtree(profile_dir)
                    self.log_message(self.scraper_log, "Chrome profile cleared successfully")
                    self.profile_status_var.set("")
                    messagebox.showinfo("Success", "Chrome profile has been cleared")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to clear profile: {str(e)}")
                    self.log_message(self.scraper_log, f"Error clearing profile: {e}")
            else:
                messagebox.showinfo("Info", "No profile exists to clear")

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