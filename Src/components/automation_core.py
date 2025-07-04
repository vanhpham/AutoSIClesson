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
    
    # Cấu hình tọa độ % có thể tùy chỉnh cho các thiết bị khác nhau
    SCROLL_X_PERCENT = 0.15  # 15% chiều rộng màn hình cho vị trí scroll
    SCROLL_Y_PERCENT = 0.50  # 50% chiều cao màn hình cho vị trí scroll
    
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
    
    def get_screen_position(self, x_percent: float, y_percent: float) -> Tuple[int, int]:
        """
        Tính toán tọa độ thực từ phần trăm màn hình
        
        Args:
            x_percent: Phần trăm chiều rộng màn hình (0.0 - 1.0)
            y_percent: Phần trăm chiều cao màn hình (0.0 - 1.0)
            
        Returns:
            Tuple[int, int]: Tọa độ thực (x, y)
        """
        screen_width, screen_height = pyautogui.size()
        x = int(screen_width * x_percent)
        y = int(screen_height * y_percent)
        return x, y
    
    def get_standard_scroll_position(self) -> Tuple[int, int]:
        """
        Lấy vị trí scroll chuẩn từ cấu hình % tọa độ
        
        Returns:
            Tuple[int, int]: Tọa độ để scroll
        """
        return self.get_screen_position(self.SCROLL_X_PERCENT, self.SCROLL_Y_PERCENT)
    
    def move_mouse_to_percent(self, x_percent: float, y_percent: float, duration: float = 0.2):
        """
        Di chuyển chuột đến vị trí phần trăm màn hình
        
        Args:
            x_percent: Phần trăm chiều rộng màn hình (0.0 - 1.0)
            y_percent: Phần trăm chiều cao màn hình (0.0 - 1.0)  
            duration: Thời gian di chuyển (giây)
        """
        x, y = self.get_screen_position(x_percent, y_percent)
        pyautogui.moveTo(x, y, duration=duration)
    
    def click_at_percent(self, x_percent: float, y_percent: float):
        """
        Click tại vị trí phần trăm màn hình
        
        Args:
            x_percent: Phần trăm chiều rộng màn hình (0.0 - 1.0)
            y_percent: Phần trăm chiều cao màn hình (0.0 - 1.0)
        """
        x, y = self.get_screen_position(x_percent, y_percent)
        pyautogui.click(x, y)
    
    def scroll_at_percent(self, x_percent: float, y_percent: float, scroll_amount: int = -200):
        """
        Scroll tại vị trí phần trăm màn hình
        
        Args:
            x_percent: Phần trăm chiều rộng màn hình (0.0 - 1.0)
            y_percent: Phần trăm chiều cao màn hình (0.0 - 1.0)
            scroll_amount: Số đơn vị scroll (âm = xuống, dương = lên)
        """
        x, y = self.get_screen_position(x_percent, y_percent)
        # Di chuyển chuột đến vị trí scroll
        pyautogui.moveTo(x, y)
        time.sleep(0.2)
        # Scroll tại vị trí đã định
        pyautogui.scroll(scroll_amount, x=x, y=y)

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
        
        # Đợi thread kết thúc hoặc force stop sau 3 giây
        if self.auto_thread and self.auto_thread.is_alive():
            self.auto_thread.join(timeout=3.0)
            if self.auto_thread.is_alive():
                self._log("Thread vẫn chạy - sẽ tự dừng khi có thể")
    
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
            # Sử dụng vị trí scroll chuẩn (15% X, 50% Y của màn hình)
            scroll_x, scroll_y = self.get_standard_scroll_position()
            
            scroll_count = 0
            
            self._log(f"Bắt đầu scroll tại vị trí ({scroll_x}, {scroll_y}) - 15% X, 50% Y màn hình để tìm expand button tiếp theo")
            
            while scroll_count < max_scrolls:
                # Di chuyển chuột đến vị trí scroll
                pyautogui.moveTo(scroll_x, scroll_y)
                
                time.sleep(0.5)
                
                # Scroll xuống tại vị trí đã định
                pyautogui.scroll(-200, x=scroll_x, y=scroll_y)  # Scroll xuống 200 đơn vị
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
    
    def handle_play_button_detected(self) -> list:
        """
        Xử lý khi phát hiện play button (video đã kết thúc)
        
        Returns:
            list: Danh sách lessons tìm được hoặc [] nếu không có
        """
        try:
            self._log("Phát hiện Play button - Video đã kết thúc!")
            
            if self.on_stats_update:
                self.on_stats_update('play_buttons_detected')
            
            # Kiểm tra xem có đang bị dừng không trước khi tiếp tục
            if not self.is_running:
                self._log("Automation đã bị dừng - không tìm lesson tiếp theo")
                return []

            self._log("Tìm lesson tiếp theo...")
            lessons = self.image_detector.detect_all_lesson_images()
            
            # Kiểm tra lại trước khi xử lý
            if not self.is_running:
                self._log("Automation đã bị dừng - không xử lý lesson")
                return []
            
            if lessons:
                self._log(f"Tìm thấy {len(lessons)} lesson(s) đang hiển thị")
                return lessons
            else:
                # Không có lessons đang hiển thị, tìm kiếm như bước khởi tạo
                self._log("Không tìm thấy lesson nào! Thực hiện tìm kiếm như bước khởi tạo...")
                return self.handle_no_lessons_scenario()
                
        except Exception as e:
            self._log(f"Lỗi khi xử lý play button: {str(e)}")
            return []
    
    def handle_no_lessons_scenario(self) -> list:
        """
        Xử lý khi không tìm thấy lessons
        
        Returns:
            list: Danh sách lessons tìm được sau khi xử lý, hoặc [] nếu không có
        """
        # Kiểm tra trạng thái trước khi bắt đầu
        if not self.is_running:
            return []
            
        self._log("Không tìm thấy lesson nào! Tìm kiếm Expand button...")
        
        # Tìm expand button khi không có lesson
        expand_btn = self.image_detector.detect_expand_button()
        if not expand_btn:
            self._log("Không tìm thấy Expand button! Thử scroll để tìm...")
            return self.scroll_and_find_lessons_or_expand()
        
        # Kiểm tra trước khi click
        if not self.is_running:
            return []
        
        # Click expand button đầu tiên
        center_x, center_y = self.click_center(expand_btn)
        self._log(f"Click Expand button tại ({center_x}, {center_y})")
        
        if self.on_stats_update:
            self.on_stats_update('expand_clicks')
        
        # Đợi expand với khả năng thoát sớm
        for i in range(20):  # 2 giây
            if not self.is_running:
                return []
            time.sleep(0.1)
        
        # Tìm lại lessons sau khi expand
        self._log("Tìm lại lessons sau khi expand...")
        lessons = self.image_detector.detect_all_lesson_images()
        
        if lessons:
            self._log(f"Tìm thấy {len(lessons)} lesson(s) sau khi expand!")
            return lessons
        
        # Nếu vẫn không có lessons, thử scroll để tìm expand tiếp theo
        self._log("Vẫn không tìm thấy lesson sau khi expand! Thử scroll để tìm expand button tiếp theo...")
        next_expand = self.scroll_and_find_expand((center_x, center_y), max_scrolls=10)
        
        if not next_expand:
            self._log("Không tìm thấy expand button tiếp theo! Thử scroll liên tục để tìm lesson...")
            return self.scroll_and_find_lessons_or_expand((center_x, center_y))
        
        # Kiểm tra trước khi click expand thứ 2
        if not self.is_running:
            return []
        
        # Click expand button thứ 2
        center_x2, center_y2 = self.click_center(next_expand)
        self._log(f"Tìm thấy expand button tiếp theo, click tại ({center_x2}, {center_y2})")
        
        if self.on_stats_update:
            self.on_stats_update('expand_clicks')
        
        # Đợi expand thứ 2
        for i in range(20):  # 2 giây
            if not self.is_running:
                return []
            time.sleep(0.1)
        
        # Tìm lại lessons sau khi expand thứ 2
        self._log("Tìm lại lessons sau khi expand thứ 2...")
        lessons = self.image_detector.detect_all_lesson_images()
        
        if lessons:
            self._log(f"Tìm thấy {len(lessons)} lesson(s) sau khi expand và scroll!")
            return lessons
        else:
            self._log("Vẫn không tìm thấy lesson sau khi expand! Thử scroll liên tục để tìm...")
            return self.scroll_and_find_lessons_or_expand((center_x2, center_y2))
    
    def handle_expand_scenario(self) -> list:
        """
        Xử lý khi cần expand để tìm lessons
        
        Returns:
            list: Danh sách lessons tìm được sau khi xử lý, hoặc [] nếu không có
        """
        # Kiểm tra trạng thái trước khi bắt đầu
        if not self.is_running:
            return []
            
        self._log("Không tìm thấy lesson - Tìm expand button...")
        expand_btn = self.image_detector.detect_expand_button()
        
        if not expand_btn:
            # Không tìm thấy expand button, thử scroll để tìm
            self._log("Không tìm thấy expand button! Thử scroll xuống để tìm...")
            return self.scroll_and_find_lessons_or_expand()
        
        # Kiểm tra trước khi click
        if not self.is_running:
            return []
            
        center_x, center_y = self.click_center(expand_btn)
        self._log(f"Click Expand button tại ({center_x}, {center_y})")
        
        if self.on_stats_update:
            self.on_stats_update('expand_clicks')
        
        # Đợi expand với khả năng thoát sớm
        for i in range(20):  # 2 giây
            if not self.is_running:
                return []
            time.sleep(0.1)
        
        # Tìm lại lessons sau khi expand
        self._log("Tìm lại lessons sau khi expand...")
        lessons = self.image_detector.detect_all_lesson_images()
        
        if lessons:
            return lessons
        self._log("Vẫn không có lesson - Scroll tìm expand tiếp theo...")
        next_expand = self.scroll_and_find_expand((center_x, center_y), max_scrolls=10)
        
        if not next_expand:
            # Không tìm thấy expand button, thử scroll tìm lesson trực tiếp
            self._log("Không tìm thấy expand button tiếp theo! Thử scroll tìm lesson trực tiếp...")
            return self.scroll_and_find_lessons_or_expand((center_x, center_y))
        
        # Kiểm tra trước khi click expand thứ 2
        if not self.is_running:
            return []
            
        center_x2, center_y2 = self.click_center(next_expand)
        self._log(f"Click expand button tiếp theo tại ({center_x2}, {center_y2})")
        
        if self.on_stats_update:
            self.on_stats_update('expand_clicks')
        
        # Đợi expand thứ 2
        for i in range(20):  # 2 giây
            if not self.is_running:
                return []
            time.sleep(0.1)
        
        # Tìm lessons sau expand thứ 2
        lessons = self.image_detector.detect_all_lesson_images()
        if lessons:
            return lessons
        else:
            self._log("Vẫn không tìm thấy lesson sau expand! Thử scroll liên tục để tìm...")
            return self.scroll_and_find_lessons_or_expand((center_x2, center_y2))
    
    def automation_loop(self):
        """Vòng lặp automation chính"""
        try:
            if self.on_step_update:
                self.on_step_update("Khởi tạo", ["Tìm lessons", "Click lesson đầu tiên"])
              # Bước 1: Tìm và click vào lesson đầu tiên
            self._log("Tìm kiếm lessons...")
            lessons = self.image_detector.detect_all_lesson_images()
            
            # Kiểm tra dừng trước khi xử lý lessons
            if not self.is_running:
                return
            
            if not lessons:
                lessons = self.handle_no_lessons_scenario()
            
            # Kiểm tra dừng trước khi click lesson
            if not self.is_running:
                return
                
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
                
                # Kiểm tra dừng trước khi detect
                if not self.is_running:
                    return
                
                # Kiểm tra loop detection
                if self.on_loop_check and self.on_loop_check("check_play_button"):
                    break  # Auto restart được kích hoạt
                
                play_btn = self.image_detector.detect_play_button()
                  # Kiểm tra dừng sau khi detect
                if not self.is_running:
                    return
                
                if play_btn:
                    lessons = self.handle_play_button_detected()
                    if lessons:
                        center_x, center_y = self.click_center(lessons[0])
                        self._log(f"Click vào lesson đầu tiên tại ({center_x}, {center_y})")
                        
                        if self.on_stats_update:
                            self.on_stats_update('lessons_clicked')
                        
                        # Thêm delay ngắn để tránh click liên tiếp
                        for i in range(20):  # 2 seconds delay với khả năng thoát sớm
                            if not self.is_running:
                                return
                            time.sleep(0.1)
                    else:
                        self._log("Có lỗi khi xử lý play button hoặc không tìm thấy lesson mới")
                        break
                else:
                    self._log("Không phát hiện Play button - Video vẫn đang chạy")
                  # Đợi 1 phút trước khi kiểm tra lại - với khả năng dừng ngay lập tức
                self._log("Đợi 60 giây trước khi kiểm tra lại...")
                for i in range(600):  # 60 giây = 600 lần 0.1 giây
                    if not self.is_running:
                        self._log("Dừng automation được yêu cầu")
                        return  # Thoát ngay lập tức
                    time.sleep(0.1)  # Sleep ngắn để có thể phản hồi nhanh
                    
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
    
    def scroll_and_find_lessons_or_expand(self, scroll_pos: Optional[Tuple[int, int]] = None, 
                                          max_scrolls: int = 20) -> list:
        """
        Scroll xuống liên tục để tìm lessons hoặc expand button mới
        
        Args:
            scroll_pos: Vị trí (x, y) để scroll, nếu None sẽ scroll ở giữa màn hình
            max_scrolls: Số lần scroll tối đa
        
        Returns:
            list: Danh sách lessons tìm được hoặc [] nếu không có
        """
        try:            # Kiểm tra trạng thái trước khi bắt đầu
            if not self.is_running:
                return []
                
            # Sử dụng vị trí scroll chuẩn (15% X, 50% Y của màn hình)
            scroll_x, scroll_y = self.get_standard_scroll_position()
            
            scroll_count = 0
            self._log(f"Bắt đầu scroll liên tục tại vị trí ({scroll_x}, {scroll_y}) - 15% X, 50% Y màn hình để tìm lesson hoặc expand button")
            
            while scroll_count < max_scrolls and self.is_running:
                # Di chuyển chuột đến vị trí scroll
                pyautogui.moveTo(scroll_x, scroll_y)
                
                # Đợi với khả năng thoát sớm
                for i in range(5):  # 0.5 giây
                    if not self.is_running:
                        return []
                    time.sleep(0.1)
                
                # Scroll xuống tại vị trí đã định
                pyautogui.scroll(-200, x=scroll_x, y=scroll_y)  # Scroll xuống 200 đơn vị
                
                # Đợi scroll hoàn thành với khả năng thoát sớm
                for i in range(10):  # 1 giây
                    if not self.is_running:
                        return []
                    time.sleep(0.1)
                
                scroll_count += 1
                self._log(f"Scroll lần {scroll_count}/{max_scrolls}")
                
                # Kiểm tra có lessons không
                lessons = self.image_detector.detect_all_lesson_images()
                if lessons and self.is_running:
                    self._log(f"Tìm thấy {len(lessons)} lesson(s) sau {scroll_count} lần scroll")
                    return lessons
                
                # Kiểm tra có expand button mới không
                expand_btn = self.image_detector.detect_expand_button()
                if expand_btn and self.is_running:
                    self._log(f"Tìm thấy expand button mới sau {scroll_count} lần scroll")
                    center_x, center_y = self.click_center(expand_btn)
                    self._log(f"Click Expand button tại ({center_x}, {center_y})")
                    if self.on_stats_update:
                        self.on_stats_update('expand_clicks')
                    for i in range(20):
                        if not self.is_running:
                            return []
                        time.sleep(0.1)
                    lessons = self.image_detector.detect_all_lesson_images()
                    if lessons and self.is_running:
                        self._log(f"Click lesson sau expand tại ({center_x}, {center_y})")
                        return lessons
                    else:
                        self._log("Không tìm thấy lesson sau expand, tiếp tục scroll tại vị trí chuẩn...")
                        continue
            self._log(f"Không tìm thấy lesson hoặc expand button sau {max_scrolls} lần scroll")
            return []
        except Exception as e:
            self._log(f"Lỗi khi scroll tìm lesson/expand: {str(e)}")
            return []

    def scroll_at_position(self, scroll_x: int, scroll_y: int, scroll_amount: int = -200):
        """
        Scroll tại vị trí cụ thể với chuẩn bị di chuyển chuột trước
        
        Args:
            scroll_x: Tọa độ X để scroll
            scroll_y: Tọa độ Y để scroll  
            scroll_amount: Số đơn vị scroll (âm = xuống, dương = lên)
        """
        # Di chuyển chuột đến vị trí scroll
        pyautogui.moveTo(scroll_x, scroll_y)
        time.sleep(0.2)  # Đợi di chuyển chuột
        
        # Click để focus
        time.sleep(0.3)
        
        # Scroll tại vị trí đã định
        pyautogui.scroll(scroll_amount, x=scroll_x, y=scroll_y)
    
    def configure_scroll_position(self, x_percent: float = 0.15, y_percent: float = 0.50):
        """
        Cấu hình lại vị trí scroll % cho thiết bị cụ thể
        
        Args:
            x_percent: Phần trăm chiều rộng màn hình (0.0 - 1.0), mặc định 0.15 (15%)
            y_percent: Phần trăm chiều cao màn hình (0.0 - 1.0), mặc định 0.50 (50%)
        """
        self.SCROLL_X_PERCENT = x_percent
        self.SCROLL_Y_PERCENT = y_percent
        self._log(f"Cấu hình vị trí scroll: {x_percent*100:.1f}% X, {y_percent*100:.1f}% Y")
    
    def get_screen_info(self) -> dict:
        """
        Lấy thông tin màn hình hiện tại
        
        Returns:
            dict: Thông tin chi tiết về màn hình và vị trí scroll
        """
        screen_width, screen_height = pyautogui.size()
        scroll_x, scroll_y = self.get_standard_scroll_position()
        
        return {
            'screen_width': screen_width,
            'screen_height': screen_height,
            'scroll_x_percent': self.SCROLL_X_PERCENT,
            'scroll_y_percent': self.SCROLL_Y_PERCENT,
            'scroll_x_actual': scroll_x,
            'scroll_y_actual': scroll_y,
            'resolution': f"{screen_width}x{screen_height}"
        }
    
    def log_screen_info(self):
        """Log thông tin màn hình hiện tại"""
        info = self.get_screen_info()
        self._log(f"Thông tin màn hình: {info['resolution']}")
        self._log(f"Vị trí scroll: ({info['scroll_x_actual']}, {info['scroll_y_actual']}) = {info['scroll_x_percent']*100:.1f}%, {info['scroll_y_percent']*100:.1f}%")
