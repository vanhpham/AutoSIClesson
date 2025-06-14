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
    
    # ...existing code...
    
    def check_loop_detection(self, action: str) -> bool:
        """
        Kiểm tra và xử lý lặp vô hạn
        
        Args:
            action: Tên hành động đang thực hiện
            
        Returns:
            bool: True nếu cần auto restart, False nếu không
        """
        is_play_button_action = "play button" in action.lower()

        if self.loop_detection['last_action'] == action:
            self.loop_detection['repeat_count'] += 1
            
            if self.on_status_update_callback:
                status_color = "orange"
                status_message_suffix = ""
                if is_play_button_action:
                    status_color = "blue" # Màu khác để chỉ trạng thái lặp của play button
                    status_message_suffix = " (Play Button - Bỏ qua restart)"
                
                status = f"Lặp {self.loop_detection['repeat_count']}/{self.loop_detection['max_repeats']}{status_message_suffix}"
                self.on_status_update_callback(status, status_color)
            
            if self.loop_detection['repeat_count'] >= self.loop_detection['max_repeats']:
                if is_play_button_action:
                    # Đối với play button, không trigger restart.
                    # Log thông báo và trả về False.
                    print(f"⚠️  Phát hiện lặp '{action}' quá {self.loop_detection['max_repeats']} lần, nhưng bỏ qua restart vì là hành động liên quan đến Play Button.")
                    # Không reset repeat_count hoặc last_action ở đây để tiếp tục theo dõi nếu nó vẫn lặp,
                    # hoặc có thể reset nếu muốn bắt đầu đếm lại từ 1 cho play button.
                    # Ví dụ: self.loop_detection['repeat_count'] = 0 
                    return False 
                else:
                    # Logic restart cho các hành động khác không phải play button
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
                status_message = "Bình thường"
                if is_play_button_action:
                    status_message += " (Play Button)"
                self.on_status_update_callback(status_message, "green")
        
        return False
    # ...existing code...
    
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
