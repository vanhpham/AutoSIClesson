# -*- coding: utf-8 -*-
"""
Module UI components cho ứng dụng AutoSIC
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import time
from typing import Callable, Optional, List


class AutoSICUI:
    """Class quản lý giao diện người dùng"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_window()
        self.setup_ui()        # Callbacks
        self.on_toggle_automation: Optional[Callable] = None
        self.on_test_detect: Optional[Callable] = None
        self.on_open_asset_manager: Optional[Callable] = None
        self.on_reset_auto_restart: Optional[Callable] = None
        self.on_reset_stats: Optional[Callable] = None
    
    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.title("AutoSIC - Tự động chạy bài học")
        self.root.geometry("800x1000+2000+200")
        self.root.resizable(True, True)
        self.root.attributes('-topmost', True)  # Thêm dòng này để cửa sổ luôn ở trên cùng
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid weight
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Thiết lập các phần của UI
        self._setup_title(main_frame)
        self._setup_control_frame(main_frame)
        self._setup_step_frame(main_frame)
        self._setup_log_frame(main_frame)
        self._setup_stats_frame(main_frame)
    
    def _setup_title(self, parent):
        """Thiết lập tiêu đề"""
        title_label = ttk.Label(parent, text="AutoSIC - Tự động chạy bài học", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
    
    def _setup_control_frame(self, parent):
        """Thiết lập frame điều khiển"""
        control_frame = ttk.LabelFrame(parent, text="Điều khiển", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Nút bắt đầu/dừng
        self.start_button = ttk.Button(control_frame, text="Bắt đầu", 
                                      command=self._on_toggle_automation)
        self.start_button.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)        # Nút test detect
        test_button = ttk.Button(control_frame, text="Test Detect", 
                                command=self._on_test_detect)
        test_button.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        # Nút Asset Manager
        asset_manager_button = ttk.Button(control_frame, text="Asset Manager", 
                                         command=self._on_open_asset_manager)
        asset_manager_button.grid(row=0, column=2, padx=(0, 10), sticky=tk.W)
        
        # Nút reset auto restart
        reset_restart_button = ttk.Button(control_frame, text="Reset Auto Restart", 
                                         command=self._on_reset_auto_restart)
        reset_restart_button.grid(row=0, column=3, padx=(0, 10), sticky=tk.W)
          # Trạng thái
        self.status_label = ttk.Label(control_frame, text="Trạng thái: Đã dừng", 
                                     foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))
    
    def _setup_step_frame(self, parent):
        """Thiết lập frame trạng thái bước"""
        step_frame = ttk.LabelFrame(parent, text="Trạng thái thực hiện", padding="10")
        step_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        step_frame.columnconfigure(1, weight=1)
        
        # Bước hiện tại
        ttk.Label(step_frame, text="Bước hiện tại:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.current_step_label = ttk.Label(step_frame, text="Chưa bắt đầu", foreground="blue")
        self.current_step_label.grid(row=0, column=1, sticky=tk.W)
        
        # Các bước tiếp theo
        ttk.Label(step_frame, text="Bước tiếp theo:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.next_steps_label = ttk.Label(step_frame, text="", foreground="gray")
        self.next_steps_label.grid(row=1, column=1, sticky=tk.W)
        
        # Trạng thái chống lặp
        ttk.Label(step_frame, text="Chống lặp:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.loop_status_label = ttk.Label(step_frame, text="Bình thường", foreground="green")
        self.loop_status_label.grid(row=2, column=1, sticky=tk.W)
    
    def _setup_log_frame(self, parent):
        """Thiết lập frame log"""
        log_frame = ttk.LabelFrame(parent, text="Log hoạt động", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text area cho log
        self.log_text = scrolledtext.ScrolledText(log_frame, width=70, height=15)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Nút xóa log
        clear_button = ttk.Button(log_frame, text="Xóa Log", command=self.clear_log)
        clear_button.grid(row=1, column=0, pady=(10, 0), sticky=tk.W)
    
    def _setup_stats_frame(self, parent):
        """Thiết lập frame thống kê"""
        stats_frame = ttk.LabelFrame(parent, text="Thống kê", padding="10")
        stats_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        stats_frame.columnconfigure(1, weight=1)
        
        # Labels thống kê
        ttk.Label(stats_frame, text="Lessons đã click:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.lessons_clicked_label = ttk.Label(stats_frame, text="0", foreground="blue")
        self.lessons_clicked_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Videos hoàn thành:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.play_buttons_label = ttk.Label(stats_frame, text="0", foreground="green")
        self.play_buttons_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Lần expand:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.expand_label = ttk.Label(stats_frame, text="0", foreground="orange")
        self.expand_label.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Auto restart:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10))
        self.auto_restart_label = ttk.Label(stats_frame, text="0", foreground="red")
        self.auto_restart_label.grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Thời gian chạy:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10))
        self.runtime_label = ttk.Label(stats_frame, text="00:00:00", foreground="purple")
        self.runtime_label.grid(row=4, column=1, sticky=tk.W)
        
        # Nút reset thống kê
        reset_stats_button = ttk.Button(stats_frame, text="Reset Thống kê", 
                                       command=self._on_reset_stats)
        reset_stats_button.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
      # Callback methods
    def set_toggle_automation_callback(self, callback: Callable):
        """Thiết lập callback cho nút bắt đầu/dừng"""
        self.on_toggle_automation = callback
    
    def set_test_detect_callback(self, callback: Callable):
        """Thiết lập callback cho nút test detect"""
        self.on_test_detect = callback
    
    def set_open_asset_manager_callback(self, callback: Callable):
        """Thiết lập callback cho nút Asset Manager"""
        self.on_open_asset_manager = callback
    
    def set_reset_auto_restart_callback(self, callback: Callable):
        """Thiết lập callback cho nút reset auto restart"""
        self.on_reset_auto_restart = callback
    
    def set_reset_stats_callback(self, callback: Callable):
        """Thiết lập callback cho nút reset stats"""
        self.on_reset_stats = callback
    def _on_toggle_automation(self):
        if self.on_toggle_automation:
            self.on_toggle_automation()
    
    def _on_test_detect(self):
        if self.on_test_detect:
            self.on_test_detect()
    
    def _on_open_asset_manager(self):
        if self.on_open_asset_manager:
            self.on_open_asset_manager()
    
    def _on_reset_auto_restart(self):
        if self.on_reset_auto_restart:
            self.on_reset_auto_restart()
    
    def _on_reset_stats(self):
        if self.on_reset_stats:
            self.on_reset_stats()
    
    # UI update methods
    def update_start_button(self, is_running: bool):
        """Cập nhật text và trạng thái nút start"""
        if is_running:
            self.start_button.config(text="Dừng")
            self.status_label.config(text="Trạng thái: Đang chạy", foreground="green")
        else:
            self.start_button.config(text="Bắt đầu")
            self.status_label.config(text="Trạng thái: Đã dừng", foreground="red")
    
    def update_step_status(self, current_step: str, next_steps: Optional[List[str]] = None):
        """Cập nhật trạng thái bước hiện tại và tiếp theo"""
        self.current_step_label.config(text=current_step)
        
        if next_steps:
            next_text = " → ".join(next_steps[:3])  # Hiển thị tối đa 3 bước tiếp theo
            if len(next_steps) > 3:
                next_text += " → ..."
            self.next_steps_label.config(text=next_text)
        else:
            self.next_steps_label.config(text="")
    
    def update_loop_status(self, status: str, color: str = "green"):
        """Cập nhật trạng thái chống lặp"""
        self.loop_status_label.config(text=status, foreground=color)
    
    def update_stats_display(self, lessons_clicked: int, play_buttons: int, 
                           expand_clicks: int, auto_restart_count: int, runtime: str):
        """Cập nhật hiển thị thống kê"""
        self.lessons_clicked_label.config(text=str(lessons_clicked))
        self.play_buttons_label.config(text=str(play_buttons))
        self.expand_label.config(text=str(expand_clicks))
        self.auto_restart_label.config(text=str(auto_restart_count))
        self.runtime_label.config(text=runtime)
    
    def log_message(self, message: str):
        """Thêm message vào log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Xóa toàn bộ log"""
        self.log_text.delete(1.0, tk.END)
