# -*- coding: utf-8 -*-
"""
Module automation core chứa logic tự động hóa chính
"""
import pyautogui
import time
import threading
from typing import Tuple, Optional, Callable
from components.image_detector import ImageDetector


class AutomationCore:
    """Class chứa logic automation chính"""
    
    def __init__(self):
        self.image_detector = ImageDetector()
        self.is_running = False
        self.auto_thread = None
        
        # Callbacks
        self.on_log_message: Optional[Callable] = None
        self.on_stats_update: Optional[Callable] = None
        self.on_step_update: Optional[Callable] = None
        self.on_loop_check: Optional[Callable] = None
    
    def set_log_callback(self, callback: Callable):
        """Thiết lập callback cho logging"""
        self.on_log_message = callback
    
    def set_stats_callback(self, callback: Callable):
        """Thiết lập callback cho cập nhật stats"""
        self.on_stats_update = callback
    
    def set_step_callback(self, callback: Callable):
        """Thiết lập callback cho cập nhật step"""
        self.on_step_update = callback
    
    def set_loop_check_callback(self, callback: Callable):
        """Thiết lập callback cho kiểm tra loop"""
        self.on_loop_check = callback
    
    def _log(self, message: str):
        """Helper method để log message"""
        if self.on_log_message:
            self.on_log_message(message)
        else:
            print(message)
    
    def start_automation(self):
        """Bắt đầu automation"""
        if self.is_running:
            return
        
        self.is_running = True
        self.auto_thread = threading.Thread(target=self.automation_loop, daemon=True)
        self.auto_thread.start()
        self._log("Bắt đầu automation")
    
    def stop_automation(self):
        """Dừng automation"""
        self.is_running = False
        self._log("Dừng automation")
    
    def click_center(self, bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """
        Click vào trung tâm của bounding box
        
        Args:
            bbox: Tuple (x, y, width, height)
            
        Returns:
            Tuple[int, int]: Tọa độ đã click (center_x, center_y)
        """
        x, y, w, h = bbox
        center_x, center_y = x + w//2, y + h//2
        pyautogui.click(center_x, center_y)
        return center_x, center_y
    
    def scroll_and_find_expand(self, last_expand_pos: Tuple[int, int], 
                              max_scrolls: int = 10) -> Optional[Tuple[int, int, int, int]]:
        """
        Scroll xuống tại vị trí expand cuối cùng để tìm expand button tiếp theo
        
        Args:
            last_expand_pos: Vị trí (x, y) của expand button cuối cùng được click
            max_scrolls: Số lần scroll tối đa
        
        Returns:
            Optional[Tuple[int, int, int, int]]: Vị trí expand button mới hoặc None
        """
        try:
            scroll_x, scroll_y = last_expand_pos
            scroll_count = 0
            
            self._log(f"Bắt đầu scroll tại vị trí ({scroll_x}, {scroll_y}) để tìm expand button tiếp theo")
            
            while scroll_count < max_scrolls:
                # Scroll xuống tại vị trí expand cuối cùng
                pyautogui.click(scroll_x, scroll_y)  # Click để focus
                time.sleep(0.5)
                pyautogui.scroll(-3, x=scroll_x, y=scroll_y)  # Scroll xuống 3 đơn vị
                time.sleep(1)  # Đợi scroll hoàn thành
                
                scroll_count += 1
                self._log(f"Scroll lần {scroll_count}/{max_scrolls}")
                
                # Kiểm tra có expand button mới không
                expand_btn = self.image_detector.detect_expand_button()
                if expand_btn:
                    self._log(f"Tìm thấy expand button mới sau {scroll_count} lần scroll")
                    return expand_btn
                    
            self._log(f"Không tìm thấy expand button sau {max_scrolls} lần scroll")
            return None
            
        except Exception as e:
            self._log(f"Lỗi khi scroll tìm expand: {str(e)}")
            return None
    
    def handle_no_lessons_scenario(self) -> bool:
        """
        Xử lý khi không tìm thấy lessons
        
        Returns:
            bool: True nếu tìm thấy lessons sau khi xử lý, False nếu không
        """
        self._log("Không tìm thấy lesson nào! Tìm kiếm Expand button...")
        
        # Tìm expand button khi không có lesson
        expand_btn = self.image_detector.detect_expand_button()
        if not expand_btn:
            self._log("Không tìm thấy Expand button!")
            return False
        
        # Click expand button đầu tiên
        center_x, center_y = self.click_center(expand_btn)
        self._log(f"Click Expand button tại ({center_x}, {center_y})")
        
        if self.on_stats_update:
            self.on_stats_update('expand_clicks')
        
        time.sleep(2)  # Đợi expand
        
        # Tìm lại lessons sau khi expand
        self._log("Tìm lại lessons sau khi expand...")
        lessons = self.image_detector.detect_all_lesson_images()
        
        if lessons:
            self._log(f"Tìm thấy {len(lessons)} lesson(s) sau khi expand!")
            return True
        
        # Nếu vẫn không có lessons, thử scroll để tìm expand tiếp theo
        self._log("Vẫn không tìm thấy lesson sau khi expand! Thử scroll để tìm expand button tiếp theo...")
        next_expand = self.scroll_and_find_expand((center_x, center_y), max_scrolls=10)
        
        if not next_expand:
            self._log("Không tìm thấy expand button tiếp theo sau khi scroll!")
            return False
        
        # Click expand button thứ 2
        center_x2, center_y2 = self.click_center(next_expand)
        self._log(f"Tìm thấy expand button tiếp theo, click tại ({center_x2}, {center_y2})")
        
        if self.on_stats_update:
            self.on_stats_update('expand_clicks')
        
        time.sleep(2)  # Đợi expand
        
        # Tìm lại lessons sau khi expand thứ 2
        self._log("Tìm lại lessons sau khi expand thứ 2...")
        lessons = self.image_detector.detect_all_lesson_images()
        
        if lessons:
            self._log(f"Tìm thấy {len(lessons)} lesson(s) sau khi expand và scroll!")
            return True
        else:
            self._log("Vẫn không tìm thấy lesson sau khi expand và scroll!")
            return False
    
    def handle_play_button_detected(self) -> bool:
        """
        Xử lý khi phát hiện play button (video đã kết thúc)
        
        Returns:
            bool: True nếu xử lý thành công, False nếu có lỗi
        """
        self._log("Phát hiện Play button - Video đã kết thúc!")
        
        if self.on_stats_update:
            self.on_stats_update('play_buttons_detected')
        
        # Tìm và click refresh button
        refresh_btn = self.image_detector.detect_refresh_button()
        if not refresh_btn:
            self._log("Không tìm thấy Refresh button!")
            return False
        
        center_x, center_y = self.click_center(refresh_btn)
        self._log(f"Click Refresh button tại ({center_x}, {center_y})")
        
        if self.on_stats_update:
            self.on_stats_update('refresh_clicks')
        
        time.sleep(3)  # Đợi trang refresh
        
        # Tìm lesson tiếp theo sau khi refresh
        self._log("Tìm lesson tiếp theo sau khi refresh...")
        lessons = self.image_detector.detect_all_lesson_images()
        
        if lessons:
            # Có lessons khả dụng, click vào lesson đầu tiên
            center_x, center_y = self.click_center(lessons[0])
            self._log(f"Click vào lesson đầu tiên tại ({center_x}, {center_y})")
            
            if self.on_stats_update:
                self.on_stats_update('lessons_clicked')
            
            time.sleep(2)
            return True
        else:
            # Không có lessons, xử lý expand scenario
            return self.handle_expand_scenario()
    
    def handle_expand_scenario(self) -> bool:
        """
        Xử lý khi cần expand để tìm lessons
        
        Returns:
            bool: True nếu tìm thấy lessons, False nếu không
        """
        self._log("Không tìm thấy lesson - Tìm expand button...")
        expand_btn = self.image_detector.detect_expand_button()
        
        if not expand_btn:
            self._log("Không tìm thấy expand button! Có thể đã hoàn thành tất cả.")
            return False
        
        center_x, center_y = self.click_center(expand_btn)
        self._log(f"Click Expand button tại ({center_x}, {center_y})")
        
        if self.on_stats_update:
            self.on_stats_update('expand_clicks')
        
        time.sleep(2)  # Đợi expand
        
        # Tìm lại lessons sau khi expand
        self._log("Tìm lại lessons sau khi expand...")
        lessons = self.image_detector.detect_all_lesson_images()
        
        if lessons:
            # Có lessons sau expand, click vào lesson đầu tiên
            center_x, center_y = self.click_center(lessons[0])
            self._log(f"Click vào lesson đầu tiên sau expand tại ({center_x}, {center_y})")
            
            if self.on_stats_update:
                self.on_stats_update('lessons_clicked')
            
            time.sleep(2)
            return True
        else:
            # Vẫn không có lessons, thử scroll để tìm expand tiếp theo
            self._log("Vẫn không có lesson - Scroll tìm expand tiếp theo...")
            next_expand = self.scroll_and_find_expand((center_x, center_y), max_scrolls=10)
            
            if not next_expand:
                self._log("Không tìm thấy expand button tiếp theo! Có thể đã hoàn thành tất cả.")
                return False
            
            center_x2, center_y2 = self.click_center(next_expand)
            self._log(f"Click expand button tiếp theo tại ({center_x2}, {center_y2})")
            
            if self.on_stats_update:
                self.on_stats_update('expand_clicks')
            
            time.sleep(2)
            
            # Tìm lessons sau expand thứ 2
            lessons = self.image_detector.detect_all_lesson_images()
            if lessons:
                center_x, center_y = self.click_center(lessons[0])
                self._log(f"Click lesson sau expand và scroll tại ({center_x}, {center_y})")
                
                if self.on_stats_update:
                    self.on_stats_update('lessons_clicked')
                
                time.sleep(2)
                return True
            else:
                self._log("Không tìm thấy lesson nào sau tất cả các bước! Có thể đã hoàn thành tất cả.")
                return False
    
    def automation_loop(self):
        """Vòng lặp automation chính"""
        try:
            if self.on_step_update:
                self.on_step_update("Khởi tạo", ["Tìm lessons", "Click lesson đầu tiên"])
            
            # Bước 1: Tìm và click vào lesson đầu tiên
            self._log("Tìm kiếm lessons...")
            lessons = self.image_detector.detect_all_lesson_images()
            
            if not lessons:
                if not self.handle_no_lessons_scenario():
                    self.stop_automation()
                    return
                # Tìm lại lessons sau khi xử lý
                lessons = self.image_detector.detect_all_lesson_images()
            
            if lessons:
                # Click vào lesson đầu tiên
                center_x, center_y = self.click_center(lessons[0])
                self._log(f"Click vào lesson đầu tiên tại ({center_x}, {center_y})")
                
                if self.on_stats_update:
                    self.on_stats_update('lessons_clicked')
                
                time.sleep(2)  # Đợi trang load
            
            # Bước 2: Vòng lặp kiểm tra play button mỗi phút
            while self.is_running:
                if self.on_step_update:
                    self.on_step_update("Kiểm tra video", ["Detect play button", "Chờ 60s"])
                
                self._log("Kiểm tra Play button...")
                
                # Kiểm tra loop detection
                if self.on_loop_check and self.on_loop_check("check_play_button"):
                    break  # Auto restart được kích hoạt
                
                play_btn = self.image_detector.detect_play_button()
                
                if play_btn:
                    if not self.handle_play_button_detected():
                        self._log("Có lỗi khi xử lý play button")
                        break
                else:
                    self._log("Không phát hiện Play button - Video vẫn đang chạy")
                
                # Đợi 1 phút trước khi kiểm tra lại
                self._log("Đợi 60 giây trước khi kiểm tra lại...")
                for i in range(60):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            self._log(f"Lỗi trong automation: {str(e)}")
            self.stop_automation()
    
    def test_detect(self):
        """Test các function detect"""
        self._log("=== Bắt đầu test detect ===")
        
        # Test detect lessons
        lessons = self.image_detector.detect_all_lesson_images()
        self._log(f"Tìm thấy {len(lessons)} lesson(s)")
        
        # Test detect play button
        play_btn = self.image_detector.detect_play_button()
        if play_btn:
            self._log("Tìm thấy Play button")
        else:
            self._log("Không tìm thấy Play button")
            
        # Test detect refresh button
        refresh_btn = self.image_detector.detect_refresh_button()
        if refresh_btn:
            self._log("Tìm thấy Refresh button")
        else:
            self._log("Không tìm thấy Refresh button")
              
        # Test detect expand button
        expand_btn = self.image_detector.detect_expand_button()
        if expand_btn:
            self._log("Tìm thấy Expand button")
        else:
            self._log("Không tìm thấy Expand button")
            
        self._log("=== Kết thúc test detect ===")
    
    def auto_restart(self):
        """Tự động restart automation"""
        try:
            self._log("🔄 Đang thực hiện auto restart...")
            if self.on_step_update:
                self.on_step_update("Auto restarting", ["Dừng automation", "Đợi 3 giây", "Bắt đầu lại"])
            
            # Dừng automation hiện tại
            self.is_running = False
            time.sleep(3)  # Đợi 3 giây
            
            # Bắt đầu lại nếu chưa được bắt đầu thủ công
            if not self.is_running:
                self.start_automation()
                
        except Exception as e:
            self._log(f"❌ Lỗi auto restart: {str(e)}")
