# -*- coding: utf-8 -*-
"""
File chính để khởi chạy ứng dụng AutoSIC
"""
import tkinter as tk
from components.ui_components import AutoSICUI
from components.automation_core import AutomationCore
from components.stats_manager import StatsManager
from components.loop_detector import LoopDetector


class AutoSICApp:
    """Class chính quản lý toàn bộ ứng dụng"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        
        # Khởi tạo các components
        self.ui = AutoSICUI(root)
        self.automation = AutomationCore()
        self.stats = StatsManager()
        self.loop_detector = LoopDetector()
        
        self.setup_callbacks()
        
        # Biến trạng thái
        self.is_running = False
    
    def setup_callbacks(self):
        """Thiết lập các callbacks giữa các components"""        # UI callbacks
        self.ui.set_toggle_automation_callback(self.toggle_automation)
        self.ui.set_test_detect_callback(self.test_detect)
        self.ui.set_open_asset_manager_callback(self.open_asset_manager)
        self.ui.set_reset_auto_restart_callback(self.reset_auto_restart)
        self.ui.set_reset_stats_callback(self.reset_stats)
        
        # Automation callbacks
        self.automation.set_log_callback(self.ui.log_message)
        self.automation.set_stats_callback(self.update_stats)
        self.automation.set_step_callback(self.ui.update_step_status)
        self.automation.set_loop_check_callback(self.loop_detector.check_loop_detection)
        
        # Loop detector callbacks
        self.loop_detector.set_auto_restart_callback(self.auto_restart)
        self.loop_detector.set_status_update_callback(self.ui.update_loop_status)
    
    def toggle_automation(self):
        """Bật/tắt automation"""
        if not self.is_running:
            self.start_automation()
        else:
            self.stop_automation()
    
    def start_automation(self):
        """Bắt đầu automation"""
        self.is_running = True
        self.ui.update_start_button(True)
        
        # Bắt đầu đếm thời gian
        self.stats.start_timer()
        
        # Bắt đầu automation
        self.automation.start_automation()
        
        self.ui.log_message("Bắt đầu automation")
        
        # Bắt đầu timer để cập nhật stats
        self.update_stats_display()
    
    def stop_automation(self):
        """Dừng automation"""
        self.is_running = False
        self.ui.update_start_button(False)
        
        # Dừng automation
        self.automation.stop_automation()
        
        self.ui.log_message("Dừng automation")
    
    def auto_restart(self):
        """Tự động restart automation"""
        self.ui.log_message("🔄 Phát hiện lặp vô hạn! Tự động restart...")
        
        # Dừng automation hiện tại
        self.stop_automation()
        
        # Đợi một chút rồi bắt đầu lại
        self.root.after(3000, self.start_automation)  # Sau 3 giây
    
    def update_stats(self, stat_type: str):
        """Cập nhật thống kê"""
        if stat_type == 'lessons_clicked':
            self.stats.increment_lessons_clicked()
        elif stat_type == 'play_buttons_detected':
            self.stats.increment_play_buttons_detected()
        elif stat_type == 'refresh_clicks':
            self.stats.increment_refresh_clicks()
        elif stat_type == 'expand_clicks':
            self.stats.increment_expand_clicks()
        
        # Cập nhật hiển thị
        self.update_stats_display()
    
    def update_stats_display(self):
        """Cập nhật hiển thị thống kê trên UI"""
        stats = self.stats.get_all_stats()
        runtime = self.stats.get_runtime()
        auto_restart_count = self.loop_detector.get_auto_restart_count()
        
        self.ui.update_stats_display(
            stats['lessons_clicked'],
            stats['play_buttons_detected'],
            stats['expand_clicks'],
            auto_restart_count,
            runtime
        )
        
        # Lên lịch cập nhật tiếp theo nếu đang chạy
        if self.is_running:
            self.root.after(5000, self.update_stats_display)  # Cập nhật mỗi 5 giây

    def test_detect(self):
        """Test các function detect"""
        self.automation.test_detect()
    
    def open_asset_manager(self):
        """Mở cửa sổ Asset Manager"""
        try:
            from components.asset_manager_ui import AssetManagerWindow
            
            # Tạo cửa sổ Asset Manager
            asset_manager_window = AssetManagerWindow(self.root, "Assets")
            
            # Thiết lập callback khi asset được cập nhật
            def on_asset_updated(asset_key):
                self.ui.log_message(f"📦 Asset '{asset_key}' đã được cập nhật")
                # Reload asset trong automation core
                if hasattr(self.automation, 'image_detector'):
                    self.automation.image_detector.reload_asset(asset_key)
            
            asset_manager_window.set_asset_updated_callback(on_asset_updated)
            
            self.ui.log_message("🔧 Đã mở Asset Manager")
            
        except Exception as e:
            self.ui.log_message(f"❌ Lỗi khi mở Asset Manager: {str(e)}")
    
    def reset_auto_restart(self):
        """Reset bộ đếm auto restart"""
        self.loop_detector.reset_auto_restart_count()
        self.ui.log_message("🔄 Đã reset bộ đếm auto restart")
        self.update_stats_display()
    
    def reset_stats(self):
        """Reset thống kê"""
        self.stats.reset_stats()
        self.ui.log_message("Đã reset thống kê")
        self.update_stats_display()


def main():
    """Function chính để chạy ứng dụng"""
    root = tk.Tk()
    app = AutoSICApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
