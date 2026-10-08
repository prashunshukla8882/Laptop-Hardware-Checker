import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform
import os
from datetime import datetime, timedelta
import webbrowser
import threading
import time
import re

class LaptopChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Laptop Hardware Checker V2.0 - Ultimate Edition - By Prashun")
        self.root.geometry("1100x850")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        
        self.text_widgets = {}
        self.is_loading = False
        self.verification_results = {}
        
        self.create_header()
        self.create_footer()
        self.create_notebook()
        
    def get_save_folder(self):
        user_profile = os.environ.get('USERPROFILE', '')
        
        try:
            for folder in os.listdir(user_profile):
                if folder.startswith('OneDrive'):
                    potential_desktop = os.path.join(user_profile, folder, 'Desktop')
                    if os.path.exists(potential_desktop):
                        return potential_desktop
        except:
            pass
        
        regular_desktop = os.path.join(user_profile, 'Desktop')
        if os.path.exists(regular_desktop):
            return regular_desktop
        
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
            winreg.CloseKey(key)
            if os.path.exists(desktop_path):
                return desktop_path
        except:
            pass
        
        documents = os.path.join(user_profile, 'Documents')
        if os.path.exists(documents):
            return documents
        
        return os.getcwd()

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#16213e", pady=15)
        header_frame.pack(fill="x", side="top")
        
        title = tk.Label(
            header_frame, 
            text="💻 LAPTOP HARDWARE CHECKER V2.0",
            font=("Segoe UI", 24, "bold"),
            fg="#00fff5",
            bg="#16213e"
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text="🛡️ ULTIMATE EDITION - Maximum Fraud Detection",
            font=("Segoe UI", 11),
            fg="#e94560",
            bg="#16213e"
        )
        subtitle.pack()
        
        self.loading_frame = tk.Frame(header_frame, bg="#16213e")
        self.loading_frame.pack(pady=10)
        
        self.loading_label = tk.Label(
            self.loading_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            fg="#ffff00",
            bg="#16213e"
        )
        self.loading_label.pack()
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.loading_frame,
            variable=self.progress_var,
            maximum=100,
            length=400,
            mode='determinate'
        )

    def create_footer(self):
        footer_frame = tk.Frame(self.root, bg="#16213e", pady=15, height=70)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        btn_font = ("Segoe UI", 10, "bold")
        
        tk.Button(
            footer_frame, text=" 🔄 REFRESH ", font=btn_font,
            bg="#e94560", fg="white", pady=5, relief="flat",
            cursor="hand2", command=self.refresh_data_threaded
        ).pack(side="left", padx=8, pady=5)
        
        tk.Button(
            footer_frame, text=" 💾 SAVE TXT ", font=btn_font,
            bg="#00aa55", fg="white", pady=5, relief="flat",
            cursor="hand2", command=self.quick_export
        ).pack(side="left", padx=5, pady=5)
        
        tk.Button(
            footer_frame, text=" 🎨 ULTIMATE REPORT ", font=btn_font,
            bg="#9933ff", fg="white", pady=5, relief="flat",
            cursor="hand2", command=self.generate_html_report
        ).pack(side="left", padx=5, pady=5)
        
        tk.Button(
            footer_frame, text=" 🔍 WARRANTY ", font=btn_font,
            bg="#ff8800", fg="white", pady=5, relief="flat",
            cursor="hand2", command=self.check_warranty
        ).pack(side="left", padx=5, pady=5)
        
        tk.Button(
            footer_frame, text=" 📋 COPY ", font=btn_font,
            bg="#0088cc", fg="white", pady=5, relief="flat",
            cursor="hand2", command=self.copy_to_clipboard
        ).pack(side="left", padx=5, pady=5)
        
        tk.Label(
            footer_frame,
            text="💜 Made by PRASHUN 💜",
            font=("Segoe UI", 12, "bold"),
            fg="#00fff5",
            bg="#16213e"
        ).pack(side="right", padx=20, pady=5)

    def create_notebook(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a2e')
        style.configure('TNotebook.Tab', font=('Segoe UI', 9, 'bold'), padding=[10, 5])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ALL TABS including new ones!
        self.tabs = [
            ("💻 System", self.get_system_info),
            ("⚡ CPU", self.get_cpu_info),
            ("🧠 RAM", self.get_ram_info),
            ("💾 Storage", self.get_storage_info),
            ("📊 SMART", self.get_smart_data),           # NEW!
            ("🔋 Battery", self.get_battery_info),
            ("🎮 GPU", self.get_gpu_info),
            ("🌐 Network", self.get_network_info),
            ("🖥️ Display", self.get_display_info),
            ("🎤 Devices", self.get_devices_info),
            ("🪟 Windows", self.get_windows_info),
            ("📜 History", self.get_hardware_history),    # NEW!
            ("🔌 USB Log", self.get_usb_history),         # NEW!
            ("🔍 Verify", self.get_verification_info),
            ("✅ Checklist", self.get_physical_checklist), # NEW!
            ("🌐 Links", self.get_manufacturer_links),     # NEW!
            ("📄 Full", self.get_all_info)
        ]
        
        for tab_name, info_func in self.tabs:
            frame = tk.Frame(self.notebook, bg="#0f0f23")
            self.notebook.add(frame, text=tab_name)
            self.create_info_display(frame, tab_name, info_func)

    def create_info_display(self, parent, tab_name, info_func):
        text_widget = tk.Text(
            parent, font=("Consolas", 11), bg="#0f0f23", fg="#00ff88",
            relief="flat", padx=15, pady=15, wrap="word"
        )
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text_widget.pack(fill="both", expand=True, side="left")
        
        text_widget.tag_configure("red", foreground="#ff4444")
        text_widget.tag_configure("yellow", foreground="#ffcc00")
        text_widget.tag_configure("green", foreground="#00ff88")
        text_widget.tag_configure("cyan", foreground="#00fff5")
        text_widget.tag_configure("header", foreground="#00fff5", font=("Consolas", 12, "bold"))
        
        self.text_widgets[tab_name] = (text_widget, info_func)
        self.load_tab_data_threaded(tab_name)

    def show_loading(self, msg, progress=0):
        self.is_loading = True
        self.loading_label.config(text=msg)
        self.progress_var.set(progress)
        if not self.progress_bar.winfo_ismapped():
            self.progress_bar.pack(pady=5)
        self.root.update_idletasks()

    def hide_loading(self):
        self.is_loading = False
        self.loading_label.config(text="")
        self.progress_var.set(0)
        if self.progress_bar.winfo_ismapped():
            self.progress_bar.pack_forget()
        self.root.update_idletasks()

    def update_progress(self, msg, progress):
        self.root.after(0, lambda m=msg, p=progress: self.show_loading(m, p))

    def load_tab_data_threaded(self, tab_name):
        def load():
            text_widget, info_func = self.text_widgets[tab_name]
            try:
                info = info_func()
                self.root.after(0, lambda: self.update_text_widget(text_widget, info))
            except Exception as ex:
                error_msg = str(ex)
                self.root.after(0, lambda: self.update_text_widget(text_widget, f"Error: {error_msg}"))
        threading.Thread(target=load, daemon=True).start()

    def update_text_widget(self, text_widget, content):
        text_widget.configure(state="normal")
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", content)
        text_widget.configure(state="disabled")

    def refresh_data_threaded(self):
        def refresh():
            self.update_progress("🔄 Refreshing all data...", 0)
            total = len(self.text_widgets)
            for i, tab_name in enumerate(self.text_widgets):
                text_widget, info_func = self.text_widgets[tab_name]
                progress = int((i + 1) / total * 100)
                self.update_progress(f"🔄 Refreshing {tab_name}...", progress)
                try:
                    info = info_func()
                    self.root.after(0, lambda tw=text_widget, inf=info: self.update_text_widget(tw, inf))
                except:
                    pass
                time.sleep(0.1)
            self.root.after(0, self.hide_loading)
            self.root.after(0, lambda: messagebox.showinfo("Done", "✅ All data refreshed!"))
        threading.Thread(target=refresh, daemon=True).start()

    def quick_export(self):
        def export():
            try:
                self.update_progress("💾 Saving report...", 50)
                save_folder = self.get_save_folder()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_folder, f"Laptop_Ultimate_Report_{timestamp}.txt")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.get_all_info())
                
                self.root.after(0, self.hide_loading)
                
                if os.path.exists(filename):
                    self.root.after(0, lambda: messagebox.showinfo("✅ Saved!", f"File saved to:\n\n{filename}"))
                    subprocess.Popen(['explorer', '/select,', filename])
            except Exception as ex:
                error_msg = str(ex)
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed: {error_msg}"))
        threading.Thread(target=export, daemon=True).start()

    def copy_to_clipboard(self):
        try:
            self.show_loading("📋 Copying...", 50)
            self.root.clipboard_clear()
            self.root.clipboard_append(self.get_all_info())
            self.hide_loading()
            messagebox.showinfo("📋 Copied!", "Report copied to clipboard!")
        except Exception as ex:
            self.hide_loading()
            messagebox.showerror("Error", str(ex))

    def check_warranty(self):
        try:
            manufacturer = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Manufacturer").lower()
            serial = self.run_powershell("(Get-WmiObject Win32_BIOS).SerialNumber")
            
            urls = {
                "dell": "https://www.dell.com/support/home/en-us/product-support/servicetag/",
                "hp": "https://support.hp.com/us-en/check-warranty",
                "lenovo": "https://pcsupport.lenovo.com/us/en/warrantylookup",
                "asus": "https://www.asus.com/support/warranty-status-inquiry/",
                "acer": "https://www.acer.com/ac/en/US/content/support"
            }
            
            url = next((link for brand, link in urls.items() if brand in manufacturer), None)
            
            if url:
                messagebox.showinfo("🔍 Warranty", f"Manufacturer: {manufacturer.title()}\nSerial: {serial}\n\nOpening...")
                webbrowser.open(url)
            else:
                messagebox.showinfo("🔍 Warranty", f"Manufacturer: {manufacturer}\nSerial: {serial}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def run_powershell(self, command):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                ['powershell', '-Command', command],
                capture_output=True, text=True, timeout=30,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            output = result.stdout.strip()
            return output if output else "N/A"
        except:
            return "N/A"

    # ==================== SMART DATA (SSD/HDD Health) ====================
    def get_smart_data(self):
        disk_model = self.run_powershell("(Get-WmiObject Win32_DiskDrive | Select-Object -First 1).Model")
        disk_serial = self.run_powershell("(Get-WmiObject Win32_DiskDrive | Select-Object -First 1).SerialNumber")
        disk_size = self.run_powershell("[math]::Round((Get-WmiObject Win32_DiskDrive | Select-Object -First 1).Size / 1GB, 2)")
        disk_interface = self.run_powershell("(Get-WmiObject Win32_DiskDrive | Select-Object -First 1).InterfaceType")
        disk_status = self.run_powershell("(Get-WmiObject Win32_DiskDrive | Select-Object -First 1).Status")
        
        # Get SMART data using PowerShell
        smart_data = self.run_powershell("""
            try {
                $disk = Get-PhysicalDisk | Select-Object -First 1
                if ($disk) {
                    "HealthStatus: $($disk.HealthStatus)"
                    "OperationalStatus: $($disk.OperationalStatus)"
                    "MediaType: $($disk.MediaType)"
                    "BusType: $($disk.BusType)"
                    "FirmwareVersion: $($disk.FirmwareVersion)"
                    "SpindleSpeed: $($disk.SpindleSpeed)"
                } else {
                    "N/A"
                }
            } catch { "N/A" }
        """)
        
        # Get Power On Hours (if available)
        power_on_hours = self.run_powershell("""
            try {
                $reliability = Get-WmiObject -Namespace root/wmi -Class MSStorageDriver_FailurePredictData -EA SilentlyContinue
                if ($reliability) { "Data Available" } else { "Requires Admin Rights or CrystalDiskInfo" }
            } catch { "Requires CrystalDiskInfo for detailed SMART" }
        """)
        
        # Get disk reliability
        disk_reliability = self.run_powershell("""
            try {
                $disk = Get-PhysicalDisk | Select-Object -First 1
                $reliability = Get-StorageReliabilityCounter -PhysicalDisk $disk -EA SilentlyContinue
                if ($reliability) {
                    "ReadErrors: $($reliability.ReadErrorsTotal)"
                    "WriteErrors: $($reliability.WriteErrorsTotal)"
                    "Temperature: $($reliability.Temperature) C"
                    "Wear: $($reliability.Wear)"
                    "PowerOnHours: $($reliability.PowerOnHours)"
                } else { "N/A" }
            } catch { "Run as Admin for full data" }
        """)
        
        # Detect SSD or HDD
        is_ssd = "SSD" in disk_model.upper() or "NVME" in disk_model.upper() or "SOLID" in disk_model.upper()
        disk_type = "⚡ SSD/NVMe" if is_ssd else "💽 HDD"
        
        # Check if disk is healthy
        health_warning = ""
        if "Healthy" in smart_data:
            health_warning = "✅ DISK IS HEALTHY"
        elif "Warning" in smart_data or "Degraded" in smart_data:
            health_warning = "⚠️ WARNING: DISK MAY HAVE ISSUES!"
        elif "Unhealthy" in smart_data:
            health_warning = "🔴 CRITICAL: DISK IS FAILING!"
        else:
            health_warning = "ℹ️ Run as Administrator for full health check"
        
        return f"""
{'='*65}
       📊 SMART DATA - DISK HEALTH ANALYSIS
{'='*65}

  {health_warning}

{'='*65}
       DISK INFORMATION
{'='*65}

  Model          : {disk_model}
  Serial Number  : {disk_serial}
  Size           : {disk_size} GB
  Type           : {disk_type}
  Interface      : {disk_interface}
  Status         : {disk_status}

{'='*65}
       SMART STATUS
{'='*65}

{smart_data}

{'='*65}
       RELIABILITY DATA
{'='*65}

{disk_reliability}

{'='*65}
       ⚠️ FRAUD DETECTION NOTES
{'='*65}

  🔍 What to look for:
  
  • Power-On Hours > 5000    = Heavy use (suspicious if sold as "new")
  • Power-On Hours > 20000   = Very old drive
  • Read/Write Errors > 0    = Drive may be failing
  • Temperature > 50°C       = Overheating issue
  • Wear > 10%               = SSD wearing out
  
  🛡️ RECOMMENDATION:
  
  For detailed SMART data, install CrystalDiskInfo (free):
  https://crystalmark.info/en/software/crystaldiskinfo/
  
  It shows:
  • Exact Power-On Hours
  • Total Data Written
  • Reallocated Sectors
  • Health Percentage

{'='*65}
"""

    # ==================== HARDWARE HISTORY (Event Logs) ====================
    def get_hardware_history(self):
        # Get driver install dates
        driver_installs = self.run_powershell("""
            Get-WinEvent -LogName System -FilterXPath "*[System[EventID=20 or EventID=7045]]" -MaxEvents 20 -EA SilentlyContinue | 
            Select-Object TimeCreated, Message | 
            ForEach-Object { "$($_.TimeCreated.ToString('yyyy-MM-dd HH:mm')) | $($_.Message.Substring(0, [Math]::Min(60, $_.Message.Length)))..." }
        """)
        
        # Get hardware change events
        hardware_changes = self.run_powershell("""
            Get-WinEvent -LogName System -FilterXPath "*[System[Provider[@Name='Microsoft-Windows-Kernel-PnP']]]" -MaxEvents 15 -EA SilentlyContinue |
            Select-Object TimeCreated, Message |
            ForEach-Object { "$($_.TimeCreated.ToString('yyyy-MM-dd HH:mm')) | $($_.Message.Substring(0, [Math]::Min(70, $_.Message.Length)))..." }
        """)
        
        # Get system startup count
        startup_events = self.run_powershell("""
            $startups = (Get-WinEvent -LogName System -FilterXPath "*[System[EventID=6005]]" -EA SilentlyContinue).Count
            "Total recorded startups: $startups"
        """)
        
        # Get last shutdown time
        last_shutdown = self.run_powershell("""
            $shutdown = Get-WinEvent -LogName System -FilterXPath "*[System[EventID=6006]]" -MaxEvents 1 -EA SilentlyContinue
            if ($shutdown) { $shutdown.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss') } else { "N/A" }
        """)
        
        # Get Windows install date
        windows_install = self.run_powershell("""
            $os = Get-WmiObject Win32_OperatingSystem
            $installDate = $os.ConvertToDateTime($os.InstallDate)
            $installDate.ToString('yyyy-MM-dd HH:mm:ss')
        """)
        
        # Get BIOS date
        bios_date = self.run_powershell("""
            $bios = Get-WmiObject Win32_BIOS
            if ($bios.ReleaseDate) {
                $date = [Management.ManagementDateTimeConverter]::ToDateTime($bios.ReleaseDate)
                $date.ToString('yyyy-MM-dd')
            } else { "N/A" }
        """)
        
        # Get recent program installs
        recent_installs = self.run_powershell("""
            Get-WinEvent -LogName Application -FilterXPath "*[System[EventID=11707 or EventID=1033]]" -MaxEvents 10 -EA SilentlyContinue |
            Select-Object TimeCreated, Message |
            ForEach-Object { "$($_.TimeCreated.ToString('yyyy-MM-dd')) | $($_.Message.Substring(0, [Math]::Min(50, $_.Message.Length)))..." }
        """)
        
        # Analyze dates for fraud
        fraud_warning = ""
        try:
            # Parse BIOS date
            if bios_date != "N/A":
                bios_year = int(bios_date.split('-')[0])
                current_year = datetime.now().year
                laptop_age = current_year - bios_year
                
                # Parse Windows install
                if windows_install != "N/A":
                    install_date = datetime.strptime(windows_install.split(' ')[0], '%Y-%m-%d')
                    days_since_install = (datetime.now() - install_date).days
                    
                    if days_since_install < 7 and laptop_age > 1:
                        fraud_warning = """
  🔴 MAJOR RED FLAG DETECTED!
  
  ⚠️ Windows was installed VERY RECENTLY ({} days ago)
  ⚠️ But laptop BIOS is from {} ({} years old)
  
  This suggests:
  • Fresh OS install to hide usage history
  • Possible refurbished unit
  • Seller may be hiding something!
  
  👉 ASK SELLER: Why was Windows reinstalled?
""".format(days_since_install, bios_year, laptop_age)
                    elif days_since_install < 30 and laptop_age > 1:
                        fraud_warning = """
  ⚠️ WARNING: Recent Windows Install Detected
  
  • Windows installed {} days ago
  • Laptop is approximately {} years old
  
  This MIGHT be normal, but ask seller for reason.
""".format(days_since_install, laptop_age)
                    else:
                        fraud_warning = """
  ✅ Timeline looks consistent
  
  • Laptop age: ~{} years
  • Windows age: {} days
  • No obvious timeline manipulation detected
""".format(laptop_age, days_since_install)
        except:
            fraud_warning = "  ℹ️ Could not analyze timeline automatically"
        
        return f"""
{'='*65}
       📜 HARDWARE & SYSTEM HISTORY
{'='*65}

  🔍 This reveals the REAL history of this laptop!

{'='*65}
       ⚠️ FRAUD ANALYSIS
{'='*65}
{fraud_warning}

{'='*65}
       KEY DATES
{'='*65}

  BIOS Release Date      : {bios_date}
  Windows Install Date   : {windows_install}
  Last Shutdown          : {last_shutdown}
  {startup_events}

{'='*65}
       RECENT HARDWARE CHANGES
{'='*65}

{hardware_changes if hardware_changes != "N/A" else "  No recent hardware changes detected"}

{'='*65}
       RECENT DRIVER INSTALLS
{'='*65}

{driver_installs if driver_installs != "N/A" else "  No recent driver installs found"}

{'='*65}
       RECENT PROGRAM INSTALLS
{'='*65}

{recent_installs if recent_installs != "N/A" else "  No recent program installs found"}

{'='*65}
       💡 WHAT TO LOOK FOR
{'='*65}

  🔴 RED FLAGS:
  • Fresh Windows install on old laptop
  • Many recent driver installs (hardware replaced?)
  • Low startup count on old laptop (odometer reset?)
  
  ✅ GOOD SIGNS:
  • Consistent timeline (old laptop, old Windows)
  • Gradual program installs over time
  • Normal startup count for age

{'='*65}
"""

    # ==================== USB HISTORY ====================
    def get_usb_history(self):
        # Get USB device history from registry
        usb_devices = self.run_powershell("""
            Get-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\USB\\*\\*' -EA SilentlyContinue | 
            Select-Object -First 20 |
            ForEach-Object { 
                $friendlyName = if ($_.FriendlyName) { $_.FriendlyName } else { $_.DeviceDesc }
                if ($friendlyName) { "  • $friendlyName" }
            }
        """)
        
        # Get USB storage devices
        usb_storage = self.run_powershell("""
            Get-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR\\*\\*' -EA SilentlyContinue | 
            ForEach-Object { 
                $name = if ($_.FriendlyName) { $_.FriendlyName } else { "USB Storage Device" }
                "  • $name"
            }
        """)
        
        # Get current USB devices
        current_usb = self.run_powershell("""
            Get-WmiObject Win32_USBHub | ForEach-Object {
                "  • $($_.Description) - $($_.DeviceID.Substring(0, [Math]::Min(40, $_.DeviceID.Length)))..."
            }
        """)
        
        # Get Bluetooth devices
        bluetooth_devices = self.run_powershell("""
            Get-WmiObject Win32_PnPEntity | Where-Object { $_.Name -like '*Bluetooth*' } |
            ForEach-Object { "  • $($_.Name)" }
        """)
        
        return f"""
{'='*65}
       🔌 USB & DEVICE CONNECTION HISTORY
{'='*65}

  🔍 Shows all devices that have been connected to this laptop.
  
  ⚠️ Why this matters:
  • Shows what peripherals were used
  • External drives may indicate data transfer
  • Can reveal if laptop was used commercially

{'='*65}
       CURRENT USB DEVICES
{'='*65}

{current_usb if current_usb != "N/A" else "  No USB devices currently connected"}

{'='*65}
       USB STORAGE HISTORY
{'='*65}

{usb_storage if usb_storage != "N/A" else "  No USB storage history found"}

{'='*65}
       ALL USB DEVICE HISTORY
{'='*65}

{usb_devices if usb_devices != "N/A" else "  No USB history found"}

{'='*65}
       BLUETOOTH DEVICES
{'='*65}

{bluetooth_devices if bluetooth_devices != "N/A" else "  No Bluetooth devices found"}

{'='*65}
       💡 ANALYSIS TIPS
{'='*65}

  Look for:
  • Many USB storage devices = Heavy file transfer use
  • Docking stations = Corporate/Office use
  • Multiple keyboards/mice = Shared use or repairs
  • Forensic tools = Previous analysis (why?)

{'='*65}
"""

    # ==================== PHYSICAL INSPECTION CHECKLIST ====================
    def get_physical_checklist(self):
        return f"""
{'='*65}
       ✅ PHYSICAL INSPECTION CHECKLIST
{'='*65}

  🔍 Software can only detect so much!
  Use this checklist for manual inspection.

{'='*65}
       📋 BODY & EXTERIOR
{'='*65}

  [ ] Check for scratches, dents, cracks
  [ ] Look for mismatched screws (different sizes = opened before)
  [ ] Check if stickers are original or peeling
  [ ] Look for paint touch-ups or respray
  [ ] Check rubber feet (worn = heavy use, new = replaced)
  [ ] Inspect hinges for looseness or creaking
  [ ] Check USB ports for wear/damage
  [ ] Inspect charging port for damage

{'='*65}
       🖥️ SCREEN CHECK
{'='*65}

  [ ] Run dead pixel test (display solid colors)
      → Open: https://www.jscreenfix.com/fix.html
  [ ] Check for backlight bleed (show black screen in dark room)
  [ ] Look for scratches on screen
  [ ] Check for screen burn-in (ghost images)
  [ ] Verify touch works (if touchscreen)
  [ ] Test screen at all angles

{'='*65}
       ⌨️ KEYBOARD & TRACKPAD
{'='*65}

  [ ] Test EVERY key (use: https://www.keyboardtester.com/)
  [ ] Check for sticky or mushy keys
  [ ] Look for shiny/worn keycaps (heavy use)
  [ ] Test trackpad gestures (2-finger scroll, etc.)
  [ ] Check trackpad click buttons
  [ ] Test keyboard backlight (if available)

{'='*65}
       🔊 AUDIO & PORTS
{'='*65}

  [ ] Test both speakers (left and right)
  [ ] Test headphone jack
  [ ] Test microphone
  [ ] Test webcam
  [ ] Test all USB ports with a device
  [ ] Test HDMI/DisplayPort output
  [ ] Test SD card slot (if available)

{'='*65}
       🔋 BATTERY TEST
{'='*65}

  [ ] Unplug and check battery drain rate
  [ ] Charge from 0-100% and note time
  [ ] Check if battery is bulging (DANGER!)
  [ ] Verify battery holds charge for expected time
  [ ] Check charging cable for damage

{'='*65}
       🌡️ THERMAL TEST
{'='*65}

  [ ] Run a game or video for 15 minutes
  [ ] Check for excessive heat
  [ ] Listen for loud fan noise
  [ ] Check for thermal throttling (CPU slows down)
  [ ] Feel bottom of laptop for hot spots

{'='*65}
       📡 CONNECTIVITY
{'='*65}

  [ ] Test WiFi connection and speed
  [ ] Test Bluetooth pairing
  [ ] Test Ethernet port (if available)
  [ ] Check signal strength vs other devices

{'='*65}
       📝 DOCUMENTATION CHECK
{'='*65}

  [ ] Ask for original purchase invoice
  [ ] Verify serial number matches invoice
  [ ] Check warranty status online
  [ ] Ask for reason of selling
  [ ] Ask about any repairs done

{'='*65}
       🔴 RED FLAGS - WALK AWAY IF:
{'='*65}

  ❌ Serial number scratched/removed
  ❌ Seller refuses to show invoice
  ❌ Mismatched screws on bottom
  ❌ Battery is swollen
  ❌ Screen has dead pixels
  ❌ Keys are sticky or not working
  ❌ WiFi/Bluetooth not working
  ❌ Strange noises from inside

{'='*65}
       🌐 USEFUL TEST LINKS
{'='*65}

  Dead Pixel Test: https://www.jscreenfix.com/fix.html
  Keyboard Test:   https://www.keyboardtester.com/
  Speed Test:      https://www.speedtest.net/
  Battery Test:    https://www.batterybenchmark.com/

{'='*65}
"""

    # ==================== MANUFACTURER LINKS ====================
    def get_manufacturer_links(self):
        manufacturer = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Manufacturer")
        model = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Model")
        serial = self.run_powershell("(Get-WmiObject Win32_BIOS).SerialNumber")
        
        return f"""
{'='*65}
       🌐 MANUFACTURER VERIFICATION LINKS
{'='*65}

  Your Laptop:
  Manufacturer : {manufacturer}
  Model        : {model}
  Serial       : {serial}

{'='*65}
       🔍 WARRANTY & SERIAL VERIFICATION
{'='*65}

  Use these links to verify your laptop with the manufacturer.
  Enter the serial number to check:
  
  ✅ Warranty status
  ✅ Original specs
  ✅ If serial is legitimate
  ✅ Repair history (sometimes)

{'='*65}
       DELL
{'='*65}

  Warranty Check:
  https://www.dell.com/support/home/en-us/product-support/servicetag/{serial}
  
  General Support:
  https://www.dell.com/support/home

{'='*65}
       HP
{'='*65}

  Warranty Check:
  https://support.hp.com/us-en/check-warranty
  
  Serial Lookup:
  https://partsurfer.hp.com/

{'='*65}
       LENOVO
{'='*65}

  Warranty Check:
  https://pcsupport.lenovo.com/us/en/warrantylookup
  
  Parts Lookup:
  https://support.lenovo.com/partslookup

{'='*65}
       ASUS
{'='*65}

  Warranty Check:
  https://www.asus.com/support/warranty-status-inquiry/
  
  General Support:
  https://www.asus.com/support/

{'='*65}
       ACER
{'='*65}

  Warranty Check:
  https://www.acer.com/ac/en/US/content/support
  
  Serial Verification:
  https://www.acer.com/worldwide/support/

{'='*65}
       MICROSOFT SURFACE
{'='*65}

  Device Service:
  https://account.microsoft.com/devices

{'='*65}
       🛡️ WHAT TO VERIFY
{'='*65}

  When you enter serial number, check:
  
  [ ] Serial is recognized (not fake)
  [ ] Warranty dates make sense
  [ ] Model matches what seller claims
  [ ] Check if reported stolen (some brands)
  [ ] Original specs match current hardware

{'='*65}
       ⚠️ RED FLAGS
{'='*65}

  🔴 Serial not found = Fake serial / Modified BIOS
  🔴 Warranty expired years ago but sold as "new"
  🔴 Model shown differs from seller's claim
  🔴 Serial reported as stolen

{'='*65}
       💡 PRO TIP
{'='*65}

  📞 CALL THE MANUFACTURER!
  
  If something seems off, call support:
  • Dell: 1-800-624-9897
  • HP: 1-800-474-6836  
  • Lenovo: 1-855-253-6686
  • ASUS: 1-812-282-2787
  • Acer: 1-866-695-2237
  
  Tell them the serial number and ask:
  "Can you verify this serial and original specs?"

{'='*65}
"""

    # ==================== ENHANCED VERIFICATION ====================
    def perform_verification(self):
        results = {
            'checks': [],
            'score': 100,
            'original_count': 0,
            'suspicious_count': 0,
            'replaced_count': 0,
            'critical_flags': []
        }
        
        manufacturer = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Manufacturer").upper()
        model = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Model")
        bios_serial = self.run_powershell("(Get-WmiObject Win32_BIOS).SerialNumber")
        chassis_serial = self.run_powershell("(Get-WmiObject Win32_SystemEnclosure).SerialNumber")
        mb_serial = self.run_powershell("(Get-WmiObject Win32_BaseBoard).SerialNumber")
        
        # 1. SERIAL NUMBER CONSISTENCY
        serials_match = bios_serial == chassis_serial or bios_serial == mb_serial
        if serials_match and bios_serial != "N/A" and bios_serial != "":
            results['checks'].append({
                'component': 'Serial Numbers',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'BIOS and Chassis serials match: {bios_serial}',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif bios_serial == "N/A" or chassis_serial == "N/A" or bios_serial == "" or bios_serial == "To Be Filled By O.E.M.":
            results['checks'].append({
                'component': 'Serial Numbers',
                'status': 'SUSPICIOUS',
                'color': 'red',
                'details': f'Serial number is missing or generic: {bios_serial}',
                'icon': '🔴'
            })
            results['critical_flags'].append("Missing/Generic serial number - Possible BIOS tampering!")
            results['replaced_count'] += 1
            results['score'] -= 20
        else:
            results['checks'].append({
                'component': 'Serial Numbers',
                'status': 'MISMATCH',
                'color': 'red',
                'details': f'BIOS: {bios_serial} vs Chassis: {chassis_serial}',
                'icon': '🔴'
            })
            results['critical_flags'].append("Serial numbers don't match - Motherboard may be replaced!")
            results['replaced_count'] += 1
            results['score'] -= 15
        
        # 2. BIOS DATE vs WINDOWS INSTALL DATE
        bios_date = self.run_powershell("""
            $bios = Get-WmiObject Win32_BIOS
            if ($bios.ReleaseDate) {
                $date = [Management.ManagementDateTimeConverter]::ToDateTime($bios.ReleaseDate)
                $date.ToString('yyyy-MM-dd')
            } else { "N/A" }
        """)
        
        windows_install = self.run_powershell("""
            $os = Get-WmiObject Win32_OperatingSystem
            $installDate = $os.ConvertToDateTime($os.InstallDate)
            $installDate.ToString('yyyy-MM-dd')
        """)
        
        try:
            if bios_date != "N/A" and windows_install != "N/A":
                bios_year = int(bios_date.split('-')[0])
                install_date = datetime.strptime(windows_install, '%Y-%m-%d')
                days_since_install = (datetime.now() - install_date).days
                laptop_age_years = datetime.now().year - bios_year
                
                if days_since_install < 7 and laptop_age_years > 1:
                    results['checks'].append({
                        'component': 'OS Install Timeline',
                        'status': 'CRITICAL FLAG',
                        'color': 'red',
                        'details': f'Windows installed {days_since_install} days ago on {laptop_age_years} year old laptop!',
                        'icon': '🔴'
                    })
                    results['critical_flags'].append(f"Fresh Windows install ({days_since_install} days) on old laptop ({laptop_age_years} years) - HIDING HISTORY!")
                    results['replaced_count'] += 1
                    results['score'] -= 25
                elif days_since_install < 30 and laptop_age_years > 2:
                    results['checks'].append({
                        'component': 'OS Install Timeline',
                        'status': 'SUSPICIOUS',
                        'color': 'yellow',
                        'details': f'Windows installed {days_since_install} days ago on {laptop_age_years} year old laptop',
                        'icon': '⚠️'
                    })
                    results['suspicious_count'] += 1
                    results['score'] -= 10
                else:
                    results['checks'].append({
                        'component': 'OS Install Timeline',
                        'status': 'NORMAL',
                        'color': 'green',
                        'details': f'Windows age ({days_since_install} days) reasonable for laptop age ({laptop_age_years} years)',
                        'icon': '✅'
                    })
                    results['original_count'] += 1
        except:
            pass
        
        # 3. RAM VERIFICATION
        ram_info = self.run_powershell("""
            Get-WmiObject Win32_PhysicalMemory | ForEach-Object {
                "$($_.Manufacturer)|$($_.PartNumber)|$($_.SerialNumber)|$($_.Capacity)"
            }
        """)
        
        oem_ram = {
            'DELL': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'KINGSTON'],
            'HP': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'RAMAXEL'],
            'LENOVO': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'RAMAXEL'],
            'ASUS': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'KINGSTON'],
            'ACER': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'KINGSTON'],
        }
        
        aftermarket_ram = ['CORSAIR', 'G.SKILL', 'GSKILL', 'TEAMGROUP', 'PATRIOT', 'PNY', 'ADATA', 'CRUCIAL']
        
        expected_ram_brands = oem_ram.get(manufacturer.split()[0], ['SAMSUNG', 'SK HYNIX', 'MICRON'])
        
        ram_sticks = ram_info.strip().split('\n') if ram_info != "N/A" else []
        ram_is_oem = True
        ram_manufacturers = []
        is_aftermarket = False
        
        for stick in ram_sticks:
            if '|' in stick:
                parts = stick.split('|')
                ram_mfr = parts[0].upper() if parts[0] else "UNKNOWN"
                ram_manufacturers.append(ram_mfr)
                
                if any(am in ram_mfr for am in aftermarket_ram):
                    is_aftermarket = True
                    ram_is_oem = False
                elif not any(oem in ram_mfr for oem in expected_ram_brands) and ram_mfr not in ['', 'UNKNOWN', 'N/A']:
                    ram_is_oem = False
        
        if is_aftermarket:
            results['checks'].append({
                'component': 'RAM Modules',
                'status': 'REPLACED',
                'color': 'red',
                'details': f'Aftermarket RAM detected: {", ".join(set(ram_manufacturers))}',
                'icon': '🔴'
            })
            results['replaced_count'] += 1
            results['score'] -= 10
        elif ram_is_oem and ram_manufacturers:
            results['checks'].append({
                'component': 'RAM Modules',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'OEM RAM detected: {", ".join(set(ram_manufacturers))}',
                'icon': '✅'
            })
            results['original_count'] += 1
        else:
            results['checks'].append({
                'component': 'RAM Modules',
                'status': 'UNKNOWN',
                'color': 'yellow',
                'details': f'Could not verify RAM manufacturer: {", ".join(set(ram_manufacturers))}',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
            results['score'] -= 5
        
        # 4. STORAGE VERIFICATION
        disk_info = self.run_powershell("""
            Get-WmiObject Win32_DiskDrive | Select-Object -First 1 | ForEach-Object {
                "$($_.Model)|$($_.SerialNumber)|$($_.InterfaceType)"
            }
        """)
        
        oem_storage = ['SAMSUNG', 'TOSHIBA', 'KIOXIA', 'SK HYNIX', 'HYNIX', 'INTEL', 'SANDISK', 'WD', 'WESTERN DIGITAL', 'LITEON', 'MICRON']
        aftermarket_storage = ['CRUCIAL', 'ADATA', 'PNY', 'TEAMGROUP', 'PATRIOT', 'CORSAIR', 'SEAGATE', 'TRANSCEND', 'KINGSTON']
        
        if disk_info != "N/A" and '|' in disk_info:
            disk_model = disk_info.split('|')[0].upper()
            
            is_aftermarket_ssd = any(am in disk_model for am in aftermarket_storage)
            is_oem_storage = any(oem in disk_model for oem in oem_storage)
            
            if is_aftermarket_ssd:
                results['checks'].append({
                    'component': 'Storage Drive',
                    'status': 'REPLACED',
                    'color': 'red',
                    'details': f'Aftermarket SSD detected: {disk_model}',
                    'icon': '🔴'
                })
                results['replaced_count'] += 1
                results['score'] -= 10
            elif is_oem_storage:
                results['checks'].append({
                    'component': 'Storage Drive',
                    'status': 'ORIGINAL',
                    'color': 'green',
                    'details': f'OEM Storage: {disk_model}',
                    'icon': '✅'
                })
                results['original_count'] += 1
            else:
                results['checks'].append({
                    'component': 'Storage Drive',
                    'status': 'UNKNOWN',
                    'color': 'yellow',
                    'details': f'Unknown brand: {disk_model}',
                    'icon': '⚠️'
                })
                results['suspicious_count'] += 1
                results['score'] -= 5
        
        # 5. BATTERY VERIFICATION
        battery_health = self.run_powershell("""
            try {
                $f = (Get-WmiObject -Namespace "root/WMI" -Class "BatteryFullChargedCapacity" -EA SilentlyContinue).FullChargedCapacity
                $d = (Get-WmiObject -Namespace "root/WMI" -Class "BatteryStaticData" -EA SilentlyContinue).DesignedCapacity
                if ($f -and $d -and $d -gt 0) { [math]::Round(($f / $d) * 100, 1) } else { "N/A" }
            } catch { "N/A" }
        """)
        
        battery_cycles = self.run_powershell("(Get-WmiObject -Namespace 'root/WMI' -Class 'BatteryCycleCount' -EA SilentlyContinue).CycleCount")
        
        try:
            health_val = float(battery_health) if battery_health != "N/A" else 0
            cycles_val = int(battery_cycles) if battery_cycles != "N/A" else 0
            laptop_age_years = datetime.now().year - int(bios_date.split('-')[0]) if bios_date != "N/A" else 0
        except:
            health_val = 0
            cycles_val = 0
            laptop_age_years = 0
        
        # Battery on old laptop with > 95% health and < 50 cycles = likely replaced
        if health_val > 95 and cycles_val < 50 and laptop_age_years > 2:
            results['checks'].append({
                'component': 'Battery',
                'status': 'LIKELY REPLACED',
                'color': 'yellow',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. New battery on {laptop_age_years} year old laptop.',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
            results['score'] -= 5
        elif health_val >= 80:
            results['checks'].append({
                'component': 'Battery',
                'status': 'GOOD',
                'color': 'green',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. Normal condition.',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif health_val >= 50:
            results['checks'].append({
                'component': 'Battery',
                'status': 'WORN',
                'color': 'yellow',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. Battery is worn.',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
        elif health_val > 0:
            results['checks'].append({
                'component': 'Battery',
                'status': 'DEGRADED',
                'color': 'red',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. Battery needs replacement.',
                'icon': '🔴'
            })
            results['replaced_count'] += 1
            results['score'] -= 10
        
        # 6. BIOS VENDOR CHECK
        bios_vendor = self.run_powershell("(Get-WmiObject Win32_BIOS).Manufacturer").upper()
        
        legit_bios = ['AMERICAN MEGATRENDS', 'AMI', 'INSYDE', 'PHOENIX', 'DELL', 'HP', 'LENOVO', 'ASUS', 'ACER']
        bios_legit = any(b in bios_vendor for b in legit_bios)
        
        if bios_legit:
            results['checks'].append({
                'component': 'BIOS/Firmware',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'Legitimate BIOS vendor: {bios_vendor}',
                'icon': '✅'
            })
            results['original_count'] += 1
        else:
            results['checks'].append({
                'component': 'BIOS/Firmware',
                'status': 'SUSPICIOUS',
                'color': 'red',
                'details': f'Unknown BIOS vendor: {bios_vendor}. May be modified!',
                'icon': '🔴'
            })
            results['critical_flags'].append("Unknown BIOS vendor - Possible firmware modification!")
            results['replaced_count'] += 1
            results['score'] -= 15
        
        # 7. DISK HEALTH CHECK
        disk_health = self.run_powershell("""
            try {
                $disk = Get-PhysicalDisk | Select-Object -First 1
                if ($disk) { $disk.HealthStatus } else { "N/A" }
            } catch { "N/A" }
        """)
        
        if disk_health == "Healthy":
            results['checks'].append({
                'component': 'Disk Health (SMART)',
                'status': 'HEALTHY',
                'color': 'green',
                'details': 'Disk reports healthy status',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif disk_health in ["Warning", "Degraded"]:
            results['checks'].append({
                'component': 'Disk Health (SMART)',
                'status': 'WARNING',
                'color': 'yellow',
                'details': f'Disk health: {disk_health}. Drive may be failing!',
                'icon': '⚠️'
            })
            results['critical_flags'].append("Disk showing warning signs - May fail soon!")
            results['suspicious_count'] += 1
            results['score'] -= 15
        elif disk_health == "Unhealthy":
            results['checks'].append({
                'component': 'Disk Health (SMART)',
                'status': 'FAILING',
                'color': 'red',
                'details': 'Disk is UNHEALTHY! Drive failure imminent!',
                'icon': '🔴'
            })
            results['critical_flags'].append("DISK IS FAILING! Do not buy!")
            results['replaced_count'] += 1
            results['score'] -= 30
        else:
            results['checks'].append({
                'component': 'Disk Health (SMART)',
                'status': 'UNKNOWN',
                'color': 'yellow',
                'details': 'Could not read disk health. Run as Admin.',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
        
        # 8. NETWORK ADAPTER CHECK
        network_adapter = self.run_powershell("""
            Get-WmiObject Win32_NetworkAdapter | Where-Object {$_.PhysicalAdapter -and $_.MACAddress} |
            Select-Object -First 1 | ForEach-Object { $_.Name }
        """)
        
        oem_network = ['INTEL', 'REALTEK', 'QUALCOMM', 'BROADCOM', 'KILLER', 'MEDIATEK']
        
        if any(oem in network_adapter.upper() for oem in oem_network):
            results['checks'].append({
                'component': 'Network Adapter',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'Standard OEM adapter: {network_adapter}',
                'icon': '✅'
            })
            results['original_count'] += 1
        else:
            results['checks'].append({
                'component': 'Network Adapter',
                'status': 'CHECK',
                'color': 'yellow',
                'details': f'Verify adapter: {network_adapter}',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
        
        # 9. TPM CHECK
        tpm_status = self.run_powershell("""
            try {
                $tpm = Get-Tpm -EA SilentlyContinue
                if ($tpm.TpmPresent) { "Present - Version: $((Get-WmiObject -Namespace root/cimv2/security/microsofttpm -Class Win32_Tpm -EA SilentlyContinue).SpecVersion)" }
                else { "Not Present" }
            } catch { "Could not check" }
        """)
        
        if "Present" in tpm_status:
            results['checks'].append({
                'component': 'TPM Security Chip',
                'status': 'PRESENT',
                'color': 'green',
                'details': f'Security chip: {tpm_status}',
                'icon': '✅'
            })
            results['original_count'] += 1
        else:
            results['checks'].append({
                'component': 'TPM Security Chip',
                'status': 'NOT FOUND',
                'color': 'yellow',
                'details': 'TPM not detected or disabled',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
        
        # Calculate final score
        results['score'] = max(0, min(100, results['score']))
        
        self.verification_results = results
        return results

    def get_verification_info(self):
        results = self.perform_verification()
        
        # Score rating
        score = results['score']
        if score >= 90:
            grade = "A+ EXCELLENT"
            verdict = "Hardware appears to be mostly original"
        elif score >= 75:
            grade = "B GOOD"
            verdict = "Minor concerns, likely original hardware"
        elif score >= 60:
            grade = "C FAIR"
            verdict = "Some components may have been replaced"
        elif score >= 40:
            grade = "D SUSPICIOUS"
            verdict = "Multiple components appear to be replaced"
        else:
            grade = "F POOR - DO NOT BUY"
            verdict = "Significant modifications detected - HIGH RISK!"
        
        # Critical flags text
        flags_text = ""
        if results['critical_flags']:
            flags_text = "\n  🚨 CRITICAL FLAGS:\n"
            for flag in results['critical_flags']:
                flags_text += f"\n  🔴 {flag}"
            flags_text += "\n"
        
        text = f"""
{'='*65}
       🔍 ULTIMATE HARDWARE VERIFICATION REPORT
{'='*65}

  📊 AUTHENTICITY SCORE: {score}/100
  
  📋 Grade: {grade}
  
  📝 Verdict: {verdict}

{'='*65}
       SUMMARY
{'='*65}

  ✅ Original Components:    {results['original_count']}
  ⚠️  Suspicious Items:       {results['suspicious_count']}
  🔴 Replaced/Modified:      {results['replaced_count']}
{flags_text}
{'='*65}
       DETAILED COMPONENT ANALYSIS
{'='*65}
"""
        
        for check in results['checks']:
            text += f"""
  {check['icon']} {check['component']}
     Status: {check['status']}
     Details: {check['details']}
"""
        
        text += f"""
{'='*65}
       💡 RECOMMENDATIONS
{'='*65}

"""
        
        if score < 60:
            text += """  🔴 HIGH RISK PURCHASE!
  
  • Multiple red flags detected
  • Ask seller for original invoice
  • Verify serial number with manufacturer
  • Consider walking away from this deal
  • If you proceed, negotiate significant discount
"""
        elif score < 80:
            text += """  ⚠️ PROCEED WITH CAUTION
  
  • Some components may be replaced
  • This is not necessarily bad (could be upgrades)
  • Ask seller about any repairs or upgrades
  • Verify warranty status
  • Negotiate price if parts are aftermarket
"""
        else:
            text += """  ✅ LOOKS GOOD
  
  • Hardware appears mostly original
  • Still do physical inspection
  • Verify with manufacturer if unsure
  • Check warranty status
"""
        
        text += f"""
{'='*65}
       ⚠️ REMEMBER
{'='*65}

  • Software detection is ~90% accurate, not 100%
  • Always do physical inspection (see Checklist tab)
  • Verify serial number with manufacturer (see Links tab)
  • Ask for original purchase invoice
  • If in doubt, walk away!

{'='*65}
              Report by: Prashun's Laptop Checker V2.0
{'='*65}
"""
        
        return text

    # ==================== BASIC INFO FUNCTIONS ====================
    def get_system_info(self):
        return f"""
{'='*60}
              💻 SYSTEM INFORMATION
{'='*60}

  Computer Name  : {platform.node()}
  OS             : {platform.system()} {platform.release()}
  Manufacturer   : {self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Manufacturer")}
  Model          : {self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Model")}
  Serial Number  : {self.run_powershell("(Get-WmiObject Win32_BIOS).SerialNumber")}
  BIOS Version   : {self.run_powershell("(Get-WmiObject Win32_BIOS).SMBIOSBIOSVersion")}
  BIOS Date      : {self.run_powershell("(Get-WmiObject Win32_BIOS).ReleaseDate")}
  
  --- MOTHERBOARD ---
  Manufacturer   : {self.run_powershell("(Get-WmiObject Win32_BaseBoard).Manufacturer")}
  Product        : {self.run_powershell("(Get-WmiObject Win32_BaseBoard).Product")}
  Serial Number  : {self.run_powershell("(Get-WmiObject Win32_BaseBoard).SerialNumber")}
  
  --- CHASSIS ---
  Chassis Serial : {self.run_powershell("(Get-WmiObject Win32_SystemEnclosure).SerialNumber")}
  Chassis Type   : {self.run_powershell("(Get-WmiObject Win32_SystemEnclosure).ChassisTypes")}
"""

    def get_cpu_info(self):
        return f"""
{'='*60}
              ⚡ CPU INFORMATION
{'='*60}

  Processor      : {self.run_powershell("(Get-WmiObject Win32_Processor).Name")}
  Cores          : {self.run_powershell("(Get-WmiObject Win32_Processor).NumberOfCores")}
  Threads        : {self.run_powershell("(Get-WmiObject Win32_Processor).NumberOfLogicalProcessors")}
  Max Speed      : {self.run_powershell("(Get-WmiObject Win32_Processor).MaxClockSpeed")} MHz
  Current Speed  : {self.run_powershell("(Get-WmiObject Win32_Processor).CurrentClockSpeed")} MHz
  CPU ID         : {self.run_powershell("(Get-WmiObject Win32_Processor).ProcessorId")}
  Architecture   : {self.run_powershell("(Get-WmiObject Win32_Processor).Architecture")}
  Socket         : {self.run_powershell("(Get-WmiObject Win32_Processor).SocketDesignation")}
"""

    def get_ram_info(self):
        ram_sticks = self.run_powershell("""
            Get-WmiObject Win32_PhysicalMemory | ForEach-Object {
                "  Slot: $($_.DeviceLocator)"
                "    Manufacturer: $($_.Manufacturer)"
                "    Capacity: $([math]::Round($_.Capacity/1GB,0)) GB"
                "    Speed: $($_.Speed) MHz"
                "    Part Number: $($_.PartNumber)"
                "    Serial: $($_.SerialNumber)"
                ""
            }
        """)
        return f"""
{'='*60}
              🧠 RAM INFORMATION
{'='*60}

  Total RAM      : {self.run_powershell("[math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory/1GB,2)")} GB
  Slots Used     : {self.run_powershell("(Get-WmiObject Win32_PhysicalMemory).Count")}
  Memory Type    : {self.run_powershell("$t=(Get-WmiObject Win32_PhysicalMemory|Select-Object -First 1).SMBIOSMemoryType;switch($t){20{'DDR'}21{'DDR2'}24{'DDR3'}26{'DDR4'}34{'DDR5'}default{'DDR4'}}")}
  
{'='*60}
       RAM MODULES (Check for aftermarket brands!)
{'='*60}

{ram_sticks}

{'='*60}
       ⚠️ AFTERMARKET RAM BRANDS TO WATCH FOR
{'='*60}

  🔴 Corsair, G.Skill, TeamGroup, Patriot, ADATA
  🔴 If you see these, RAM has been replaced/upgraded
  
  ✅ OEM brands: Samsung, SK Hynix, Micron, Ramaxel
"""

    def get_storage_info(self):
        disks = self.run_powershell("""
            Get-WmiObject Win32_DiskDrive | ForEach-Object {
                "  Model: $($_.Model)"
                "    Size: $([math]::Round($_.Size/1GB,2)) GB"
                "    Interface: $($_.InterfaceType)"
                "    Serial: $($_.SerialNumber)"
                "    Status: $($_.Status)"
                ""
            }
        """)
        partitions = self.run_powershell("""
            Get-WmiObject Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | ForEach-Object {
                $used = [math]::Round(($_.Size - $_.FreeSpace)/1GB,2)
                $total = [math]::Round($_.Size/1GB,2)
                $pct = if ($_.Size -gt 0) { [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 1) } else { 0 }
                "  $($_.DeviceID) : $used GB / $total GB used ($pct%)"
            }
        """)
        return f"""
{'='*60}
              💾 STORAGE INFORMATION
{'='*60}

  --- PHYSICAL DRIVES ---
{disks}

  --- PARTITIONS ---
{partitions}

{'='*60}
       ⚠️ AFTERMARKET SSD BRANDS TO WATCH FOR
{'='*60}

  🔴 Crucial, ADATA, PNY, TeamGroup, Patriot, Transcend
  🔴 If you see these, SSD has been replaced/upgraded
  
  ✅ OEM brands: Samsung, Toshiba/Kioxia, SK Hynix, Intel, WD, SanDisk
"""

    def get_battery_info(self):
        return f"""
{'='*60}
              🔋 BATTERY INFORMATION
{'='*60}

  Current Charge : {self.run_powershell("(Get-WmiObject Win32_Battery).EstimatedChargeRemaining")}%
  Status         : {self.run_powershell("$s=(Get-WmiObject Win32_Battery).BatteryStatus;switch($s){1{'Discharging'}2{'AC Connected'}3{'Fully Charged'}6{'Charging'}default{'Unknown'}}")}
  Battery Name   : {self.run_powershell("(Get-WmiObject Win32_Battery).Name")}
  
{'='*60}
       BATTERY HEALTH (Critical for used laptops!)
{'='*60}

  Health %       : {self.run_powershell("try{$f=(Get-WmiObject -Namespace root/WMI -Class BatteryFullChargedCapacity -EA SilentlyContinue).FullChargedCapacity;$d=(Get-WmiObject -Namespace root/WMI -Class BatteryStaticData -EA SilentlyContinue).DesignedCapacity;if($f -and $d){[math]::Round(($f/$d)*100,1)}else{'N/A'}}catch{'N/A'}")}%
  Cycle Count    : {self.run_powershell("(Get-WmiObject -Namespace root/WMI -Class BatteryCycleCount -EA SilentlyContinue).CycleCount")}
  
  Design Capacity    : {self.run_powershell("(Get-WmiObject -Namespace root/WMI -Class BatteryStaticData -EA SilentlyContinue).DesignedCapacity")} mWh
  Current Capacity   : {self.run_powershell("(Get-WmiObject -Namespace root/WMI -Class BatteryFullChargedCapacity -EA SilentlyContinue).FullChargedCapacity")} mWh

{'='*60}
       ⚠️ BATTERY ANALYSIS
{'='*60}

  📊 Health Guide:
  • 100-80%  = Excellent (like new)
  • 80-60%   = Good (normal wear)
  • 60-40%   = Fair (consider replacement)
  • Below 40% = Poor (needs replacement!)
  
  📊 Cycle Count Guide:
  • 0-300    = Light use
  • 300-500  = Normal use
  • 500-1000 = Heavy use
  • 1000+    = Very heavy use (battery worn)
  
  🔍 Fraud Detection:
  • New battery (>95%, <50 cycles) on old laptop = Replaced
  • This is not bad, but means original battery was worn
  • Ask seller about battery replacement
"""

    def get_gpu_info(self):
        gpus = self.run_powershell("""
            Get-WmiObject Win32_VideoController | ForEach-Object {
                "  Name: $($_.Name)"
                "    VRAM: $([math]::Round($_.AdapterRAM/1GB,2)) GB"
                "    Driver Version: $($_.DriverVersion)"
                "    Driver Date: $($_.DriverDate)"
                "    Resolution: $($_.CurrentHorizontalResolution) x $($_.CurrentVerticalResolution)"
                "    Refresh Rate: $($_.CurrentRefreshRate) Hz"
                ""
            }
        """)
        return f"""
{'='*60}
              🎮 GPU INFORMATION
{'='*60}

{gpus}
"""

    def get_network_info(self):
        adapters = self.run_powershell("""
            Get-WmiObject Win32_NetworkAdapter | Where-Object {$_.MACAddress -and $_.PhysicalAdapter} | ForEach-Object {
                "  Name: $($_.Name)"
                "    MAC: $($_.MACAddress)"
                "    Manufacturer: $($_.Manufacturer)"
                ""
            }
        """)
        return f"""
{'='*60}
              🌐 NETWORK INFORMATION
{'='*60}

  IP Address     : {self.run_powershell("(Get-WmiObject Win32_NetworkAdapterConfiguration|Where-Object{$_.IPAddress}|Select-Object -First 1).IPAddress[0]")}
  
  --- NETWORK ADAPTERS ---
{adapters}
"""

    def get_display_info(self):
        return f"""
{'='*60}
              🖥️ DISPLAY INFORMATION
{'='*60}

  Resolution     : {self.run_powershell("$g=Get-WmiObject Win32_VideoController|Select-Object -First 1;\"$($g.CurrentHorizontalResolution) x $($g.CurrentVerticalResolution)\"")}
  Refresh Rate   : {self.run_powershell("(Get-WmiObject Win32_VideoController|Select-Object -First 1).CurrentRefreshRate")} Hz
  Color Depth    : {self.run_powershell("(Get-WmiObject Win32_VideoController|Select-Object -First 1).CurrentBitsPerPixel")} bit
  Touch Screen   : {self.run_powershell("if(Get-WmiObject Win32_PnPEntity|Where-Object{$_.Name -like '*touch*'}){'Yes'}else{'No'}")}
  
  --- MONITOR INFO ---
{self.run_powershell('''
    Get-WmiObject WmiMonitorID -Namespace root/wmi -EA SilentlyContinue | ForEach-Object {
        $name = ($_.UserFriendlyName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ''
        $mfr = ($_.ManufacturerName | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join ''
        "  Manufacturer: $mfr"
        "  Name: $name"
        "  Serial: $(($_.SerialNumberID | Where-Object {$_ -ne 0} | ForEach-Object {[char]$_}) -join '')"
    }
''')}
"""

    def get_devices_info(self):
        return f"""
{'='*60}
              🎤 DEVICES INFORMATION
{'='*60}

  Webcam         : {self.run_powershell("$c=Get-WmiObject Win32_PnPEntity|Where-Object{$_.PNPClass -eq 'Camera' -or $_.Name -like '*webcam*' -or $_.Name -like '*camera*'};if($c){($c|Select-Object -First 1).Name}else{'Not Detected'}")}
  Audio Device   : {self.run_powershell("(Get-WmiObject Win32_SoundDevice|Select-Object -First 1).Name")}
  Bluetooth      : {self.run_powershell("if(Get-WmiObject Win32_PnPEntity|Where-Object{$_.Name -like '*bluetooth*'}){'Available'}else{'Not Found'}")}
  Fingerprint    : {self.run_powershell("if(Get-WmiObject Win32_PnPEntity|Where-Object{$_.Name -like '*fingerprint*'}){'Available'}else{'Not Found'}")}
  
  --- KEYBOARD ---
  {self.run_powershell("(Get-WmiObject Win32_Keyboard | Select-Object -First 1).Description")}
  
  --- POINTING DEVICE ---
  {self.run_powershell("(Get-WmiObject Win32_PointingDevice | Select-Object -First 1).Name")}
"""

    def get_windows_info(self):
        return f"""
{'='*60}
              🪟 WINDOWS INFORMATION
{'='*60}

  Edition        : {self.run_powershell("(Get-WmiObject Win32_OperatingSystem).Caption")}
  Version        : {self.run_powershell("(Get-WmiObject Win32_OperatingSystem).Version")}
  Build          : {self.run_powershell("(Get-WmiObject Win32_OperatingSystem).BuildNumber")}
  Install Date   : {self.run_powershell("$os=Get-WmiObject Win32_OperatingSystem;$os.ConvertToDateTime($os.InstallDate).ToString('yyyy-MM-dd HH:mm:ss')")}
  
  --- ACTIVATION ---
  Activated      : {self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;if($l.LicenseStatus -eq 1){'Yes - Genuine'}else{'No'}")}
  Product Key    : {self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;'XXXXX-XXXXX-XXXXX-XXXXX-'+$l.PartialProductKey")}
  License Type   : {self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;$l.Description")}
"""

    def get_all_info(self):
        return f"""
{'='*65}
          ULTIMATE LAPTOP HARDWARE REPORT V2.0
          Generated by: Prashun's Laptop Checker
          Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*65}
{self.get_system_info()}
{self.get_cpu_info()}
{self.get_ram_info()}
{self.get_storage_info()}
{self.get_smart_data()}
{self.get_battery_info()}
{self.get_gpu_info()}
{self.get_network_info()}
{self.get_display_info()}
{self.get_devices_info()}
{self.get_windows_info()}
{self.get_hardware_history()}
{self.get_usb_history()}
{self.get_verification_info()}
{self.get_physical_checklist()}
{self.get_manufacturer_links()}
{'='*65}
              💜 Made with Love by PRASHUN 💜
              ULTIMATE EDITION V2.0
{'='*65}
"""

    # ==================== HTML REPORT ====================
    def generate_html_report(self):
        def generate():
            try:
                self.update_progress("🔍 Running Ultimate Verification...", 5)
                verification = self.perform_verification()
                
                data = {'verification': verification}
                
                self.update_progress("🔍 Scanning System...", 10)
                data['computer_name'] = platform.node()
                data['manufacturer'] = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Manufacturer")
                data['model'] = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Model")
                data['serial'] = self.run_powershell("(Get-WmiObject Win32_BIOS).SerialNumber")
                
                self.update_progress("⚡ Scanning CPU...", 20)
                data['cpu_name'] = self.run_powershell("(Get-WmiObject Win32_Processor).Name")
                data['cpu_cores'] = self.run_powershell("(Get-WmiObject Win32_Processor).NumberOfCores")
                data['cpu_threads'] = self.run_powershell("(Get-WmiObject Win32_Processor).NumberOfLogicalProcessors")
                
                self.update_progress("🧠 Scanning RAM...", 30)
                data['total_ram'] = self.run_powershell("[math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory/1GB,2)")
                data['ram_type'] = self.run_powershell("$t=(Get-WmiObject Win32_PhysicalMemory|Select-Object -First 1).SMBIOSMemoryType;switch($t){20{'DDR'}21{'DDR2'}24{'DDR3'}26{'DDR4'}34{'DDR5'}default{'DDR4'}}")
                data['ram_speed'] = self.run_powershell("(Get-WmiObject Win32_PhysicalMemory|Select-Object -First 1).Speed")
                
                self.update_progress("💾 Scanning Storage...", 40)
                data['disk_model'] = self.run_powershell("(Get-WmiObject Win32_DiskDrive|Select-Object -First 1).Model")
                data['disk_size'] = self.run_powershell("[math]::Round((Get-WmiObject Win32_DiskDrive|Select-Object -First 1).Size/1GB,2)")
                data['disk_health'] = self.run_powershell("try{(Get-PhysicalDisk|Select-Object -First 1).HealthStatus}catch{'Unknown'}")
                
                self.update_progress("🔋 Scanning Battery...", 50)
                data['battery_charge'] = self.run_powershell("(Get-WmiObject Win32_Battery).EstimatedChargeRemaining")
                data['battery_health'] = self.run_powershell("try{$f=(Get-WmiObject -Namespace root/WMI -Class BatteryFullChargedCapacity -EA SilentlyContinue).FullChargedCapacity;$d=(Get-WmiObject -Namespace root/WMI -Class BatteryStaticData -EA SilentlyContinue).DesignedCapacity;if($f -and $d){[math]::Round(($f/$d)*100,1)}else{'N/A'}}catch{'N/A'}")
                data['battery_cycles'] = self.run_powershell("(Get-WmiObject -Namespace root/WMI -Class BatteryCycleCount -EA SilentlyContinue).CycleCount")
                
                self.update_progress("🎮 Scanning GPU...", 60)
                data['gpu_name'] = self.run_powershell("(Get-WmiObject Win32_VideoController|Select-Object -First 1).Name")
                data['resolution'] = self.run_powershell("$g=Get-WmiObject Win32_VideoController|Select-Object -First 1;\"$($g.CurrentHorizontalResolution) x $($g.CurrentVerticalResolution)\"")
                
                self.update_progress("🪟 Checking Windows...", 70)
                data['windows_edition'] = self.run_powershell("(Get-WmiObject Win32_OperatingSystem).Caption")
                data['windows_activated'] = self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;if($l.LicenseStatus -eq 1){'Yes'}else{'No'}")
                data['windows_install'] = self.run_powershell("$os=Get-WmiObject Win32_OperatingSystem;$os.ConvertToDateTime($os.InstallDate).ToString('yyyy-MM-dd')")
                
                self.update_progress("📜 Checking History...", 80)
                data['bios_date'] = self.run_powershell("try{$bios=Get-WmiObject Win32_BIOS;$date=[Management.ManagementDateTimeConverter]::ToDateTime($bios.ReleaseDate);$date.ToString('yyyy-MM-dd')}catch{'N/A'}")
                
                self.update_progress("🎨 Generating Report...", 90)
                html = self.create_ultimate_html(data)
                
                save_folder = self.get_save_folder()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_folder, f"Ultimate_Laptop_Report_{timestamp}.html")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                self.update_progress("✅ Complete!", 100)
                time.sleep(0.3)
                
                self.root.after(0, self.hide_loading)
                
                if os.path.exists(filename):
                    self.root.after(0, lambda fn=filename: self.show_success(fn))
                    
            except Exception as ex:
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: messagebox.showerror("Error", str(ex)))
        
        threading.Thread(target=generate, daemon=True).start()

    def show_success(self, filename):
        result = messagebox.askyesno("🎨 Ultimate Report Created!", f"✅ Report saved!\n\n📁 {filename}\n\nOpen now?")
        if result:
            webbrowser.open(f'file:///{filename}')

    def create_ultimate_html(self, data):
        verification = data.get('verification', {})
        score = verification.get('score', 0)
        checks = verification.get('checks', [])
        critical_flags = verification.get('critical_flags', [])
        
        # Score colors
        if score >= 90:
            score_color, grade = "#00ff88", "A+ EXCELLENT"
        elif score >= 75:
            score_color, grade = "#88ff00", "B GOOD"
        elif score >= 60:
            score_color, grade = "#ffcc00", "C FAIR"
        elif score >= 40:
            score_color, grade = "#ff8800", "D SUSPICIOUS"
        else:
            score_color, grade = "#ff4444", "F POOR - DO NOT BUY"
        
        # Battery health
        try:
            health = float(str(data.get('battery_health', '0')).replace('N/A', '0'))
        except:
            health = 0
        
        if health >= 80:
            batt_color = "#00ff88"
        elif health >= 60:
            batt_color = "#ffcc00"
        else:
            batt_color = "#ff4444"
        
        # Verification HTML
        verify_html = ""
        for check in checks:
            color_map = {'green': '#00ff88', 'yellow': '#ffcc00', 'red': '#ff4444'}
            c = color_map.get(check['color'], '#888')
            verify_html += f'''
            <div style="background:rgba(0,0,0,0.3);padding:15px;border-radius:10px;margin-bottom:10px;border-left:4px solid {c};">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:1.5em;">{check['icon']}</span>
                    <strong>{check['component']}</strong>
                    <span style="margin-left:auto;color:{c};font-weight:bold;">{check['status']}</span>
                </div>
                <div style="color:#888;margin-top:5px;margin-left:35px;">{check['details']}</div>
            </div>'''
        
        # Critical flags HTML
        flags_html = ""
        if critical_flags:
            flags_html = '<div style="background:#ff444433;border:2px solid #ff4444;border-radius:15px;padding:20px;margin-bottom:30px;"><h3 style="color:#ff4444;margin-bottom:15px;">🚨 CRITICAL FLAGS DETECTED!</h3>'
            for flag in critical_flags:
                flags_html += f'<div style="padding:10px;margin-bottom:5px;">🔴 {flag}</div>'
            flags_html += '</div>'
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ultimate Laptop Report - {data.get('model', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f0f23);
            min-height: 100vh;
            color: #fff;
            padding: 30px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .score-card {{
            background: linear-gradient(145deg, #1e1e3f, #2a2a5a);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            margin-bottom: 30px;
            border: 3px solid {score_color};
        }}
        .score-circle {{
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: conic-gradient({score_color} {score}%, #333 {score}%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }}
        .score-inner {{
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: #1a1a2e;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .score-number {{ font-size: 3em; font-weight: bold; color: {score_color}; }}
        .card {{
            background: linear-gradient(145deg, #1e1e3f, #2a2a5a);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        .card-title {{ font-size: 1.3em; color: #00fff5; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }}
        .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .info-value {{ color: #00ff88; font-weight: bold; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .footer {{ text-align: center; padding: 30px; margin-top: 30px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ ULTIMATE LAPTOP VERIFICATION REPORT</h1>
            <p style="font-size:1.2em;margin-top:10px;">{data.get('manufacturer', '')} {data.get('model', '')}</p>
            <p style="color:#ffcc00;margin-top:10px;">Serial: {data.get('serial', 'N/A')}</p>
            <p style="margin-top:10px;opacity:0.8;">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="score-card">
            <h2 style="color:#00fff5;margin-bottom:20px;">🔍 AUTHENTICITY SCORE</h2>
            <div class="score-circle">
                <div class="score-inner">
                    <div class="score-number">{score}</div>
                    <div style="color:#888;">/100</div>
                </div>
            </div>
            <div style="font-size:1.5em;font-weight:bold;color:{score_color};">{grade}</div>
            <div style="margin-top:20px;display:flex;justify-content:center;gap:40px;">
                <div><span style="font-size:2em;color:#00ff88;">✅</span><br><strong>{verification.get('original_count', 0)}</strong><br><small>Original</small></div>
                <div><span style="font-size:2em;color:#ffcc00;">⚠️</span><br><strong>{verification.get('suspicious_count', 0)}</strong><br><small>Suspicious</small></div>
                <div><span style="font-size:2em;color:#ff4444;">🔴</span><br><strong>{verification.get('replaced_count', 0)}</strong><br><small>Replaced</small></div>
            </div>
        </div>
        
        {flags_html}
        
        <div class="card">
            <div class="card-title">🔍 Component Verification</div>
            {verify_html}
        </div>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">💻 System</div>
                <div class="info-row"><span>Manufacturer</span><span class="info-value">{data.get('manufacturer', 'N/A')}</span></div>
                <div class="info-row"><span>Model</span><span class="info-value">{data.get('model', 'N/A')}</span></div>
                <div class="info-row"><span>Serial</span><span class="info-value" style="color:#ffcc00;">{data.get('serial', 'N/A')}</span></div>
                <div class="info-row"><span>BIOS Date</span><span class="info-value">{data.get('bios_date', 'N/A')}</span></div>
            </div>
            
            <div class="card">
                <div class="card-title">⚡ Processor</div>
                <div class="info-row"><span>CPU</span><span class="info-value">{data.get('cpu_name', 'N/A')}</span></div>
                <div class="info-row"><span>Cores/Threads</span><span class="info-value">{data.get('cpu_cores', 'N/A')}/{data.get('cpu_threads', 'N/A')}</span></div>
            </div>
            
            <div class="card">
                <div class="card-title">🧠 Memory</div>
                <div class="info-row"><span>Total RAM</span><span class="info-value">{data.get('total_ram', 'N/A')} GB</span></div>
                <div class="info-row"><span>Type</span><span class="info-value">{data.get('ram_type', 'DDR4')} @ {data.get('ram_speed', 'N/A')} MHz</span></div>
            </div>
            
            <div class="card">
                <div class="card-title">💾 Storage</div>
                <div class="info-row"><span>Model</span><span class="info-value">{data.get('disk_model', 'N/A')}</span></div>
                <div class="info-row"><span>Size</span><span class="info-value">{data.get('disk_size', 'N/A')} GB</span></div>
                <div class="info-row"><span>Health</span><span class="info-value">{data.get('disk_health', 'Unknown')}</span></div>
            </div>
            
            <div class="card">
                <div class="card-title">🔋 Battery</div>
                <div class="info-row"><span>Charge</span><span class="info-value">{data.get('battery_charge', 'N/A')}%</span></div>
                <div class="info-row"><span>Health</span><span class="info-value" style="color:{batt_color};">{data.get('battery_health', 'N/A')}%</span></div>
                <div class="info-row"><span>Cycles</span><span class="info-value">{data.get('battery_cycles', 'N/A')}</span></div>
            </div>
            
            <div class="card">
                <div class="card-title">🪟 Windows</div>
                <div class="info-row"><span>Edition</span><span class="info-value">{data.get('windows_edition', 'N/A')}</span></div>
                <div class="info-row"><span>Activated</span><span class="info-value">{'✅ Yes' if data.get('windows_activated', 'No') == 'Yes' else '❌ No'}</span></div>
                <div class="info-row"><span>Install Date</span><span class="info-value">{data.get('windows_install', 'N/A')}</span></div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">⚠️ Important Notes</div>
            <p style="line-height:1.8;">
                • This report provides software-based detection (~90% accuracy)<br>
                • Always perform physical inspection<br>
                • Verify serial number with manufacturer<br>
                • Ask for original purchase invoice<br>
                • "Replaced" parts are not always bad (could be upgrades)<br>
                • When in doubt, walk away from the deal
            </p>
        </div>
        
        <div class="footer">
            <h2>💜 Made with Love by PRASHUN 💜</h2>
            <p style="margin-top:10px;">Laptop Hardware Checker - Ultimate Edition V2.0</p>
        </div>
    </div>
</body>
</html>'''
        return html


def main():
    root = tk.Tk()
    app = LaptopChecker(root)
    root.mainloop()


if __name__ == "__main__":
    main()