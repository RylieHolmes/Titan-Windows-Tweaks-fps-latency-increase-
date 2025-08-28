import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import ctypes
import subprocess
import sys
import os
import webbrowser
import logging
from io import BytesIO

# --- Setup Logging ---
# This will create a log file in the same directory as the script/exe
logging.basicConfig(filename='titan_tool.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

# --- Constants ---
APP_TITLE = "Titan Tweak Tool v4.2"
APP_GEOMETRY = "950x750"
GITHUB_URL = "https://github.com/YOUR_USERNAME/titan-tweak-tool"

# Correctly determine asset directories for both script and bundled .exe
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

SCRIPT_DIR = os.path.join(base_path, "scripts")
ICON_DIR = os.path.join(base_path, "icons")
TOOLS_DIR = os.path.join(base_path, "tools")

# --- SVG Loading Function ---
def load_svg_icon(filename, size=(20, 20)):
    try:
        path = os.path.join(ICON_DIR, filename)
        if not os.path.exists(path):
            logging.warning(f"Icon file not found: {path}")
            return None
        # In-memory conversion of SVG to PNG
        png_data = svg2png(url=path, output_width=size[0], output_height=size[1])
        image = Image.open(BytesIO(png_data))
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    except Exception as e:
        logging.error(f"Failed to load icon {filename}: {e}")
        return None

# --- Main Application ---
class TweakApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True) # Remove default title bar
        self.title(APP_TITLE); self.geometry(APP_GEOMETRY)
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
        
        self.tweaks = {}; self.tab_tweaks = {}
        self.x = 0; self.y = 0 # For window dragging

        if sys.platform == "win32" and not os.path.isdir(SCRIPT_DIR):
            messagebox.showerror("Fatal Error", f"The '{SCRIPT_DIR}' directory was not found.")
            self.destroy(); return

        self.icons = { "general": load_svg_icon("general.svg"), "power": load_svg_icon("power.svg"), "mouse": load_svg_icon("mouse.svg"), "network": load_svg_icon("network.svg"), "storage": load_svg_icon("storage.svg"), "debloat": load_svg_icon("debloat.svg"), "gpu": load_svg_icon("gpu.svg"), "memory": load_svg_icon("memory.svg"), "clean": load_svg_icon("clean.svg"), "app_icon": load_svg_icon("app_icon.svg", size=(16,16)) }

        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)

        # --- Custom Title Bar ---
        self.title_bar = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color="#212121")
        self.title_bar.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(self.title_bar, text=APP_TITLE, image=self.icons["app_icon"], compound="left", padx=10).pack(side="left")
        ctk.CTkButton(self.title_bar, text="✕", width=30, height=30, command=self.quit_app, fg_color="transparent", hover_color="#B71C1C").pack(side="right")
        ctk.CTkButton(self.title_bar, text="—", width=30, height=30, command=self.iconify_window, fg_color="transparent", hover_color="#555555").pack(side="right")
        self.title_bar.bind("<ButtonPress-1>", self.start_move); self.title_bar.bind("<ButtonRelease-1>", self.stop_move); self.title_bar.bind("<B1-Motion>", self.do_move)
        
        # --- Main Content Frame ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(1, weight=1); self.content_frame.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self.content_frame, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        ctk.CTkLabel(self.sidebar_frame, text="Titan Tweaks", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(self.sidebar_frame, text="Apply Selected", command=self.apply_all_selected_tweaks).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Revert Selected", fg_color="#D32F2F", hover_color="#B71C1C", command=self.revert_all_selected_tweaks).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="About", fg_color="transparent", border_width=2, command=self.show_about).grid(row=5, column=0, padx=20, pady=(10, 20))
        
        self.main_frame = ctk.CTkFrame(self.content_frame, corner_radius=0); self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.tab_view = ctk.CTkTabview(self.main_frame, fg_color="#2B2B2B"); self.tab_view.pack(expand=True, fill='both')
        self.add_tab_with_tweaks("General", self.create_general_tweaks)
        self.add_tab_with_tweaks("Power & CPU", self.create_power_cpu_tweaks)
        self.add_tab_with_tweaks("Input & USB", self.create_kbm_usb_tweaks)
        self.add_tab_with_tweaks("Network", self.create_network_tweaks)
        self.add_tab_with_tweaks("Storage", self.create_storage_tweaks)
        self.add_tab_with_tweaks("Debloat", self.create_debloat_tweaks)
        self.add_tab_with_tweaks("GPU", self.create_gpu_tweaks)
        self.add_tab_with_tweaks("Memory", self.create_memory_tweaks)
        self.add_tab_with_tweaks("PC Clean", self.create_clean_tweaks)

    # --- Window Management Methods ---
    def start_move(self, event): self.x = event.x; self.y = event.y
    def stop_move(self, event): self.x = None; self.y = None
    def do_move(self, event):
        self.geometry(f"+{self.winfo_x() + event.x - self.x}+{self.winfo_y() + event.y - self.y}")
    
    def iconify_window(self): self.iconify()
    def quit_app(self): self.destroy()

    # --- GUI Creation Methods ---
    def add_tab_with_tweaks(self, tab_name, creation_func):
        tab = self.tab_view.add(tab_name)
        tab.grid_columnconfigure(0, weight=1); self.tab_tweaks[tab_name] = []
        scrollable_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scrollable_frame.pack(expand=True, fill='both', padx=5, pady=5)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        select_all_var = tk.BooleanVar()
        ctk.CTkCheckBox(scrollable_frame, text=f"Select All in {tab_name}", variable=select_all_var, command=lambda: self.toggle_all_tweaks(tab_name, select_all_var.get())).pack(anchor='ne', padx=10, pady=5)
        creation_func(scrollable_frame, tab_name)

    def create_general_tweaks(self, parent, tab_name):
        self.add_tweak(parent, tab_name, "timers", "Optimize System Timers", "Disables Dynamic Tick and HPET for better timer consistency.", self.icons["general"])
        self.add_tweak(parent, tab_name, "responsiveness", "Improve System Responsiveness", "Prioritizes foreground apps and optimizes MMCSS for gaming.", self.icons["general"])
        self.add_tweak(parent, tab_name, "timeouts", "Reduce UI & App Timeouts", "Makes the desktop feel snappier by removing menu delays.", self.icons["general"])
        self.add_tweak(parent, tab_name, "fse_and_gamemode", "Apply Fullscreen & Game Mode Optimizations", "Enables Game Mode and applies modern fullscreen optimizations.", self.icons["general"])

    def create_power_cpu_tweaks(self, parent, tab_name):
        self.add_tweak(parent, tab_name, "power_plan", "Create 'Titan' High-Performance Power Plan", "Creates and activates a custom power plan.", self.icons["power"])
        self.add_tweak(parent, tab_name, "cpu_tweaks", "Apply Core CPU Tweaks", "Disables CPU power saving (C-States, Core Parking, Throttling).", self.icons["power"])
        self.add_tweak(parent, tab_name, "disable_mitigations", "Disable Security Mitigations (Advanced)", "Reduces Spectre/Meltdown protection for a performance boost. High risk.", self.icons["power"], is_risky=True)

    def create_kbm_usb_tweaks(self, parent, tab_name):
        self.add_tweak(parent, tab_name, "kbm_settings", "Keyboard & Mouse Optimizations", "Disables mouse acceleration and reduces input delay.", self.icons["mouse"])
        self.add_tweak(parent, tab_name, "disable_usb_powersaving", "Disable USB Power Saving", "Prevents Windows from suspending USB ports.", self.icons["mouse"])

    def create_network_tweaks(self, parent, tab_name):
        self.add_tweak(parent, tab_name, "network_tweaks", "Comprehensive Network Tweaks", "Disables throttling, optimizes TCP/IP, and disables adapter power saving.", self.icons["network"])

    def create_storage_tweaks(self, parent, tab_name):
        self.add_tweak(parent, tab_name, "storage_tweaks", "Storage & NTFS Optimizations", "Disables disk power saving and optimizes the filesystem.", self.icons["storage"])

    def create_debloat_tweaks(self, parent, tab_name):
        self.add_tweak(parent, tab_name, "debloat_tweaks", "Core Debloat (Telemetry, GameDVR)", "Disables non-essential background services and data collection.", self.icons["debloat"])
        self.add_tweak(parent, tab_name, "debloat_services", "Disable Unnecessary Services", "Disables Printing, Maps, and Bluetooth services.", self.icons["debloat"])
        self.add_tweak(parent, tab_name, "debloat_apps", "Uninstall Bloatware Apps", "Removes pre-installed apps like Weather, GetHelp, Solitaire, etc.", self.icons["debloat"])

    def create_gpu_tweaks(self, parent, tab_name):
        gpu_brand = "Unknown"
        try:
            command = "wmic path win32_VideoController get name"
            result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            gpu_name = result.stdout.lower()
            if "nvidia" in gpu_name: gpu_brand = "NVIDIA"
            elif "amd" in gpu_name or "radeon" in gpu_name: gpu_brand = "AMD"
            elif "intel" in gpu_name: gpu_brand = "Intel"
        except Exception as e: logging.error(f"GPU detection failed: {e}")
        
        ctk.CTkLabel(parent, text=f"Detected GPU: {gpu_brand}", font=ctk.CTkFont(weight="bold")).pack(anchor='center', padx=10, pady=10)
        
        if gpu_brand == "NVIDIA":
            self.add_tweak(parent, tab_name, "gpu_nvidia", "Apply NVIDIA Performance Tweaks", "Applies registry tweaks for low latency and disables HDCP.", self.icons["gpu"])
            ctk.CTkButton(parent, text="Download NVIDIA Profile Inspector & Profile", command=self.handle_nvidia_inspector).pack(pady=10)
            ctk.CTkLabel(parent, text="For full optimization, this will download the official tool and the EXM profile. You must then manually import the '.nip' profile file.", wraplength=500).pack(padx=10)
        elif gpu_brand == "AMD":
            self.add_tweak(parent, tab_name, "gpu_amd", "Apply AMD Performance Tweaks", "Applies a comprehensive set of registry tweaks for AMD GPUs.", self.icons["gpu"])
        elif gpu_brand == "Intel":
            self.add_tweak(parent, tab_name, "gpu_intel", "Apply Intel iGPU Tweaks", "Sets dedicated segment size and other tweaks for integrated graphics.", self.icons["gpu"])
        else:
            ctk.CTkLabel(parent, text="Could not automatically detect your GPU brand.").pack(padx=10, pady=10)

    def create_memory_tweaks(self, parent, tab_name):
        ctk.CTkLabel(parent, text="Select your installed RAM amount:", font=ctk.CTkFont(weight="bold")).pack(anchor='w', padx=10, pady=(10,0))
        self.ram_combobox = ctk.CTkComboBox(parent, values=["8GB or less (Enables Compression)", "16GB or more (Disables Compression)"])
        self.ram_combobox.pack(padx=10, pady=5, fill='x')
        ctk.CTkButton(parent, text="Apply Memory Tweaks", command=self.apply_memory_tweaks).pack(pady=10)
        ctk.CTkButton(parent, text="Revert Memory Tweaks", fg_color="#D32F2F", hover_color="#B71C1C", command=self.revert_memory_tweaks).pack(pady=5)
    
    def create_clean_tweaks(self, parent, tab_name):
        ctk.CTkButton(parent, text="Launch Windows Disk Cleanup", command=lambda: os.system('cleanmgr.exe')).pack(pady=10, padx=10, fill='x')
        self.add_tweak(parent, tab_name, "clean_devices", "Clean Old/Unused Device Drivers", "Removes disconnected device driver entries from your system.", self.icons["clean"])

    def add_tweak(self, parent, tab_name, id, text, desc, icon, is_risky=False):
        frame = ctk.CTkFrame(parent); frame.pack(fill='x', padx=10, pady=7)
        frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(frame, image=icon, text="").grid(row=0, column=0, rowspan=2, padx=10, pady=5)
        ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=10, pady=(5,0))
        ctk.CTkLabel(frame, text=desc, wraplength=500, justify='left', text_color="gray60").grid(row=1, column=1, sticky="w", padx=10, pady=(0,5))
        var = tk.BooleanVar()
        switch = ctk.CTkSwitch(frame, text="", variable=var); switch.grid(row=0, column=2, rowspan=2, padx=10)
        self.tweaks[id] = {"var": var, "apply_arg": id, "revert_arg": id, "risky": is_risky}
        self.tab_tweaks[tab_name].append(var)

    def toggle_all_tweaks(self, tab_name, state):
        for var in self.tab_tweaks.get(tab_name, []): var.set(state)

    def execute_master_script(self, script_path, argument):
        if not os.path.exists(script_path): return False, "Master script not found", script_path
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            result = subprocess.run([script_path, argument], shell=True, check=True, capture_output=True, text=True, creationflags=creation_flags)
            return True, result.stdout.strip(), ""
        except subprocess.CalledProcessError as e:
            return False, e.stdout.strip(), e.stderr.strip()
        except Exception as e: return False, "", str(e)

    def execute_tweaks(self, action_type):
        action_key = "apply_arg" if action_type == "Apply" else "revert_arg"
        script_path = os.path.join(SCRIPT_DIR, "apply.cmd" if action_type == "Apply" else "revert.cmd")
        tweaks_to_run = [data for id, data in self.tweaks.items() if data["var"].get()]
        if not tweaks_to_run: messagebox.showinfo("No Selection", "Please select one or more tweaks to perform."); return
        if any(t['risky'] for t in tweaks_to_run) and action_type == "Apply":
            if not messagebox.askyesno("High-Risk Tweak Selected", "You have selected a tweak marked as high-risk.\nThis may expose your system to certain threats in exchange for performance. Are you sure?"): return
        self.update_status(f"Executing {action_type.lower()} operation..."); log_content = f"--- Titan Tweak Tool Log - {action_type} ---"
        for tweak in tweaks_to_run:
            arg = tweak[action_key]
            log_content += f"\n\nRunning '{os.path.basename(script_path)}' with argument '{arg}'..."
            success, stdout, stderr = self.execute_master_script(script_path, arg)
            if success: log_content += f"\n  Status: SUCCESS"; logging.info(f"SUCCESS: {script_path} {arg}");
            else: log_content += f"\n  Status: FAILED"; logging.error(f"FAILED: {script_path} {arg} | Error: {stderr}")
            if stdout: log_content += f"\n  Output: {stdout}"
            if stderr: log_content += f"\n  Error: {stderr}"
        self.show_log_window(log_content); self.update_status("Ready")

    def show_log_window(self, log_content):
        log_window = ctk.CTkToplevel(self); log_window.title("Execution Log"); log_window.geometry("600x400"); log_window.transient(self); log_window.grab_set()
        textbox = ctk.CTkTextbox(log_window, width=600, height=400); textbox.pack(expand=True, fill='both')
        textbox.insert("0.0", log_content); textbox.configure(state="disabled")

    def apply_all_selected_tweaks(self): self.execute_tweaks("Apply")
    def revert_all_selected_tweaks(self): self.execute_tweaks("Revert")
    
    def apply_memory_tweaks(self):
        arg = "ram_high" if "16GB" in self.ram_combobox.get() else "ram_low"
        self.execute_tweaks_by_arg("Apply", arg)
    def revert_memory_tweaks(self):
        self.execute_tweaks_by_arg("Revert", "memory")

    def execute_tweaks_by_arg(self, action_type, arg):
        script_path = os.path.join(SCRIPT_DIR, "apply.cmd" if action_type == "Apply" else "revert.cmd")
        self.update_status(f"Executing {action_type.lower()} operation...")
        log_content = f"--- Titan Tweak Tool Log - {action_type} ---\n\nRunning '{os.path.basename(script_path)}' with argument '{arg}'..."
        success, stdout, stderr = self.execute_master_script(script_path, arg)
        if success: log_content += f"\n  Status: SUCCESS"; logging.info(f"SUCCESS: {script_path} {arg}")
        else: log_content += f"\n  Status: FAILED"; logging.error(f"FAILED: {script_path} {arg} | Error: {stderr}")
        if stdout: log_content += f"\n  Output: {stdout}"
        if stderr: log_content += f"\n  Error: {stderr}"
        self.show_log_window(log_content); self.update_status("Ready")

    def handle_nvidia_inspector(self):
        os.makedirs(TOOLS_DIR, exist_ok=True)
        webbrowser.open("https://github.com/Orbmu2k/nvidiaProfileInspector/releases/download/2.4.0.4/nvidiaProfileInspector.zip")
        webbrowser.open("https://raw.githubusercontent.com/exm4L/EXM-FREE-UTILITY-RESCOURSES/main/EXM_Free_NVPI_V9.nip")
        messagebox.showinfo("NVIDIA Profile Inspector", "Your browser has opened to download two files:\n\n1. nvidiaProfileInspector.zip\n2. EXM_Free_NVPI_V9.nip\n\nInstructions:\n1. Unzip the inspector tool into the 'tools' folder.\n2. Run 'nvidiaProfileInspector.exe'.\n3. Click the 'Import user defined profiles' button.\n4. Select the 'EXM_Free_NVPI_V9.nip' file you downloaded.")
        os.startfile(TOOLS_DIR)

    def show_about(self):
        about_window = ctk.CTkToplevel(self); about_window.title("About"); about_window.geometry("450x300"); about_window.transient(self); about_window.grab_set()
        about_window.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(about_window, text=APP_TITLE, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(about_window, text="A transparent, open-source utility to optimize Windows.", justify='center', wraplength=400).pack(pady=(0, 20))
        info_frame = ctk.CTkFrame(about_window, fg_color="transparent"); info_frame.pack(pady=10)
        ctk.CTkLabel(info_frame, text="Inspired by:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky='e', padx=5)
        ctk.CTkLabel(info_frame, text="IEXM Free Tweaking Utility").grid(row=0, column=1, sticky='w')
        ctk.CTkLabel(info_frame, text="Source Code:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky='e', padx=5)
        link_label = ctk.CTkLabel(info_frame, text=GITHUB_URL, text_color="#6495ED", cursor="hand2"); link_label.grid(row=1, column=1, sticky='w'); link_label.bind("<Button-1>", lambda e: webbrowser.open_new(GITHUB_URL))
        ctk.CTkButton(about_window, text="OK", command=about_window.destroy).pack(pady=(20, 20))

    def update_status(self, message):
        self.status_bar.configure(text=message); self.update_idletasks()

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            if is_admin():
                app = TweakApp()
                app.mainloop()
            else:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            print("This is a Windows-only application.")
    except Exception as e:
        logging.critical(f"A critical error occurred on startup: {e}")
        messagebox.showerror("Startup Error", f"A critical error occurred: {e}\n\nPlease check the titan_tool.log file for more details.")