# -*- coding: utf-8 -*-
"""
Asset Manager UI - Giao diện quản lý assets
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
from typing import Dict, Optional, Callable
from .asset_manager import AssetManager


class AssetManagerWindow:
    """Cửa sổ quản lý assets"""
    
    def __init__(self, parent: tk.Tk, assets_path: str = "Assets"):
        self.parent = parent
        self.assets_path = assets_path
        self.asset_manager = AssetManager(assets_path)
        
        # Tạo cửa sổ mới
        self.window = tk.Toplevel(parent)
        self.setup_window()
        self.setup_ui()
        
        # Load assets
        self.load_assets_list()
        
        # Callbacks
        self.on_asset_updated: Optional[Callable] = None
    
    def setup_window(self):
        """Thiết lập cửa sổ Asset Manager"""
        self.window.title("Asset Manager - Quản lý hình ảnh")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Đặt cửa sổ ở giữa màn hình
        self.window.transient(self.parent)
        self.window.grab_set()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Asset list
        self._setup_asset_list_panel(main_frame)
        
        # Right panel - Asset details
        self._setup_asset_details_panel(main_frame)
        
        # Bottom panel - Actions
        self._setup_actions_panel(main_frame)
    
    def _setup_asset_list_panel(self, parent):
        """Thiết lập panel danh sách assets"""
        # Left frame
        left_frame = ttk.LabelFrame(parent, text="Danh sách Assets", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # Treeview cho danh sách assets
        columns = ("file", "status", "size")
        self.assets_tree = ttk.Treeview(left_frame, columns=columns, show="tree headings", height=15)
        
        # Định nghĩa columns
        self.assets_tree.heading("#0", text="Asset Key")
        self.assets_tree.heading("file", text="File")
        self.assets_tree.heading("status", text="Trạng thái")
        self.assets_tree.heading("size", text="Kích thước")
        
        # Cấu hình column widths
        self.assets_tree.column("#0", width=150)
        self.assets_tree.column("file", width=120)
        self.assets_tree.column("status", width=80)
        self.assets_tree.column("size", width=80)
        
        # Scrollbar cho treeview
        tree_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.assets_tree.yview)
        self.assets_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview và scrollbar
        self.assets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.assets_tree.bind("<<TreeviewSelect>>", self.on_asset_selected)
    
    def _setup_asset_details_panel(self, parent):
        """Thiết lập panel chi tiết asset"""
        # Right frame
        right_frame = ttk.LabelFrame(parent, text="Chi tiết Asset", padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Asset info frame
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Asset key
        ttk.Label(info_frame, text="Asset Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.asset_key_label = ttk.Label(info_frame, text="", font=("Arial", 10, "bold"))
        self.asset_key_label.grid(row=0, column=1, sticky=tk.W)
        
        # File path
        ttk.Label(info_frame, text="File Path:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_label = ttk.Label(info_frame, text="")
        self.file_path_label.grid(row=1, column=1, sticky=tk.W)
        
        # Image dimensions
        ttk.Label(info_frame, text="Kích thước:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.dimensions_label = ttk.Label(info_frame, text="")
        self.dimensions_label.grid(row=2, column=1, sticky=tk.W)
        
        # Image preview frame
        preview_frame = ttk.LabelFrame(right_frame, text="Xem trước", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas for image preview
        self.preview_canvas = tk.Canvas(preview_frame, bg="white", height=200)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Test detection frame
        test_frame = ttk.LabelFrame(right_frame, text="Test Detection", padding="5")
        test_frame.pack(fill=tk.X)
        
        # Test button
        self.test_detect_button = ttk.Button(test_frame, text="Test Detect Asset", 
                                           command=self.test_current_asset)
        self.test_detect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Test result label
        self.test_result_label = ttk.Label(test_frame, text="")
        self.test_result_label.pack(side=tk.LEFT)
    
    def _setup_actions_panel(self, parent):
        """Thiết lập panel hành động"""
        actions_frame = ttk.LabelFrame(parent, text="Hành động", padding="5")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Replace asset button
        self.replace_button = ttk.Button(actions_frame, text="Thay thế Asset", 
                                       command=self.replace_current_asset, state=tk.DISABLED)
        self.replace_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reload all assets button
        reload_button = ttk.Button(actions_frame, text="Reload All Assets", 
                                 command=self.reload_all_assets)
        reload_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Test all assets button
        test_all_button = ttk.Button(actions_frame, text="Test All Assets", 
                                   command=self.test_all_assets)
        test_all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Validate assets button
        validate_button = ttk.Button(actions_frame, text="Validate Assets", 
                                   command=self.validate_assets)
        validate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_button = ttk.Button(actions_frame, text="Đóng", 
                                command=self.window.destroy)
        close_button.pack(side=tk.RIGHT)
    
    def load_assets_list(self):
        """Load danh sách assets vào treeview"""
        # Clear existing items
        for item in self.assets_tree.get_children():
            self.assets_tree.delete(item)
        
        # Get assets info từ asset manager
        assets_info = self.asset_manager.get_all_assets_info()
        
        for asset_key, info in assets_info.items():
            file_name = os.path.basename(info['file_path']) if info['file_path'] else "N/A"
            status = "✅" if info['loaded'] else "❌"
            size = f"{info['width']}x{info['height']}" if info['loaded'] else "N/A"
            
            self.assets_tree.insert("", tk.END, text=asset_key, 
                                  values=(file_name, status, size))
    
    def on_asset_selected(self, event):
        """Xử lý khi chọn asset trong tree"""
        selection = self.assets_tree.selection()
        if not selection:
            self.clear_asset_details()
            return
        
        # Lấy asset key được chọn
        item = selection[0]
        asset_key = self.assets_tree.item(item, "text")
        
        # Hiển thị chi tiết asset
        self.display_asset_details(asset_key)
    
    def display_asset_details(self, asset_key: str):
        """Hiển thị chi tiết của asset"""
        assets_info = self.asset_manager.get_all_assets_info()
        
        if asset_key not in assets_info:
            self.clear_asset_details()
            return
        
        info = assets_info[asset_key]
        
        # Update labels
        self.asset_key_label.config(text=asset_key)
        self.file_path_label.config(text=info['file_path'] or "N/A")
        
        if info['loaded']:
            self.dimensions_label.config(text=f"{info['width']} x {info['height']} pixels")
            self.replace_button.config(state=tk.NORMAL)
            
            # Load và hiển thị preview
            self.load_image_preview(info['file_path'])
        else:
            self.dimensions_label.config(text="Asset không load được")
            self.replace_button.config(state=tk.DISABLED)
            self.clear_image_preview()
        
        # Clear test result
        self.test_result_label.config(text="")
    
    def clear_asset_details(self):
        """Xóa thông tin chi tiết asset"""
        self.asset_key_label.config(text="")
        self.file_path_label.config(text="")
        self.dimensions_label.config(text="")
        self.replace_button.config(state=tk.DISABLED)
        self.test_result_label.config(text="")
        self.clear_image_preview()
    
    def load_image_preview(self, image_path: str):
        """Load và hiển thị preview của hình ảnh"""
        try:
            # Mở hình ảnh
            image = Image.open(image_path)
            
            # Resize để fit trong canvas (max 300x200)
            canvas_width = self.preview_canvas.winfo_width() or 300
            canvas_height = self.preview_canvas.winfo_height() or 200
            
            # Calculate scale to fit
            scale_x = canvas_width / image.width
            scale_y = canvas_height / image.height
            scale = min(scale_x, scale_y, 1.0)  # Không scale up
            
            new_width = int(image.width * scale)
            new_height = int(image.height * scale)
            
            # Resize image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.preview_photo = ImageTk.PhotoImage(resized_image)
            
            # Clear canvas và hiển thị image
            self.preview_canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)
            
        except Exception as e:
            self.clear_image_preview()
            print(f"Lỗi load preview: {str(e)}")
    
    def clear_image_preview(self):
        """Xóa preview hình ảnh"""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(150, 100, text="Không có preview", 
                                      fill="gray", font=("Arial", 12))
    
    def replace_current_asset(self):
        """Thay thế asset hiện tại"""
        selection = self.assets_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn asset để thay thế")
            return
        
        asset_key = self.assets_tree.item(selection[0], "text")
        
        # Mở dialog chọn file
        file_path = filedialog.askopenfilename(
            title=f"Chọn hình ảnh thay thế cho {asset_key}",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Backup file cũ
            assets_info = self.asset_manager.get_all_assets_info()
            old_file = assets_info[asset_key]['file_path']
            
            if old_file and os.path.exists(old_file):
                backup_path = old_file + ".backup"
                shutil.copy2(old_file, backup_path)
                print(f"Đã backup file cũ: {backup_path}")
            
            # Copy file mới
            new_file_path = os.path.join(self.assets_path, 
                                       self.asset_manager.asset_files[asset_key])
            shutil.copy2(file_path, new_file_path)
            
            # Reload asset
            success = self.asset_manager.reload_asset(asset_key)
            
            if success:
                messagebox.showinfo("Thành công", 
                                  f"Đã thay thế asset '{asset_key}' thành công!")
                
                # Refresh UI
                self.load_assets_list()
                self.display_asset_details(asset_key)
                
                # Callback notification
                if self.on_asset_updated:
                    self.on_asset_updated(asset_key)
            else:
                messagebox.showerror("Lỗi", f"Không thể reload asset '{asset_key}'")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thay thế asset: {str(e)}")
    
    def test_current_asset(self):
        """Test detect asset hiện tại"""
        selection = self.assets_tree.selection()
        if not selection:
            self.test_result_label.config(text="Chưa chọn asset", foreground="red")
            return
        
        asset_key = self.assets_tree.item(selection[0], "text")
        
        try:
            # Test detect asset
            result = self.asset_manager.test_detect_asset(asset_key)
            
            if result['found']:
                self.test_result_label.config(
                    text=f"✅ Tìm thấy {result['matches']} vị trí (confidence: {result['max_confidence']:.3f})",
                    foreground="green"
                )
            else:
                self.test_result_label.config(
                    text="❌ Không tìm thấy trên màn hình",
                    foreground="red"
                )
                
        except Exception as e:
            self.test_result_label.config(
                text=f"Lỗi: {str(e)}",
                foreground="red"
            )
    
    def test_all_assets(self):
        """Test detect tất cả assets"""
        try:
            results = self.asset_manager.test_detect_all_assets()
            
            # Tạo cửa sổ hiển thị kết quả
            result_window = tk.Toplevel(self.window)
            result_window.title("Kết quả Test All Assets")
            result_window.geometry("500x400")
            
            # Text widget để hiển thị kết quả
            text_widget = tk.Text(result_window, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(result_window, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # Insert results
            text_widget.insert(tk.END, "=== KẾT QUẢ TEST DETECT TẤT CẢ ASSETS ===\n\n")
            
            for asset_key, result in results.items():
                status = "✅" if result['found'] else "❌"
                if result['found']:
                    text_widget.insert(tk.END, f"{status} {asset_key}: Tìm thấy {result['matches']} vị trí (confidence: {result['max_confidence']:.3f})\n")
                else:
                    text_widget.insert(tk.END, f"{status} {asset_key}: Không tìm thấy\n")
            
            text_widget.config(state=tk.DISABLED)
            
            # Pack widgets
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi test assets: {str(e)}")
    
    def validate_assets(self):
        """Validate tất cả assets"""
        try:
            results = self.asset_manager.validate_assets()
            
            # Đếm assets hợp lệ/không hợp lệ
            valid_count = sum(1 for r in results.values() if r['valid'])
            total_count = len(results)
            
            # Hiển thị kết quả summary
            message = f"Kết quả validate:\n"
            message += f"- Hợp lệ: {valid_count}/{total_count} assets\n\n"
            
            # Chi tiết các assets không hợp lệ
            invalid_assets = {k: v for k, v in results.items() if not v['valid']}
            if invalid_assets:
                message += "Assets không hợp lệ:\n"
                for asset_key, result in invalid_assets.items():
                    message += f"- {asset_key}: {result['error']}\n"
            else:
                message += "Tất cả assets đều hợp lệ! ✅"
            
            messagebox.showinfo("Kết quả Validate", message)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi validate assets: {str(e)}")
    
    def reload_all_assets(self):
        """Reload tất cả assets"""
        try:
            success = self.asset_manager.reload_all_assets()
            
            if success:
                messagebox.showinfo("Thành công", "Đã reload tất cả assets thành công!")
            else:
                messagebox.showwarning("Cảnh báo", "Một số assets không reload được")
            
            # Refresh UI
            self.load_assets_list()
            self.clear_asset_details()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi reload assets: {str(e)}")
    
    def set_asset_updated_callback(self, callback: Callable):
        """Thiết lập callback khi asset được cập nhật"""
        self.on_asset_updated = callback
