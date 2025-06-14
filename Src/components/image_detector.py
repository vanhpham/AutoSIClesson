# -*- coding: utf-8 -*-
"""
Module phát hiện hình ảnh sử dụng template matching
"""
import pyautogui
import cv2
import numpy as np
import os
from typing import List, Tuple, Optional


class ImageDetector:
    """Class chứa các hàm detect hình ảnh trên màn hình"""
    
    def __init__(self, assets_path: str = "Assets"):
        self.assets_path = assets_path
    
    def _load_template(self, template_name: str) -> Optional[np.ndarray]:
        """
        Load template image
        
        Args:
            template_name: Tên file template
            
        Returns:
            Template image hoặc None nếu không load được
        """
        template_path = os.path.join(self.assets_path, template_name)
        
        if not os.path.exists(template_path):
            print(f"Không tìm thấy file template: {template_path}")
            return None
        
        template = cv2.imread(template_path)
        if template is None:
            print(f"Không thể đọc file template: {template_path}")
            return None
            
        return template
    
    def _get_screenshot(self) -> np.ndarray:
        """
        Chụp màn hình và chuyển đổi format cho OpenCV
        
        Returns:
            Screenshot dưới dạng OpenCV format
        """
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        return screenshot_cv
    
    def _filter_duplicate_matches(self, matches: List[Tuple[int, int, int, int]], 
                                 distance_threshold: int = 10) -> List[Tuple[int, int, int, int]]:
        """
        Loại bỏ các matches trùng lặp (gần nhau)
        
        Args:
            matches: Danh sách các matches
            distance_threshold: Ngưỡng khoảng cách để coi là trùng lặp
            
        Returns:
            Danh sách matches đã lọc
        """
        filtered_matches = []
        
        for match in matches:
            x, y, w, h = match
            is_duplicate = False
            
            for existing_match in filtered_matches:
                ex_x, ex_y, ex_w, ex_h = existing_match
                # Kiểm tra nếu matches gần nhau
                if abs(x - ex_x) < distance_threshold and abs(y - ex_y) < distance_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered_matches.append(match)
        
        return filtered_matches
    
    def detect_all_lesson_images(self) -> List[Tuple[int, int, int, int]]:
        """
        Detect tất cả các vị trí khớp với hình ảnh Lesson_image.png trên màn hình
        
        Returns:
            List[Tuple[int, int, int, int]]: Danh sách các vị trí (x, y, width, height) 
            được sắp xếp từ trên xuống dưới theo tọa độ y
        """
        try:
            template = self._load_template("Lesson_unfinish_image.png")
            if template is None:
                return []
            
            screenshot_cv = self._get_screenshot()
            
            # Lấy kích thước template
            template_height, template_width = template.shape[:2]
            
            # Thực hiện template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Đặt ngưỡng để xác định match
            threshold = 0.99
            locations = np.where(result >= threshold)
            
            # Chuyển đổi locations thành danh sách các hộp giới hạn
            matches = []
            for pt in zip(*locations[::-1]):  # locations trả về (y, x), ta cần (x, y)
                x, y = pt
                matches.append((x, y, template_width, template_height))
            
            # Loại bỏ các matches trùng lặp
            filtered_matches = self._filter_duplicate_matches(matches)
            
            # Sắp xếp theo tọa độ y (từ trên xuống dưới)
            filtered_matches.sort(key=lambda match: match[1])
            
            print(f"Tìm thấy {len(filtered_matches)} vị trí khớp với hình ảnh lesson")
            for i, (x, y, w, h) in enumerate(filtered_matches):
                print(f"Vị trí {i+1}: x={x}, y={y}, width={w}, height={h}")
            
            return filtered_matches
            
        except Exception as e:
            print(f"Lỗi khi detect lesson images: {str(e)}")
            return []
    
    def detect_play_button(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect vị trí của Play_button.png trên màn hình (chỉ có 1 nút duy nhất)
        
        Returns:
            Optional[Tuple[int, int, int, int]]: Vị trí (x, y, width, height) hoặc None nếu không tìm thấy
        """
        try:
            template = self._load_template("Play_button.png")
            if template is None:
                return None
            
            screenshot_cv = self._get_screenshot()
            
            # Lấy kích thước template
            template_height, template_width = template.shape[:2]
            
            # Thực hiện template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Tìm vị trí có độ khớp cao nhất
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Kiểm tra ngưỡng để xác định match
            threshold = 0.8
            if max_val >= threshold:
                x, y = max_loc
                print(f"Tìm thấy Play button tại: x={x}, y={y}, width={template_width}, height={template_height}")
                return (x, y, template_width, template_height)
            else:
                print("Không tìm thấy Play button trên màn hình")
                return None
            
        except Exception as e:
            print(f"Lỗi khi detect Play button: {str(e)}")
            return None
    
    def detect_refresh_button(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect vị trí của Refresh_page.png trên màn hình
        
        Returns:
            Optional[Tuple[int, int, int, int]]: Vị trí (x, y, width, height) hoặc None nếu không tìm thấy
        """
        try:
            template = self._load_template("Refresh_page.png")
            if template is None:
                return None
            
            screenshot_cv = self._get_screenshot()
            
            # Lấy kích thước template
            template_height, template_width = template.shape[:2]
            
            # Thực hiện template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Tìm vị trí có độ khớp cao nhất
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Kiểm tra ngưỡng để xác định match
            threshold = 0.8
            if max_val >= threshold:
                x, y = max_loc
                print(f"Tìm thấy Refresh button tại: x={x}, y={y}, width={template_width}, height={template_height}")
                return (x, y, template_width, template_height)
            else:
                print("Không tìm thấy Refresh button trên màn hình")
                return None
            
        except Exception as e:
            print(f"Lỗi khi detect Refresh button: {str(e)}")
            return None
    
    def detect_expand_button(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect vị trí của Expand.png trên màn hình và trả về expand button đầu tiên từ trên xuống dưới
        
        Returns:
            Optional[Tuple[int, int, int, int]]: Vị trí (x, y, width, height) hoặc None nếu không tìm thấy
        """
        try:
            template = self._load_template("Expand.png")
            if template is None:
                return None
            
            screenshot_cv = self._get_screenshot()
            
            # Lấy kích thước template
            template_height, template_width = template.shape[:2]
            
            # Thực hiện template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Đặt ngưỡng để xác định match
            threshold = 0.8
            locations = np.where(result >= threshold)
            
            # Chuyển đổi locations thành danh sách các hộp giới hạn
            matches = []
            for pt in zip(*locations[::-1]):  # locations trả về (y, x), ta cần (x, y)
                x, y = pt
                matches.append((x, y, template_width, template_height))
            
            if not matches:
                print("Không tìm thấy Expand button trên màn hình")
                return None
            
            # Loại bỏ các matches trùng lặp
            filtered_matches = self._filter_duplicate_matches(matches)
            
            # Sắp xếp theo tọa độ y (từ trên xuống dưới)
            filtered_matches.sort(key=lambda match: match[1])
            
            # Trả về expand button đầu tiên
            first_expand = filtered_matches[0]
            x, y, w, h = first_expand
            print(f"Tìm thấy {len(filtered_matches)} Expand button(s), chọn đầu tiên tại: x={x}, y={y}, width={w}, height={h}")
            
            return first_expand
            
        except Exception as e:
            print(f"Lỗi khi detect Expand button: {str(e)}")
            return None
