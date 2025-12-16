#!/usr/bin/env python3
"""
Progress window for Cartoonizer startup.
Displays startup progress while the app initializes.
"""
import tkinter as tk
from tkinter import ttk
import os
import threading
import time

class ProgressWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cartoonizer")
        self.root.geometry("450x220")
        self.root.resizable(False, False)
        
        # Set window level to stay on top
        self.root.attributes('-topmost', True)
        
        # Center on screen
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
        
        # Set background color
        self.root.configure(bg='#f0f0f0')
        
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=20)
        
        title = tk.Label(title_frame, text="Cartoonizer", font=("Helvetica", 24, "bold"), bg='#f0f0f0')
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Loading...", font=("Helvetica", 12), fg="#666666", bg='#f0f0f0')
        subtitle.pack()
        
        # Status label
        self.status_label = tk.Label(self.root, text="Starting up...", font=("Helvetica", 13), bg='#f0f0f0', fg="#333333")
        self.status_label.pack(pady=15)
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('alt')
        self.progress = ttk.Progressbar(self.root, length=350, mode='indeterminate')
        self.progress.pack(pady=15, padx=20)
        self.progress.start(10)
        
        # Details label
        self.details_label = tk.Label(self.root, text="This may take 1-2 minutes on first run", font=("Helvetica", 10), fg="#999999", bg='#f0f0f0')
        self.details_label.pack(pady=10)
        
        self.status_file = os.path.expanduser("~/Library/Application Support/Cartoonizer/progress_status.txt")
        self.running = True
        self.last_status = ""
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_status, daemon=True)
        self.monitor_thread.start()
        
        # Bring window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
    
    def _monitor_status(self):
        """Monitor the status file for updates."""
        while self.running:
            try:
                if os.path.exists(self.status_file):
                    with open(self.status_file, 'r') as f:
                        status = f.read().strip()
                    
                    if status and status != self.last_status:
                        self.last_status = status
                        if status.upper() == "CLOSE":
                            self.running = False
                            try:
                                self.root.quit()
                            except:
                                pass
                            break
                        else:
                            self.update_status(status)
            except Exception as e:
                pass
            
            time.sleep(0.2)
    
    def update_status(self, message):
        """Update the status message from the main thread."""
        try:
            self.root.after(0, lambda: self._update_status_main(message))
        except:
            pass
    
    def _update_status_main(self, message):
        """Update status on the main thread."""
        try:
            self.status_label.config(text=message)
            self.root.update_idletasks()
        except:
            pass
    
    def run(self):
        """Run the window event loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        except Exception:
            pass

if __name__ == "__main__":
    window = ProgressWindow()
    window.run()



