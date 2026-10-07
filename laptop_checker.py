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
        self.root.title("Laptop Hardware Checker - By Prashun")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)
        
        self.text_widgets = {}
        self.is_loading = False
        self.verification_results = {}  # Store verification data
        
        self.create_header()
        self.create_footer()
        self.create_notebook()
        
    def get_save_folder(self):
        """Get a valid folder to save files"""
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
            text="💻 LAPTOP HARDWARE CHECKER",
            font=("Segoe UI", 24, "bold"),
            fg="#00fff5",
            bg="#16213e"
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text="Complete Hardware Verification for Second-Hand Laptops",
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
            footer_frame, text=" 🎨 BEAUTIFUL REPORT ", font=btn_font,
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
        
        # Added new Verification tab!
        self.tabs = [
            ("💻 System", self.get_system_info),
            ("⚡ CPU", self.get_cpu_info),
            ("🧠 RAM", self.get_ram_info),
            ("💾 Storage", self.get_storage_info),
            ("🔋 Battery", self.get_battery_info),
            ("🎮 GPU", self.get_gpu_info),
            ("🌐 Network", self.get_network_info),
            ("🖥️ Display", self.get_display_info),
            ("🎤 Devices", self.get_devices_info),
            ("🪟 Windows", self.get_windows_info),
            ("🔍 Verify", self.get_verification_info),  # NEW TAB!
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
        
        # Configure tags for colored text
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
                filename = os.path.join(save_folder, f"Laptop_Report_{timestamp}.txt")
                
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
                capture_output=True, text=True, timeout=15,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            output = result.stdout.strip()
            return output if output else "N/A"
        except:
            return "N/A"

    # ==================== HARDWARE VERIFICATION ====================
    def perform_verification(self):
        """Perform comprehensive hardware verification"""
        results = {
            'checks': [],
            'score': 100,
            'original_count': 0,
            'suspicious_count': 0,
            'replaced_count': 0
        }
        
        # Get basic system info
        manufacturer = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Manufacturer").upper()
        model = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Model")
        bios_serial = self.run_powershell("(Get-WmiObject Win32_BIOS).SerialNumber")
        chassis_serial = self.run_powershell("(Get-WmiObject Win32_SystemEnclosure).SerialNumber")
        mb_serial = self.run_powershell("(Get-WmiObject Win32_BaseBoard).SerialNumber")
        
        # 1. SERIAL NUMBER CONSISTENCY CHECK
        serials_match = bios_serial == chassis_serial or bios_serial == mb_serial
        if serials_match and bios_serial != "N/A":
            results['checks'].append({
                'component': 'Serial Numbers',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'BIOS and Chassis serials match: {bios_serial}',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif bios_serial == "N/A" or chassis_serial == "N/A":
            results['checks'].append({
                'component': 'Serial Numbers',
                'status': 'UNKNOWN',
                'color': 'yellow',
                'details': 'Could not verify serial numbers',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
            results['score'] -= 5
        else:
            results['checks'].append({
                'component': 'Serial Numbers',
                'status': 'MISMATCH',
                'color': 'red',
                'details': f'BIOS: {bios_serial} vs Chassis: {chassis_serial}',
                'icon': '🔴'
            })
            results['replaced_count'] += 1
            results['score'] -= 15
        
        # 2. RAM VERIFICATION
        ram_info = self.run_powershell("""
            Get-WmiObject Win32_PhysicalMemory | ForEach-Object {
                "$($_.Manufacturer)|$($_.PartNumber)|$($_.SerialNumber)|$($_.Capacity)"
            }
        """)
        
        # Known OEM RAM manufacturers for each brand
        oem_ram = {
            'DELL': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'KINGSTON'],
            'HP': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'RAMAXEL'],
            'LENOVO': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'RAMAXEL'],
            'ASUS': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'KINGSTON'],
            'ACER': ['SAMSUNG', 'SK HYNIX', 'HYNIX', 'MICRON', 'KINGSTON'],
        }
        
        expected_ram_brands = oem_ram.get(manufacturer.split()[0], ['SAMSUNG', 'SK HYNIX', 'MICRON'])
        
        ram_sticks = ram_info.strip().split('\n') if ram_info != "N/A" else []
        ram_is_oem = True
        ram_manufacturers = []
        
        for stick in ram_sticks:
            if '|' in stick:
                parts = stick.split('|')
                ram_mfr = parts[0].upper() if parts[0] else "UNKNOWN"
                ram_manufacturers.append(ram_mfr)
                
                is_oem = any(oem in ram_mfr for oem in expected_ram_brands)
                if not is_oem and ram_mfr not in ['', 'UNKNOWN', 'N/A']:
                    ram_is_oem = False
        
        if ram_is_oem and ram_manufacturers:
            results['checks'].append({
                'component': 'RAM Modules',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'OEM RAM detected: {", ".join(set(ram_manufacturers))}',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif not ram_manufacturers or all(m in ['', 'UNKNOWN', 'N/A'] for m in ram_manufacturers):
            results['checks'].append({
                'component': 'RAM Modules',
                'status': 'UNKNOWN',
                'color': 'yellow',
                'details': 'Could not identify RAM manufacturer',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
            results['score'] -= 5
        else:
            results['checks'].append({
                'component': 'RAM Modules',
                'status': 'LIKELY REPLACED',
                'color': 'red',
                'details': f'Non-OEM RAM: {", ".join(set(ram_manufacturers))}. Expected: {", ".join(expected_ram_brands[:3])}',
                'icon': '🔴'
            })
            results['replaced_count'] += 1
            results['score'] -= 10
        
        # 3. STORAGE/SSD VERIFICATION
        disk_info = self.run_powershell("""
            Get-WmiObject Win32_DiskDrive | Select-Object -First 1 | ForEach-Object {
                "$($_.Model)|$($_.SerialNumber)|$($_.InterfaceType)"
            }
        """)
        
        # Known OEM SSD brands
        oem_storage = {
            'DELL': ['SAMSUNG', 'TOSHIBA', 'KIOXIA', 'SK HYNIX', 'MICRON', 'LITEON', 'SANDISK', 'WD', 'WESTERN DIGITAL'],
            'HP': ['SAMSUNG', 'TOSHIBA', 'KIOXIA', 'SK HYNIX', 'INTEL', 'SANDISK', 'WD'],
            'LENOVO': ['SAMSUNG', 'TOSHIBA', 'KIOXIA', 'SK HYNIX', 'INTEL', 'UNION MEMORY', 'SANDISK', 'WD'],
            'ASUS': ['SAMSUNG', 'TOSHIBA', 'KIOXIA', 'SK HYNIX', 'INTEL', 'KINGSTON', 'SANDISK', 'WD'],
            'ACER': ['SAMSUNG', 'TOSHIBA', 'KIOXIA', 'SK HYNIX', 'INTEL', 'KINGSTON', 'SANDISK', 'WD'],
        }
        
        aftermarket_storage = ['CRUCIAL', 'ADATA', 'PNY', 'TEAMGROUP', 'PATRIOT', 'CORSAIR', 'SEAGATE', 'TRANSCEND']
        
        expected_storage = oem_storage.get(manufacturer.split()[0], ['SAMSUNG', 'TOSHIBA', 'SK HYNIX', 'WD'])
        
        if disk_info != "N/A" and '|' in disk_info:
            disk_model = disk_info.split('|')[0].upper()
            
            is_oem_storage = any(oem in disk_model for oem in expected_storage)
            is_aftermarket = any(am in disk_model for am in aftermarket_storage)
            
            if is_oem_storage:
                results['checks'].append({
                    'component': 'Storage Drive',
                    'status': 'ORIGINAL',
                    'color': 'green',
                    'details': f'OEM Storage: {disk_model}',
                    'icon': '✅'
                })
                results['original_count'] += 1
            elif is_aftermarket:
                results['checks'].append({
                    'component': 'Storage Drive',
                    'status': 'REPLACED',
                    'color': 'red',
                    'details': f'Aftermarket SSD detected: {disk_model}',
                    'icon': '🔴'
                })
                results['replaced_count'] += 1
                results['score'] -= 10
            else:
                results['checks'].append({
                    'component': 'Storage Drive',
                    'status': 'SUSPICIOUS',
                    'color': 'yellow',
                    'details': f'Unknown brand: {disk_model}',
                    'icon': '⚠️'
                })
                results['suspicious_count'] += 1
                results['score'] -= 5
        
        # 4. BATTERY VERIFICATION
        battery_health = self.run_powershell("""
            try {
                $f = (Get-WmiObject -Namespace "root/WMI" -Class "BatteryFullChargedCapacity" -EA SilentlyContinue).FullChargedCapacity
                $d = (Get-WmiObject -Namespace "root/WMI" -Class "BatteryStaticData" -EA SilentlyContinue).DesignedCapacity
                if ($f -and $d -and $d -gt 0) { [math]::Round(($f / $d) * 100, 1) } else { "N/A" }
            } catch { "N/A" }
        """)
        
        battery_cycles = self.run_powershell("(Get-WmiObject -Namespace 'root/WMI' -Class 'BatteryCycleCount' -EA SilentlyContinue).CycleCount")
        battery_name = self.run_powershell("(Get-WmiObject Win32_Battery).Name")
        
        # Get system age from BIOS date
        bios_date = self.run_powershell("(Get-WmiObject Win32_BIOS).ReleaseDate")
        
        try:
            health_val = float(battery_health) if battery_health != "N/A" else 0
            cycles_val = int(battery_cycles) if battery_cycles != "N/A" else 0
        except:
            health_val = 0
            cycles_val = 0
        
        # If battery health > 95% but system is old, likely replaced
        if health_val > 95 and cycles_val < 50:
            # Check if BIOS date suggests old system
            results['checks'].append({
                'component': 'Battery',
                'status': 'LIKELY NEW/REPLACED',
                'color': 'yellow',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. Battery appears new - may be replacement.',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
            results['score'] -= 3
        elif health_val >= 80:
            results['checks'].append({
                'component': 'Battery',
                'status': 'GOOD CONDITION',
                'color': 'green',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. Consistent with original battery.',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif health_val >= 50:
            results['checks'].append({
                'component': 'Battery',
                'status': 'WORN - ORIGINAL',
                'color': 'green',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. Normal wear suggests original battery.',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif health_val > 0:
            results['checks'].append({
                'component': 'Battery',
                'status': 'DEGRADED',
                'color': 'yellow',
                'details': f'Health: {health_val}%, Cycles: {cycles_val}. Heavily used original or old replacement.',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
        else:
            results['checks'].append({
                'component': 'Battery',
                'status': 'UNKNOWN',
                'color': 'yellow',
                'details': 'Could not read battery health data',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
        
        # 5. WINDOWS INSTALLATION CHECK
        install_date = self.run_powershell("""
            $date = (Get-WmiObject Win32_OperatingSystem).InstallDate
            if ($date) { $date.Substring(0,8) } else { "N/A" }
        """)
        
        if install_date != "N/A" and len(install_date) == 8:
            try:
                install_year = int(install_date[0:4])
                install_month = int(install_date[4:6])
                install_day = int(install_date[6:8])
                install_datetime = datetime(install_year, install_month, install_day)
                days_since_install = (datetime.now() - install_datetime).days
                
                if days_since_install < 30:
                    results['checks'].append({
                        'component': 'Windows Installation',
                        'status': 'RECENTLY INSTALLED',
                        'color': 'yellow',
                        'details': f'Installed {days_since_install} days ago on {install_datetime.strftime("%Y-%m-%d")}. Fresh install detected!',
                        'icon': '⚠️'
                    })
                    results['suspicious_count'] += 1
                    results['score'] -= 5
                else:
                    results['checks'].append({
                        'component': 'Windows Installation',
                        'status': 'NORMAL',
                        'color': 'green',
                        'details': f'Installed {days_since_install} days ago on {install_datetime.strftime("%Y-%m-%d")}',
                        'icon': '✅'
                    })
                    results['original_count'] += 1
            except:
                pass
        
        # 6. BIOS MODIFICATION CHECK
        bios_vendor = self.run_powershell("(Get-WmiObject Win32_BIOS).Manufacturer").upper()
        
        # Check if BIOS vendor matches system manufacturer
        bios_matches = any(m in bios_vendor for m in [manufacturer.split()[0], 'AMERICAN MEGATRENDS', 'AMI', 'INSYDE', 'PHOENIX'])
        
        if bios_matches:
            results['checks'].append({
                'component': 'BIOS/Firmware',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'BIOS vendor ({bios_vendor}) matches expected for {manufacturer}',
                'icon': '✅'
            })
            results['original_count'] += 1
        else:
            results['checks'].append({
                'component': 'BIOS/Firmware',
                'status': 'SUSPICIOUS',
                'color': 'yellow',
                'details': f'BIOS vendor: {bios_vendor}. May be modified.',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
            results['score'] -= 10
        
        # 7. NETWORK ADAPTER CHECK (MAC Address)
        mac_info = self.run_powershell("""
            Get-WmiObject Win32_NetworkAdapter | Where-Object {$_.MACAddress -and $_.PhysicalAdapter} | 
            Select-Object -First 1 | ForEach-Object { "$($_.Name)|$($_.MACAddress)" }
        """)
        
        if mac_info != "N/A" and '|' in mac_info:
            adapter_name = mac_info.split('|')[0]
            mac_address = mac_info.split('|')[1]
            
            # Check if network adapter matches manufacturer
            adapter_matches = any(m in adapter_name.upper() for m in ['INTEL', 'REALTEK', 'QUALCOMM', 'BROADCOM', 'KILLER', manufacturer.split()[0]])
            
            if adapter_matches:
                results['checks'].append({
                    'component': 'Network Adapter',
                    'status': 'ORIGINAL',
                    'color': 'green',
                    'details': f'{adapter_name} - Standard OEM adapter',
                    'icon': '✅'
                })
                results['original_count'] += 1
            else:
                results['checks'].append({
                    'component': 'Network Adapter',
                    'status': 'CHECK',
                    'color': 'yellow',
                    'details': f'{adapter_name} - Verify if original',
                    'icon': '⚠️'
                })
                results['suspicious_count'] += 1
        
        # 8. DISPLAY/SCREEN CHECK
        display_info = self.run_powershell("""
            Get-WmiObject WmiMonitorID -Namespace root/wmi -EA SilentlyContinue | Select-Object -First 1 | ForEach-Object {
                $name = ($_.UserFriendlyName | ForEach-Object {[char]$_}) -join ''
                $mfr = ($_.ManufacturerName | ForEach-Object {[char]$_}) -join ''
                "$mfr|$name"
            }
        """)
        
        oem_display_mfr = {
            'DELL': ['LG', 'SAMSUNG', 'AU OPTRONICS', 'AUO', 'BOE', 'CHIMEI', 'INNOLUX', 'SHARP'],
            'HP': ['LG', 'SAMSUNG', 'AU OPTRONICS', 'AUO', 'BOE', 'CHIMEI', 'INNOLUX'],
            'LENOVO': ['LG', 'SAMSUNG', 'AU OPTRONICS', 'AUO', 'BOE', 'CHIMEI', 'INNOLUX', 'CSOT'],
            'ASUS': ['LG', 'SAMSUNG', 'AU OPTRONICS', 'AUO', 'BOE', 'CHIMEI', 'INNOLUX'],
            'ACER': ['LG', 'SAMSUNG', 'AU OPTRONICS', 'AUO', 'BOE', 'CHIMEI', 'INNOLUX'],
        }
        
        expected_display = oem_display_mfr.get(manufacturer.split()[0], ['LG', 'SAMSUNG', 'AUO', 'BOE'])
        
        if display_info != "N/A" and '|' in display_info:
            display_mfr = display_info.split('|')[0].upper().strip()
            display_name = display_info.split('|')[1].strip()
            
            is_oem_display = any(oem in display_mfr for oem in expected_display) or display_mfr == ''
            
            if is_oem_display:
                results['checks'].append({
                    'component': 'Display Panel',
                    'status': 'ORIGINAL',
                    'color': 'green',
                    'details': f'OEM Display: {display_mfr} {display_name}' if display_mfr else 'Standard built-in display',
                    'icon': '✅'
                })
                results['original_count'] += 1
            else:
                results['checks'].append({
                    'component': 'Display Panel',
                    'status': 'POSSIBLY REPLACED',
                    'color': 'yellow',
                    'details': f'Display: {display_mfr} {display_name}. May be aftermarket.',
                    'icon': '⚠️'
                })
                results['suspicious_count'] += 1
                results['score'] -= 5
        else:
            results['checks'].append({
                'component': 'Display Panel',
                'status': 'BUILT-IN',
                'color': 'green',
                'details': 'Internal display detected',
                'icon': '✅'
            })
            results['original_count'] += 1
        
        # 9. KEYBOARD CHECK
        keyboard_info = self.run_powershell("(Get-WmiObject Win32_Keyboard | Select-Object -First 1).Description")
        
        if keyboard_info != "N/A" and 'HID' in keyboard_info.upper():
            results['checks'].append({
                'component': 'Keyboard',
                'status': 'ORIGINAL',
                'color': 'green',
                'details': f'Standard built-in keyboard: {keyboard_info}',
                'icon': '✅'
            })
            results['original_count'] += 1
        elif keyboard_info != "N/A":
            results['checks'].append({
                'component': 'Keyboard',
                'status': 'CHECK',
                'color': 'yellow',
                'details': f'Keyboard: {keyboard_info}',
                'icon': '⚠️'
            })
            results['suspicious_count'] += 1
        
        # Calculate final score
        results['score'] = max(0, min(100, results['score']))
        
        self.verification_results = results
        return results

    def get_verification_info(self):
        """Generate verification report text"""
        results = self.perform_verification()
        
        # Header
        text = f"""
{'='*65}
       🔍 HARDWARE AUTHENTICITY VERIFICATION REPORT
{'='*65}

  This report analyzes hardware components to detect potential
  replacements or modifications from original factory specs.

{'='*65}
"""
        
        # Score section
        score = results['score']
        if score >= 90:
            grade = "A+ EXCELLENT"
            grade_color = "🟢"
            verdict = "Hardware appears to be mostly original"
        elif score >= 75:
            grade = "B GOOD"
            grade_color = "🟢"
            verdict = "Minor concerns, likely original hardware"
        elif score >= 60:
            grade = "C FAIR"
            grade_color = "🟡"
            verdict = "Some components may have been replaced"
        elif score >= 40:
            grade = "D SUSPICIOUS"
            grade_color = "🟠"
            verdict = "Multiple components appear to be replaced"
        else:
            grade = "F POOR"
            grade_color = "🔴"
            verdict = "Significant modifications detected"
        
        text += f"""
  📊 AUTHENTICITY SCORE: {score}/100  {grade_color} {grade}
  
  Verdict: {verdict}

  Summary:
  ✅ Original Components:    {results['original_count']}
  ⚠️  Suspicious Items:       {results['suspicious_count']}
  🔴 Replaced/Modified:      {results['replaced_count']}

{'='*65}
       DETAILED COMPONENT ANALYSIS
{'='*65}
"""
        
        # Component checks
        for check in results['checks']:
            status_icon = check['icon']
            component = check['component']
            status = check['status']
            details = check['details']
            
            text += f"""
  {status_icon} {component}
     Status: {status}
     Details: {details}
"""
        
        # Recommendations
        text += f"""
{'='*65}
       💡 RECOMMENDATIONS
{'='*65}
"""
        
        if results['replaced_count'] > 0:
            text += """
  🔴 REPLACED PARTS DETECTED:
     - Ask seller about replacement history
     - Request original purchase invoice
     - Verify warranty status for replaced parts
     - Negotiate price based on non-original parts
"""
        
        if results['suspicious_count'] > 0:
            text += """
  ⚠️  SUSPICIOUS ITEMS FOUND:
     - Request documentation for any repairs
     - Check if parts match original specs
     - Verify serial numbers with manufacturer
"""
        
        if results['original_count'] == len(results['checks']):
            text += """
  ✅ ALL COMPONENTS APPEAR ORIGINAL:
     - Hardware matches expected OEM specifications
     - No obvious signs of replacement detected
     - Still verify with visual inspection
"""
        
        text += f"""
{'='*65}
       ⚠️  IMPORTANT NOTES
{'='*65}

  • This analysis is based on software detection only
  • Physical inspection is still recommended
  • Some OEM parts may not be detected correctly
  • A "replaced" part is not necessarily bad
  • New battery/SSD can be an upgrade, not fraud
  
  Always verify:
  1. Physical condition of components
  2. Original purchase invoice
  3. Manufacturer warranty status
  4. Service history from authorized centers

{'='*65}
              Report by: Prashun's Laptop Checker
{'='*65}
"""
        
        return text

    # ==================== HTML REPORT WITH VERIFICATION ====================
    def generate_html_report(self):
        def generate():
            try:
                data = {}
                
                # Run verification first
                self.update_progress("🔍 Running Hardware Verification...", 5)
                verification = self.perform_verification()
                data['verification'] = verification
                
                # System Info
                self.update_progress("🔍 Scanning System Information...", 10)
                time.sleep(0.1)
                data['computer_name'] = platform.node()
                data['os'] = f"{platform.system()} {platform.release()}"
                data['os_version'] = platform.version()
                data['architecture'] = platform.machine()
                data['manufacturer'] = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Manufacturer")
                data['model'] = self.run_powershell("(Get-WmiObject Win32_ComputerSystem).Model")
                data['serial'] = self.run_powershell("(Get-WmiObject Win32_BIOS).SerialNumber")
                data['bios_vendor'] = self.run_powershell("(Get-WmiObject Win32_BIOS).Manufacturer")
                data['bios_version'] = self.run_powershell("(Get-WmiObject Win32_BIOS).SMBIOSBIOSVersion")
                
                # Motherboard
                self.update_progress("🔧 Scanning Motherboard...", 15)
                data['mb_manufacturer'] = self.run_powershell("(Get-WmiObject Win32_BaseBoard).Manufacturer")
                data['mb_product'] = self.run_powershell("(Get-WmiObject Win32_BaseBoard).Product")
                data['mb_serial'] = self.run_powershell("(Get-WmiObject Win32_BaseBoard).SerialNumber")
                
                # CPU
                self.update_progress("⚡ Scanning Processor...", 25)
                time.sleep(0.1)
                data['cpu_name'] = self.run_powershell("(Get-WmiObject Win32_Processor).Name")
                data['cpu_cores'] = self.run_powershell("(Get-WmiObject Win32_Processor).NumberOfCores")
                data['cpu_threads'] = self.run_powershell("(Get-WmiObject Win32_Processor).NumberOfLogicalProcessors")
                data['cpu_speed'] = self.run_powershell("(Get-WmiObject Win32_Processor).MaxClockSpeed")
                data['cpu_id'] = self.run_powershell("(Get-WmiObject Win32_Processor).ProcessorId")
                
                # RAM
                self.update_progress("🧠 Scanning Memory...", 35)
                time.sleep(0.1)
                data['total_ram'] = self.run_powershell("[math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)")
                data['ram_slots_used'] = self.run_powershell("(Get-WmiObject Win32_PhysicalMemory).Count")
                data['ram_speed'] = self.run_powershell("(Get-WmiObject Win32_PhysicalMemory | Select-Object -First 1).Speed")
                data['ram_type'] = self.run_powershell("$t=(Get-WmiObject Win32_PhysicalMemory|Select-Object -First 1).SMBIOSMemoryType;switch($t){20{'DDR'}21{'DDR2'}24{'DDR3'}26{'DDR4'}34{'DDR5'}default{'DDR4'}}")
                data['ram_sticks'] = self.run_powershell("""
                    Get-WmiObject Win32_PhysicalMemory | ForEach-Object {
                        "$($_.DeviceLocator)|$($_.Manufacturer)|$([math]::Round($_.Capacity/1GB,0))|$($_.Speed)"
                    }
                """)
                
                # Storage
                self.update_progress("💾 Scanning Storage...", 45)
                time.sleep(0.1)
                data['disks'] = self.run_powershell("""
                    Get-WmiObject Win32_DiskDrive | ForEach-Object {
                        "$($_.Model)|$([math]::Round($_.Size/1GB,2))|$($_.SerialNumber)|$($_.InterfaceType)"
                    }
                """)
                data['partitions'] = self.run_powershell("""
                    Get-WmiObject Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | ForEach-Object {
                        "$($_.DeviceID)|$($_.VolumeName)|$([math]::Round($_.Size/1GB,2))|$([math]::Round($_.FreeSpace/1GB,2))|$($_.FileSystem)"
                    }
                """)
                
                # Battery
                self.update_progress("🔋 Scanning Battery...", 55)
                time.sleep(0.1)
                data['battery_charge'] = self.run_powershell("(Get-WmiObject Win32_Battery).EstimatedChargeRemaining")
                data['battery_status'] = self.run_powershell("$s=(Get-WmiObject Win32_Battery).BatteryStatus;switch($s){1{'Discharging'}2{'AC Connected'}3{'Fully Charged'}6{'Charging'}default{'Unknown'}}")
                data['battery_health'] = self.run_powershell("""
                    try {
                        $f = (Get-WmiObject -Namespace "root/WMI" -Class "BatteryFullChargedCapacity" -EA SilentlyContinue).FullChargedCapacity
                        $d = (Get-WmiObject -Namespace "root/WMI" -Class "BatteryStaticData" -EA SilentlyContinue).DesignedCapacity
                        if ($f -and $d -and $d -gt 0) { [math]::Round(($f / $d) * 100, 1) } else { "N/A" }
                    } catch { "N/A" }
                """)
                data['battery_design'] = self.run_powershell("(Get-WmiObject -Namespace 'root/WMI' -Class 'BatteryStaticData' -EA SilentlyContinue).DesignedCapacity")
                data['battery_current'] = self.run_powershell("(Get-WmiObject -Namespace 'root/WMI' -Class 'BatteryFullChargedCapacity' -EA SilentlyContinue).FullChargedCapacity")
                data['battery_cycles'] = self.run_powershell("(Get-WmiObject -Namespace 'root/WMI' -Class 'BatteryCycleCount' -EA SilentlyContinue).CycleCount")
                
                # GPU
                self.update_progress("🎮 Scanning Graphics...", 65)
                time.sleep(0.1)
                data['gpus'] = self.run_powershell("""
                    Get-WmiObject Win32_VideoController | ForEach-Object {
                        "$($_.Name)|$([math]::Round($_.AdapterRAM/1GB,2))|$($_.DriverVersion)|$($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)|$($_.CurrentRefreshRate)"
                    }
                """)
                data['resolution'] = self.run_powershell("$g=Get-WmiObject Win32_VideoController|Select-Object -First 1;\"$($g.CurrentHorizontalResolution) x $($g.CurrentVerticalResolution)\"")
                data['refresh_rate'] = self.run_powershell("(Get-WmiObject Win32_VideoController|Select-Object -First 1).CurrentRefreshRate")
                
                # Network
                self.update_progress("🌐 Scanning Network...", 75)
                time.sleep(0.1)
                data['network_adapters'] = self.run_powershell("""
                    Get-WmiObject Win32_NetworkAdapter | Where-Object {$_.MACAddress -and $_.PhysicalAdapter} | ForEach-Object {
                        "$($_.Name)|$($_.MACAddress)"
                    }
                """)
                data['ip_address'] = self.run_powershell("(Get-WmiObject Win32_NetworkAdapterConfiguration | Where-Object {$_.IPAddress} | Select-Object -First 1).IPAddress[0]")
                
                # Devices
                self.update_progress("🎤 Scanning Devices...", 85)
                time.sleep(0.1)
                data['webcam'] = self.run_powershell("$c=Get-WmiObject Win32_PnPEntity|Where-Object{$_.PNPClass -eq 'Camera' -or $_.Name -like '*webcam*' -or $_.Name -like '*camera*'};if($c){($c|Select-Object -First 1).Name}else{'Not Detected'}")
                data['audio'] = self.run_powershell("(Get-WmiObject Win32_SoundDevice|Select-Object -First 1).Name")
                data['touch'] = self.run_powershell("if(Get-WmiObject Win32_PnPEntity|Where-Object{$_.Name -like '*touch*'}){'Yes'}else{'No'}")
                data['bluetooth'] = self.run_powershell("if(Get-WmiObject Win32_PnPEntity|Where-Object{$_.Name -like '*bluetooth*'}){'Available'}else{'Not Found'}")
                
                # Windows
                self.update_progress("🪟 Checking Windows...", 92)
                time.sleep(0.1)
                data['windows_activated'] = self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;if($l.LicenseStatus -eq 1){'Yes'}else{'No'}")
                data['windows_key'] = self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;'XXXXX-XXXXX-XXXXX-XXXXX-'+$l.PartialProductKey")
                data['windows_edition'] = self.run_powershell("(Get-WmiObject Win32_OperatingSystem).Caption")
                data['windows_build'] = self.run_powershell("(Get-WmiObject Win32_OperatingSystem).BuildNumber")
                
                # Generate HTML
                self.update_progress("🎨 Generating Report...", 97)
                time.sleep(0.2)
                
                html = self.create_beautiful_html(data)
                
                self.update_progress("💾 Saving Report...", 99)
                
                save_folder = self.get_save_folder()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(save_folder, f"Laptop_Report_{timestamp}.html")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                self.update_progress("✅ Complete!", 100)
                time.sleep(0.3)
                
                self.root.after(0, self.hide_loading)
                
                if os.path.exists(filename):
                    self.root.after(0, lambda fn=filename: self.show_success(fn))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "File was not created!"))
                    
            except Exception as ex:
                error_msg = str(ex)
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda em=error_msg: messagebox.showerror("Error", f"Failed:\n\n{em}"))
        
        threading.Thread(target=generate, daemon=True).start()

    def show_success(self, filename):
        result = messagebox.askyesno(
            "🎨 Report Created!",
            f"✅ Beautiful report saved!\n\n📁 {filename}\n\nOpen now?"
        )
        if result:
            webbrowser.open(f'file:///{filename}')

    def create_beautiful_html(self, data):
        verification = data.get('verification', {})
        score = verification.get('score', 0)
        checks = verification.get('checks', [])
        
        # Score colors
        if score >= 90:
            score_color = "#00ff88"
            score_grade = "A+ EXCELLENT"
            score_verdict = "Hardware appears to be mostly original"
        elif score >= 75:
            score_color = "#88ff00"
            score_grade = "B GOOD"
            score_verdict = "Minor concerns, likely original"
        elif score >= 60:
            score_color = "#ffcc00"
            score_grade = "C FAIR"
            score_verdict = "Some components may be replaced"
        elif score >= 40:
            score_color = "#ff8800"
            score_grade = "D SUSPICIOUS"
            score_verdict = "Multiple components appear replaced"
        else:
            score_color = "#ff4444"
            score_grade = "F POOR"
            score_verdict = "Significant modifications detected"
        
        # Battery health
        try:
            health = float(str(data.get('battery_health', '0')).replace('N/A', '0'))
        except:
            health = 0
        
        if health >= 80:
            batt_color, batt_status, batt_emoji = "#00ff88", "EXCELLENT", "💚"
        elif health >= 60:
            batt_color, batt_status, batt_emoji = "#ffcc00", "GOOD", "💛"
        elif health >= 40:
            batt_color, batt_status, batt_emoji = "#ff8800", "FAIR", "🧡"
        else:
            batt_color, batt_status, batt_emoji = "#ff4444", "POOR", "❤️"
        
        # Generate verification checks HTML
        verification_html = ""
        for check in checks:
            color_map = {'green': '#00ff88', 'yellow': '#ffcc00', 'red': '#ff4444'}
            bg_color = color_map.get(check['color'], '#888')
            verification_html += f'''
            <div class="verify-item" style="border-left: 4px solid {bg_color};">
                <div class="verify-header">
                    <span class="verify-icon">{check['icon']}</span>
                    <span class="verify-component">{check['component']}</span>
                    <span class="verify-status" style="color: {bg_color};">{check['status']}</span>
                </div>
                <div class="verify-details">{check['details']}</div>
            </div>'''
        
        # RAM HTML
        ram_html = ""
        try:
            sticks = data.get('ram_sticks', '').strip().split('\n')
            for stick in sticks:
                if '|' in stick:
                    parts = stick.split('|')
                    slot, mfr, cap, spd = parts[0], parts[1], parts[2], parts[3]
                    ram_html += f'''<div class="ram-stick"><div class="ram-icon">🧠</div><div class="ram-details"><strong>{slot}</strong><br><span style="color:#00ff88;">{cap} GB</span> @ {spd} MHz<br><small style="color:#888;">{mfr}</small></div></div>'''
        except:
            ram_html = f'<div style="text-align:center;padding:20px;font-size:3em;color:#00ff88;">{data.get("total_ram", "N/A")} GB</div>'
        
        # Storage HTML
        storage_html = ""
        try:
            partitions = data.get('partitions', '').strip().split('\n')
            for part in partitions:
                if '|' in part:
                    parts = part.split('|')
                    drive, label, total, free = parts[0], parts[1], float(parts[2]), float(parts[3])
                    used = total - free
                    percent = (used / total * 100) if total > 0 else 0
                    color = "#ff4444" if percent >= 90 else "#ff8800" if percent >= 70 else "#00ff88"
                    storage_html += f'''<div class="storage-item"><div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span>💿 {drive} {f"({label})" if label else ""}</span><span>{used:.1f} / {total:.1f} GB</span></div><div class="storage-bar"><div class="storage-fill" style="width:{percent}%;background:{color};">{percent:.1f}%</div></div></div>'''
        except:
            storage_html = "<p>Storage info not available</p>"
        
        # Disks HTML
        disks_html = ""
        try:
            disks = data.get('disks', '').strip().split('\n')
            for disk in disks:
                if '|' in disk:
                    parts = disk.split('|')
                    model, size = parts[0], parts[1]
                    disk_icon = "⚡" if any(x in model.upper() for x in ['SSD', 'NVME']) else "💽"
                    disks_html += f'''<div class="disk-item"><span style="font-size:2em;margin-right:15px;">{disk_icon}</span><div><strong>{model}</strong><br><span style="color:#00ff88;">{size} GB</span></div></div>'''
        except:
            disks_html = ""
        
        # GPUs HTML
        gpus_html = ""
        try:
            gpus = data.get('gpus', '').strip().split('\n')
            for i, gpu in enumerate(gpus):
                if '|' in gpu:
                    parts = gpu.split('|')
                    name, vram = parts[0], parts[1]
                    gpus_html += f'''<div class="gpu-item"><span style="font-size:2em;margin-right:15px;">{"🎮" if i==0 else "🖥️"}</span><div><strong>{name}</strong><br>VRAM: <span style="color:#00ff88;">{vram} GB</span></div></div>'''
        except:
            gpus_html = ""
        
        # Network HTML
        network_html = ""
        try:
            adapters = data.get('network_adapters', '').strip().split('\n')
            for adapter in adapters[:3]:
                if '|' in adapter:
                    parts = adapter.split('|')
                    name, mac = parts[0], parts[1]
                    icon = "📶" if any(x in name.lower() for x in ['wireless', 'wi-fi', 'wifi']) else "🔌"
                    network_html += f'''<div class="network-item"><span style="font-size:1.8em;margin-right:12px;">{icon}</span><div><strong>{name}</strong><br><code>{mac}</code></div></div>'''
        except:
            network_html = ""
        
        # Windows status
        win_ok = str(data.get('windows_activated', 'No')).lower() == 'yes'
        win_color = "#00ff88" if win_ok else "#ff4444"
        win_icon = "✅" if win_ok else "❌"
        win_text = "GENUINE & ACTIVATED" if win_ok else "NOT ACTIVATED"
        
        # Device status
        cam_ok = "not" not in str(data.get('webcam', '')).lower()
        touch_ok = str(data.get('touch', 'No')).lower() == 'yes'
        bt_ok = "available" in str(data.get('bluetooth', '')).lower()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laptop Report - {data.get('model', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            min-height: 100vh;
            color: #fff;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1300px; margin: 0 auto; }}
        
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(40px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} }}
        @keyframes fillBar {{ from {{ width: 0; }} }}
        @keyframes glow {{ 0%, 100% {{ box-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }} 50% {{ box-shadow: 0 0 40px rgba(102, 126, 234, 0.8); }} }}
        @keyframes scoreGlow {{ 0%, 100% {{ box-shadow: 0 0 30px {score_color}66; }} 50% {{ box-shadow: 0 0 60px {score_color}aa; }} }}
        
        .header {{
            text-align: center;
            padding: 50px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
            margin-bottom: 40px;
            animation: fadeIn 0.8s ease-out, glow 3s infinite;
        }}
        .header h1 {{ font-size: 2.8em; margin-bottom: 15px; }}
        .header .model {{ font-size: 1.8em; background: rgba(255,255,255,0.2); padding: 15px 40px; border-radius: 50px; display: inline-block; margin: 15px 0; }}
        .header .serial {{ font-size: 1.1em; color: #ffcc00; }}
        .header .date {{ margin-top: 15px; opacity: 0.8; }}
        
        /* VERIFICATION SCORE CARD */
        .score-card {{
            background: linear-gradient(145deg, #1e1e3f 0%, #2a2a5a 100%);
            border-radius: 25px;
            padding: 40px;
            margin-bottom: 40px;
            text-align: center;
            border: 3px solid {score_color};
            animation: slideUp 0.6s ease-out, scoreGlow 2s infinite;
        }}
        .score-title {{ font-size: 1.5em; color: #00fff5; margin-bottom: 20px; }}
        .score-circle {{
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: conic-gradient({score_color} {score}%, #333 {score}%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            position: relative;
        }}
        .score-inner {{
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: #1a1a2e;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .score-number {{ font-size: 3.5em; font-weight: bold; color: {score_color}; line-height: 1; }}
        .score-label {{ font-size: 1em; color: #888; }}
        .score-grade {{ font-size: 1.8em; font-weight: bold; color: {score_color}; margin-bottom: 10px; }}
        .score-verdict {{ font-size: 1.1em; color: #aaa; }}
        .score-summary {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        .score-stat {{ text-align: center; }}
        .score-stat-icon {{ font-size: 2em; margin-bottom: 5px; }}
        .score-stat-num {{ font-size: 2em; font-weight: bold; }}
        .score-stat-label {{ font-size: 0.9em; color: #888; }}
        
        /* VERIFICATION ITEMS */
        .verify-section {{
            background: linear-gradient(145deg, #1e1e3f 0%, #2a2a5a 100%);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 40px;
        }}
        .verify-section-title {{
            font-size: 1.5em;
            color: #00fff5;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .verify-item {{
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 15px;
            transition: all 0.3s;
        }}
        .verify-item:hover {{ background: rgba(0,0,0,0.5); transform: translateX(5px); }}
        .verify-header {{ display: flex; align-items: center; gap: 15px; margin-bottom: 8px; }}
        .verify-icon {{ font-size: 1.5em; }}
        .verify-component {{ font-size: 1.1em; font-weight: bold; flex: 1; }}
        .verify-status {{ font-size: 0.95em; font-weight: bold; padding: 4px 12px; background: rgba(0,0,0,0.3); border-radius: 20px; }}
        .verify-details {{ color: #aaa; font-size: 0.95em; margin-left: 45px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 25px; margin-bottom: 40px; }}
        
        .card {{
            background: linear-gradient(145deg, #1e1e3f 0%, #2a2a5a 100%);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            animation: slideUp 0.6s ease-out both;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s;
        }}
        .card:hover {{ transform: translateY(-8px); box-shadow: 0 20px 50px rgba(102, 126, 234, 0.3); }}
        .card:nth-child(1) {{ animation-delay: 0.05s; }}
        .card:nth-child(2) {{ animation-delay: 0.1s; }}
        .card:nth-child(3) {{ animation-delay: 0.15s; }}
        .card:nth-child(4) {{ animation-delay: 0.2s; }}
        .card:nth-child(5) {{ animation-delay: 0.25s; }}
        .card:nth-child(6) {{ animation-delay: 0.3s; }}
        .card:nth-child(7) {{ animation-delay: 0.35s; }}
        .card:nth-child(8) {{ animation-delay: 0.4s; }}
        .card:nth-child(9) {{ animation-delay: 0.45s; }}
        
        .card-header {{ display: flex; align-items: center; margin-bottom: 22px; padding-bottom: 18px; border-bottom: 2px solid rgba(255,255,255,0.1); }}
        .card-icon {{ font-size: 2.5em; margin-right: 15px; animation: pulse 2s infinite; }}
        .card-title {{ font-size: 1.4em; font-weight: bold; color: #00fff5; }}
        
        .info-row {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        .info-row:last-child {{ border-bottom: none; }}
        .info-label {{ color: #aaa; }}
        .info-value {{ color: #00ff88; font-weight: 600; text-align: right; max-width: 60%; }}
        
        .ram-stick {{ display: flex; align-items: center; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 12px; margin-bottom: 10px; }}
        .ram-icon {{ font-size: 2em; margin-right: 15px; }}
        .ram-details {{ flex: 1; }}
        
        .storage-item {{ margin-bottom: 20px; }}
        .storage-bar {{ height: 28px; background: rgba(255,255,255,0.1); border-radius: 14px; overflow: hidden; }}
        .storage-fill {{ height: 100%; border-radius: 14px; animation: fillBar 1.5s ease-out; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.85em; }}
        
        .disk-item, .gpu-item, .network-item {{ display: flex; align-items: center; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 12px; margin-bottom: 10px; }}
        
        .battery-display {{ text-align: center; padding: 25px; }}
        .battery-percent {{ font-size: 4em; font-weight: bold; color: {batt_color}; text-shadow: 0 0 30px {batt_color}; }}
        .health-section {{ margin-top: 25px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 15px; }}
        .health-bar {{ height: 35px; background: rgba(255,255,255,0.1); border-radius: 18px; overflow: hidden; margin: 15px 0; }}
        .health-fill {{ height: 100%; width: {health}%; background: {batt_color}; border-radius: 18px; animation: fillBar 1.5s ease-out; display: flex; align-items: center; justify-content: center; font-weight: bold; }}
        .health-status {{ text-align: center; font-size: 1.5em; font-weight: bold; color: {batt_color}; }}
        .battery-stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 20px; }}
        .battery-stat {{ text-align: center; padding: 12px; background: rgba(0,0,0,0.2); border-radius: 10px; }}
        .battery-stat-value {{ font-size: 1.3em; color: #00ff88; font-weight: bold; }}
        .battery-stat-label {{ font-size: 0.85em; color: #888; margin-top: 5px; }}
        
        .status-box {{ text-align: center; padding: 35px; background: rgba(0,0,0,0.3); border-radius: 20px; border: 3px solid {win_color}; }}
        .status-icon {{ font-size: 5em; margin-bottom: 15px; }}
        .status-text {{ font-size: 1.5em; font-weight: bold; color: {win_color}; }}
        
        .devices-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .device-item {{ text-align: center; padding: 20px 10px; background: rgba(0,0,0,0.25); border-radius: 15px; }}
        .device-icon {{ font-size: 2.5em; margin-bottom: 10px; }}
        .device-status {{ font-size: 1.5em; }}
        
        code {{ background: rgba(0, 255, 136, 0.15); padding: 4px 10px; border-radius: 6px; color: #00ff88; font-family: 'Consolas', monospace; }}
        
        .footer {{
            text-align: center;
            padding: 50px;
            margin-top: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 25px;
        }}
        .footer h2 {{ font-size: 2em; margin-bottom: 15px; }}
        
        @media print {{
            body {{ background: white !important; color: black !important; }}
            .card, .score-card, .verify-section {{ box-shadow: none !important; border: 2px solid #ddd !important; }}
        }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .grid {{ grid-template-columns: 1fr; }}
            .devices-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .score-summary {{ flex-direction: column; gap: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💻 LAPTOP HARDWARE REPORT</h1>
            <div class="subtitle">Complete Hardware Verification & Authenticity Check</div>
            <div class="model">{data.get('manufacturer', 'Unknown')} {data.get('model', 'Unknown')}</div>
            <div class="serial">🔑 Serial: {data.get('serial', 'N/A')}</div>
            <div class="date">📅 Generated: {datetime.now().strftime('%B %d, %Y at %I:%M:%S %p')}</div>
        </div>
        
        <!-- VERIFICATION SCORE -->
        <div class="score-card">
            <div class="score-title">🔍 HARDWARE AUTHENTICITY SCORE</div>
            <div class="score-circle">
                <div class="score-inner">
                    <div class="score-number">{score}</div>
                    <div class="score-label">/ 100</div>
                </div>
            </div>
            <div class="score-grade">{score_grade}</div>
            <div class="score-verdict">{score_verdict}</div>
            <div class="score-summary">
                <div class="score-stat">
                    <div class="score-stat-icon">✅</div>
                    <div class="score-stat-num" style="color:#00ff88;">{verification.get('original_count', 0)}</div>
                    <div class="score-stat-label">Original</div>
                </div>
                <div class="score-stat">
                    <div class="score-stat-icon">⚠️</div>
                    <div class="score-stat-num" style="color:#ffcc00;">{verification.get('suspicious_count', 0)}</div>
                    <div class="score-stat-label">Suspicious</div>
                </div>
                <div class="score-stat">
                    <div class="score-stat-icon">🔴</div>
                    <div class="score-stat-num" style="color:#ff4444;">{verification.get('replaced_count', 0)}</div>
                    <div class="score-stat-label">Replaced</div>
                </div>
            </div>
        </div>
        
        <!-- VERIFICATION DETAILS -->
        <div class="verify-section">
            <div class="verify-section-title">
                <span style="font-size:1.5em;">🔍</span>
                Component Verification Results
            </div>
            {verification_html}
        </div>
        
        <!-- HARDWARE DETAILS -->
        <div class="grid">
            <div class="card">
                <div class="card-header"><span class="card-icon">💻</span><span class="card-title">System Information</span></div>
                <div class="info-row"><span class="info-label">Manufacturer</span><span class="info-value">{data.get('manufacturer', 'N/A')}</span></div>
                <div class="info-row"><span class="info-label">Model</span><span class="info-value">{data.get('model', 'N/A')}</span></div>
                <div class="info-row"><span class="info-label">Serial Number</span><span class="info-value" style="color:#ffcc00;">{data.get('serial', 'N/A')}</span></div>
                <div class="info-row"><span class="info-label">OS</span><span class="info-value">{data.get('windows_edition', data.get('os', 'N/A'))}</span></div>
                <div class="info-row"><span class="info-label">BIOS</span><span class="info-value">{data.get('bios_version', 'N/A')}</span></div>
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">⚡</span><span class="card-title">Processor (CPU)</span></div>
                <div class="info-row"><span class="info-label">Processor</span><span class="info-value">{data.get('cpu_name', 'N/A')}</span></div>
                <div class="info-row"><span class="info-label">Cores / Threads</span><span class="info-value">{data.get('cpu_cores', 'N/A')} / {data.get('cpu_threads', 'N/A')}</span></div>
                <div class="info-row"><span class="info-label">Max Speed</span><span class="info-value">{data.get('cpu_speed', 'N/A')} MHz</span></div>
                <div class="info-row"><span class="info-label">CPU ID</span><span class="info-value"><code>{data.get('cpu_id', 'N/A')}</code></span></div>
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">🧠</span><span class="card-title">Memory (RAM)</span></div>
                <div style="text-align:center;padding:15px;background:rgba(0,0,0,0.2);border-radius:15px;margin-bottom:15px;">
                    <div style="font-size:3em;color:#00ff88;font-weight:bold;">{data.get('total_ram', 'N/A')} GB</div>
                    <div style="color:#888;">{data.get('ram_type', 'DDR4')} @ {data.get('ram_speed', 'N/A')} MHz</div>
                </div>
                {ram_html}
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">💾</span><span class="card-title">Storage</span></div>
                {disks_html}
                <div style="margin-top:15px;">{storage_html}</div>
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">🔋</span><span class="card-title">Battery Health</span></div>
                <div class="battery-display">
                    <div style="font-size:3.5em;">{batt_emoji}</div>
                    <div class="battery-percent">{data.get('battery_charge', 'N/A')}%</div>
                    <div style="color:#888;">{data.get('battery_status', 'Unknown')}</div>
                </div>
                <div class="health-section">
                    <div style="text-align:center;margin-bottom:10px;">Battery Health</div>
                    <div class="health-bar"><div class="health-fill">{health}%</div></div>
                    <div class="health-status">{batt_status}</div>
                    <div class="battery-stats">
                        <div class="battery-stat"><div class="battery-stat-value">{data.get('battery_design', 'N/A')}</div><div class="battery-stat-label">Design (mWh)</div></div>
                        <div class="battery-stat"><div class="battery-stat-value">{data.get('battery_current', 'N/A')}</div><div class="battery-stat-label">Current (mWh)</div></div>
                        <div class="battery-stat"><div class="battery-stat-value">{data.get('battery_cycles', 'N/A')}</div><div class="battery-stat-label">Cycles</div></div>
                        <div class="battery-stat"><div class="battery-stat-value">{health}%</div><div class="battery-stat-label">Health</div></div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">🎮</span><span class="card-title">Graphics (GPU)</span></div>
                {gpus_html}
                <div style="margin-top:15px;">
                    <div class="info-row"><span class="info-label">Resolution</span><span class="info-value">{data.get('resolution', 'N/A')}</span></div>
                    <div class="info-row"><span class="info-label">Refresh Rate</span><span class="info-value">{data.get('refresh_rate', 'N/A')} Hz</span></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">🌐</span><span class="card-title">Network</span></div>
                {network_html}
                <div style="margin-top:15px;"><div class="info-row"><span class="info-label">IP Address</span><span class="info-value"><code>{data.get('ip_address', 'N/A')}</code></span></div></div>
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">🎤</span><span class="card-title">Devices</span></div>
                <div class="devices-grid">
                    <div class="device-item"><div class="device-icon">📷</div><div style="color:#aaa;font-size:0.85em;">Webcam</div><div class="device-status">{"✅" if cam_ok else "❌"}</div></div>
                    <div class="device-item"><div class="device-icon">👆</div><div style="color:#aaa;font-size:0.85em;">Touch</div><div class="device-status">{"✅" if touch_ok else "❌"}</div></div>
                    <div class="device-item"><div class="device-icon">🔵</div><div style="color:#aaa;font-size:0.85em;">Bluetooth</div><div class="device-status">{"✅" if bt_ok else "❌"}</div></div>
                    <div class="device-item"><div class="device-icon">🔊</div><div style="color:#aaa;font-size:0.85em;">Audio</div><div class="device-status">✅</div></div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header"><span class="card-icon">🪟</span><span class="card-title">Windows</span></div>
                <div class="status-box">
                    <div class="status-icon">{win_icon}</div>
                    <div class="status-text">{win_text}</div>
                    <div style="margin-top:15px;color:#888;">Key: <code>{data.get('windows_key', 'N/A')}</code></div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <h2>💜 Made with Love by PRASHUN 💜</h2>
            <p>Laptop Hardware Checker - Your Trusted Verification Tool</p>
            <p style="margin-top:15px;opacity:0.7;">© {datetime.now().year} Prashun - All Rights Reserved</p>
        </div>
    </div>
</body>
</html>'''
        return html

    # ==================== TEXT INFO FUNCTIONS ====================
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
  
  --- MOTHERBOARD ---
  Manufacturer   : {self.run_powershell("(Get-WmiObject Win32_BaseBoard).Manufacturer")}
  Product        : {self.run_powershell("(Get-WmiObject Win32_BaseBoard).Product")}
  Serial Number  : {self.run_powershell("(Get-WmiObject Win32_BaseBoard).SerialNumber")}
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
  CPU ID         : {self.run_powershell("(Get-WmiObject Win32_Processor).ProcessorId")}
"""

    def get_ram_info(self):
        ram_sticks = self.run_powershell("""
            Get-WmiObject Win32_PhysicalMemory | ForEach-Object {
                "  $($_.DeviceLocator) : $([math]::Round($_.Capacity/1GB,0)) GB @ $($_.Speed) MHz ($($_.Manufacturer))"
            }
        """)
        return f"""
{'='*60}
              🧠 RAM INFORMATION
{'='*60}

  Total RAM      : {self.run_powershell("[math]::Round((Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory/1GB,2)")} GB
  Slots Used     : {self.run_powershell("(Get-WmiObject Win32_PhysicalMemory).Count")}
  
  --- RAM MODULES ---
{ram_sticks}
"""

    def get_storage_info(self):
        disks = self.run_powershell("""
            Get-WmiObject Win32_DiskDrive | ForEach-Object {
                "  $($_.Model) - $([math]::Round($_.Size/1GB,2)) GB"
            }
        """)
        partitions = self.run_powershell("""
            Get-WmiObject Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | ForEach-Object {
                $used = [math]::Round(($_.Size - $_.FreeSpace)/1GB,2)
                $total = [math]::Round($_.Size/1GB,2)
                "  $($_.DeviceID) : $used GB / $total GB used"
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
"""

    def get_battery_info(self):
        return f"""
{'='*60}
              🔋 BATTERY INFORMATION
{'='*60}

  Current Charge : {self.run_powershell("(Get-WmiObject Win32_Battery).EstimatedChargeRemaining")}%
  Status         : {self.run_powershell("$s=(Get-WmiObject Win32_Battery).BatteryStatus;switch($s){1{'Discharging'}2{'AC Connected'}3{'Fully Charged'}6{'Charging'}default{'Unknown'}}")}
  
  --- BATTERY HEALTH ---
  Health         : {self.run_powershell("try{$f=(Get-WmiObject -Namespace root/WMI -Class BatteryFullChargedCapacity -EA SilentlyContinue).FullChargedCapacity;$d=(Get-WmiObject -Namespace root/WMI -Class BatteryStaticData -EA SilentlyContinue).DesignedCapacity;if($f -and $d){[math]::Round(($f/$d)*100,1)}else{'N/A'}}catch{'N/A'}")}%
  Cycle Count    : {self.run_powershell("(Get-WmiObject -Namespace root/WMI -Class BatteryCycleCount -EA SilentlyContinue).CycleCount")}
"""

    def get_gpu_info(self):
        gpus = self.run_powershell("""
            Get-WmiObject Win32_VideoController | ForEach-Object {
                "  $($_.Name) - $([math]::Round($_.AdapterRAM/1GB,2)) GB"
            }
        """)
        return f"""
{'='*60}
              🎮 GPU INFORMATION
{'='*60}

{gpus}
  
  Resolution     : {self.run_powershell("$g=Get-WmiObject Win32_VideoController|Select-Object -First 1;\"$($g.CurrentHorizontalResolution) x $($g.CurrentVerticalResolution)\"")}
  Refresh Rate   : {self.run_powershell("(Get-WmiObject Win32_VideoController|Select-Object -First 1).CurrentRefreshRate")} Hz
"""

    def get_network_info(self):
        adapters = self.run_powershell("""
            Get-WmiObject Win32_NetworkAdapter | Where-Object {$_.MACAddress -and $_.PhysicalAdapter} | ForEach-Object {
                "  $($_.Name)"
                "    MAC: $($_.MACAddress)"
            }
        """)
        return f"""
{'='*60}
              🌐 NETWORK INFORMATION
{'='*60}

  IP Address     : {self.run_powershell("(Get-WmiObject Win32_NetworkAdapterConfiguration|Where-Object{$_.IPAddress}|Select-Object -First 1).IPAddress[0]")}
  
{adapters}
"""

    def get_display_info(self):
        return f"""
{'='*60}
              🖥️ DISPLAY INFORMATION
{'='*60}

  Resolution     : {self.run_powershell("$g=Get-WmiObject Win32_VideoController|Select-Object -First 1;\"$($g.CurrentHorizontalResolution) x $($g.CurrentVerticalResolution)\"")}
  Refresh Rate   : {self.run_powershell("(Get-WmiObject Win32_VideoController|Select-Object -First 1).CurrentRefreshRate")} Hz
  Touch Screen   : {self.run_powershell("if(Get-WmiObject Win32_PnPEntity|Where-Object{$_.Name -like '*touch*'}){'Yes'}else{'No'}")}
"""

    def get_devices_info(self):
        return f"""
{'='*60}
              🎤 DEVICES INFORMATION
{'='*60}

  Webcam         : {self.run_powershell("$c=Get-WmiObject Win32_PnPEntity|Where-Object{$_.PNPClass -eq 'Camera' -or $_.Name -like '*webcam*' -or $_.Name -like '*camera*'};if($c){($c|Select-Object -First 1).Name}else{'Not Detected'}")}
  Audio Device   : {self.run_powershell("(Get-WmiObject Win32_SoundDevice|Select-Object -First 1).Name")}
  Bluetooth      : {self.run_powershell("if(Get-WmiObject Win32_PnPEntity|Where-Object{$_.Name -like '*bluetooth*'}){'Available'}else{'Not Found'}")}
"""

    def get_windows_info(self):
        return f"""
{'='*60}
              🪟 WINDOWS INFORMATION
{'='*60}

  Edition        : {self.run_powershell("(Get-WmiObject Win32_OperatingSystem).Caption")}
  Build          : {self.run_powershell("(Get-WmiObject Win32_OperatingSystem).BuildNumber")}
  
  --- ACTIVATION ---
  Activated      : {self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;if($l.LicenseStatus -eq 1){'Yes - Genuine'}else{'No'}")}
  Product Key    : {self.run_powershell("$l=Get-WmiObject SoftwareLicensingProduct|Where-Object{$_.PartialProductKey -and $_.Name -like '*Windows*'}|Select-Object -First 1;'XXXXX-XXXXX-XXXXX-XXXXX-'+$l.PartialProductKey")}
"""

    def get_all_info(self):
        return f"""
{'='*65}
          COMPLETE LAPTOP HARDWARE REPORT
          Generated by: Prashun's Laptop Checker
          Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*65}
{self.get_system_info()}
{self.get_cpu_info()}
{self.get_ram_info()}
{self.get_storage_info()}
{self.get_battery_info()}
{self.get_gpu_info()}
{self.get_network_info()}
{self.get_display_info()}
{self.get_devices_info()}
{self.get_windows_info()}
{self.get_verification_info()}
{'='*65}
              💜 Made with Love by PRASHUN 💜
{'='*65}
"""


def main():
    root = tk.Tk()
    app = LaptopChecker(root)
    root.mainloop()


if __name__ == "__main__":
    main()