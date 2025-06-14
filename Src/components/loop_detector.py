# -*- coding: utf-8 -*-
"""
Module phát hiện và xử lý lặp vô hạn
"""
from typing import Dict, Any, Callable


class LoopDetector:
    """Class phát hiện và xử lý lặp vô hạn"""
    
    def __init__(self, max_repeats: int = 3):
        self.loop_detection = {
            'last_action': None,
            'repeat_count': 0,
            'max_repeats': max_repeats,
            'auto_restart_count': 0
        }
        self.on_auto_restart_callback: Callable = None
        self.on_status_update_callback: Callable = None
    
    def set_auto_restart_callback(self, callback: Callable):
        """Thiết lập callback khi cần auto restart"""
        self.on_auto_restart_callback = callback
    
    def set_status_update_callback(self, callback: Callable):
        """Thiết lập callback cập nhật trạng thái"""
        self.on_status_update_callback = callback

    def check_loop_detection(self, action: str) -> bool:
        """
        Kiểm tra và xử lý lặp vô hạn
        
        Args:
            action: Tên hành động đang thực hiện
            
        Returns:
            bool: True nếu cần auto restart, False nếu không
        """
        is_play_button_action = "play button" in action.lower()

        if is_play_button_action:
            # Bỏ qua hoàn toàn các action liên quan đến play button
            if self.on_status_update_callback:
                self.on_status_update_callback("Bình thường (Play Button - Bỏ qua kiểm tra lặp)", "green")
            return False

        if self.loop_detection['last_action'] == action:
            self.loop_detection['repeat_count'] += 1

            if self.on_status_update_callback:
                status_color = "orange"
                status = f"Lặp {self.loop_detection['repeat_count']}/{self.loop_detection['max_repeats']}"
                self.on_status_update_callback(status, status_color)

            if self.loop_detection['repeat_count'] >= self.loop_detection['max_repeats']:
                print(f"🔄 Phát hiện lặp '{action}' quá {self.loop_detection['max_repeats']} lần! Tự động restart...")
                self.loop_detection['auto_restart_count'] += 1

                if self.on_status_update_callback:
                    self.on_status_update_callback("Auto restarting...", "red")

                # Reset loop detection sau khi trigger restart
                self.loop_detection['repeat_count'] = 0
                self.loop_detection['last_action'] = None

                if self.on_auto_restart_callback:
                    self.on_auto_restart_callback()

                return True
        else:
            # Hành động mới, không phải lặp của hành động trước đó
            self.loop_detection['last_action'] = action
            self.loop_detection['repeat_count'] = 1

            if self.on_status_update_callback:
                self.on_status_update_callback("Bình thường", "green")

        return False

    def reset_auto_restart_count(self):
        """Reset bộ đếm auto restart"""
        self.loop_detection['auto_restart_count'] = 0
        self.loop_detection['repeat_count'] = 0
        self.loop_detection['last_action'] = None
        
        # Cập nhật trạng thái
        if self.on_status_update_callback:
            self.on_status_update_callback("Đã reset", "green")
    
    def get_auto_restart_count(self) -> int:
        """Lấy số lần auto restart"""
        return self.loop_detection['auto_restart_count']
    
    def get_loop_status(self) -> Dict[str, Any]:
        """Lấy trạng thái hiện tại của loop detector"""
        return self.loop_detection.copy()