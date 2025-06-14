# -*- coding: utf-8 -*-
"""
Module quản lý assets (hình ảnh template) cho ứng dụng AutoSIC
"""
import os
import cv2
import numpy as np
import pyautogui
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class AssetInfo:
    """Thông tin về một asset"""
    name: str
    file_path: str
    description: str
    template: Optional[np.ndarray] = None
    is_loaded: bool = False
    file_size: int = 0
    dimensions: Tuple[int, int] = (0, 0)


class AssetManager:
    """Class quản lý tất cả assets cần thiết cho phần mềm"""
    
    def __init__(self, assets_path: str = "Assets"):
        self.assets_path = assets_path
        self.assets: Dict[str, AssetInfo] = {}
        
        # Định nghĩa các assets cần thiết
        self._define_required_assets()
        
        # Load tất cả assets
        self.load_all_assets()
    
    def _define_required_assets(self):
        """Định nghĩa tất cả assets cần thiết cho ứng dụng"""
        required_assets = {
            "lesson_unfinish": {
                "file_name": "Lesson_unfinish_image.png",
                "description": "Hình ảnh lesson chưa hoàn thành - dùng để detect lessons có thể click"
            },
            "play_button": {
                "file_name": "Play_button.png",
                "description": "Nút play video - dùng để detect khi video kết thúc"
            },
            "refresh_button": {
                "file_name": "Refresh_page.png",
                "description": "Nút refresh trang - dùng để reload trang sau khi hoàn thành video"
            },
            "expand_button": {
                "file_name": "Expand.png",
                "description": "Nút expand section - dùng để mở rộng các section có lessons"
            }
        }
        
        for asset_key, asset_data in required_assets.items():
            file_path = os.path.join(self.assets_path, asset_data["file_name"])
            self.assets[asset_key] = AssetInfo(
                name=asset_key,
                file_path=file_path,
                description=asset_data["description"]
            )
    
    def load_all_assets(self) -> bool:
        """
        Load tất cả assets
        
        Returns:
            bool: True nếu load thành công tất cả, False nếu có lỗi
        """
        all_loaded = True
        
        for asset_key, asset_info in self.assets.items():
            if not self.load_asset(asset_key):
                all_loaded = False
        
        return all_loaded
    
    def load_asset(self, asset_key: str) -> bool:
        """
        Load một asset cụ thể
        
        Args:
            asset_key: Key của asset cần load
            
        Returns:
            bool: True nếu load thành công, False nếu có lỗi
        """
        if asset_key not in self.assets:
            print(f"❌ Asset key '{asset_key}' không tồn tại")
            return False
        
        asset_info = self.assets[asset_key]
        
        try:
            # Kiểm tra file tồn tại
            if not os.path.exists(asset_info.file_path):
                print(f"❌ Không tìm thấy file: {asset_info.file_path}")
                asset_info.is_loaded = False
                return False
            
            # Lấy thông tin file
            asset_info.file_size = os.path.getsize(asset_info.file_path)
            
            # Load template
            template = cv2.imread(asset_info.file_path)
            if template is None:
                print(f"❌ Không thể đọc file: {asset_info.file_path}")
                asset_info.is_loaded = False
                return False
            
            # Lưu template và thông tin
            asset_info.template = template
            asset_info.dimensions = (template.shape[1], template.shape[0])  # (width, height)
            asset_info.is_loaded = True
            
            print(f"✅ Đã load asset '{asset_key}': {asset_info.dimensions[0]}x{asset_info.dimensions[1]}px, {asset_info.file_size} bytes")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi load asset '{asset_key}': {str(e)}")
            asset_info.is_loaded = False
            return False
    
    def get_asset_template(self, asset_key: str) -> Optional[np.ndarray]:
        """
        Lấy template của asset
        
        Args:
            asset_key: Key của asset
            
        Returns:
            Template image hoặc None nếu không load được
        """
        if asset_key not in self.assets:
            print(f"❌ Asset key '{asset_key}' không tồn tại")
            return None
        
        asset_info = self.assets[asset_key]
        
        if not asset_info.is_loaded:
            print(f"⚠️ Asset '{asset_key}' chưa được load, thử load lại...")
            if not self.load_asset(asset_key):
                return None
        
        return asset_info.template
    
    def get_asset_info(self, asset_key: str) -> Optional[AssetInfo]:
        """
        Lấy thông tin của asset
        
        Args:
            asset_key: Key của asset
            
        Returns:
            AssetInfo hoặc None nếu không tồn tại
        """
        return self.assets.get(asset_key)
    
    def get_all_assets_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Lấy thông tin của tất cả assets
        
        Returns:
            Dictionary chứa thông tin chi tiết của tất cả assets
        """
        assets_info = {}
        
        for asset_key, asset_info in self.assets.items():
            assets_info[asset_key] = {
                'file_path': asset_info.file_path,
                'description': asset_info.description,
                'loaded': asset_info.is_loaded,
                'file_size': asset_info.file_size,
                'width': asset_info.dimensions[0] if asset_info.dimensions else 0,
                'height': asset_info.dimensions[1] if asset_info.dimensions else 0
            }
        
        return assets_info
    
    def reload_asset(self, asset_key: str) -> bool:
        """
        Reload một asset cụ thể
        
        Args:
            asset_key: Key của asset cần reload
            
        Returns:
            bool: True nếu reload thành công
        """
        if asset_key not in self.assets:
            return False
        
        asset_info = self.assets[asset_key]
        
        try:
            # Load lại template
            if os.path.exists(asset_info.file_path):
                template = cv2.imread(asset_info.file_path)
                if template is not None:
                    asset_info.template = template
                    asset_info.is_loaded = True
                    
                    # Cập nhật thông tin file
                    asset_info.file_size = os.path.getsize(asset_info.file_path)
                    asset_info.dimensions = (template.shape[1], template.shape[0])
                    
                    print(f"✅ Đã reload asset '{asset_key}' thành công")
                    return True
                else:
                    asset_info.is_loaded = False
                    print(f"❌ Không thể đọc file hình ảnh: {asset_info.file_path}")
                    return False
            else:
                asset_info.is_loaded = False
                print(f"❌ File không tồn tại: {asset_info.file_path}")
                return False
                
        except Exception as e:
            asset_info.is_loaded = False
            print(f"❌ Lỗi khi reload asset '{asset_key}': {str(e)}")
            return False
    
    def reload_all_assets(self) -> bool:
        """
        Reload tất cả assets
        
        Returns:
            bool: True nếu reload thành công tất cả
        """
        print("🔄 Đang reload tất cả assets...")
        
        # Reset trạng thái
        for asset_info in self.assets.values():
            asset_info.is_loaded = False
            asset_info.template = None
        
        return self.load_all_assets()
    
    def validate_assets(self) -> Dict[str, bool]:
        """
        Kiểm tra tình trạng tất cả assets
        
        Returns:
            Dictionary với trạng thái validate của từng asset
        """
        validation_results = {}
        
        for asset_key, asset_info in self.assets.items():
            is_valid = (
                os.path.exists(asset_info.file_path) and
                asset_info.is_loaded and
                asset_info.template is not None
            )
            validation_results[asset_key] = is_valid
        
        return validation_results
    
    def get_assets_summary(self) -> str:
        """
        Lấy tóm tắt trạng thái assets
        
        Returns:
            String tóm tắt trạng thái
        """
        total_assets = len(self.assets)
        loaded_assets = sum(1 for asset in self.assets.values() if asset.is_loaded)
        total_size = sum(asset.file_size for asset in self.assets.values() if asset.is_loaded)
        
        return f"Assets: {loaded_assets}/{total_assets} loaded, Total size: {total_size} bytes"
    
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
    
    def test_detect_asset(self, asset_key: str, threshold: float = 0.8) -> Dict[str, Any]:
        """
        Test detect một asset cụ thể trên màn hình hiện tại
        
        Args:
            asset_key: Key của asset cần test
            threshold: Ngưỡng để xác định match
            
        Returns:
            Dictionary chứa kết quả test
        """
        result = {
            "asset_key": asset_key,
            "success": False,
            "matches_found": 0,
            "matches": [],
            "error": None,
            "threshold_used": threshold
        }
        
        try:
            # Lấy template
            template = self.get_asset_template(asset_key)
            if template is None:
                result["error"] = f"Không thể load template cho asset '{asset_key}'"
                return result
            
            # Chụp màn hình
            screenshot_cv = self._get_screenshot()
            
            # Lấy kích thước template
            template_height, template_width = template.shape[:2]
            
            # Thực hiện template matching
            match_result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            
            # Tìm tất cả matches
            locations = np.where(match_result >= threshold)
            
            # Chuyển đổi thành danh sách matches
            matches = []
            for pt in zip(*locations[::-1]):  # locations trả về (y, x), ta cần (x, y)
                x, y = pt
                matches.append((x, y, template_width, template_height))
            
            # Lọc duplicates
            filtered_matches = self._filter_duplicate_matches(matches)
            
            # Sắp xếp theo tọa độ y (từ trên xuống dưới)
            filtered_matches.sort(key=lambda match: match[1])
            
            result["success"] = True
            result["matches_found"] = len(filtered_matches)
            result["matches"] = filtered_matches
            
        except Exception as e:
            result["error"] = f"Lỗi khi test detect: {str(e)}"
        
        return result
    
    def test_detect_all_assets(self, threshold: float = 0.8) -> Dict[str, Dict[str, Any]]:
        """
        Test detect tất cả assets trên màn hình hiện tại
        
        Args:
            threshold: Ngưỡng để xác định match
            
        Returns:
            Dictionary chứa kết quả test cho tất cả assets
        """
        print(f"🔍 Bắt đầu test detect tất cả assets với threshold = {threshold}")
        print("=" * 60)
        
        results = {}
        
        for asset_key in self.assets.keys():
            print(f"\n🎯 Test detect asset: {asset_key}")
            asset_info = self.assets[asset_key]
            print(f"   📝 Mô tả: {asset_info.description}")
            
            result = self.test_detect_asset(asset_key, threshold)
            results[asset_key] = result
            
            if result["success"]:
                matches_count = result["matches_found"]
                if matches_count > 0:
                    print(f"   ✅ Tìm thấy {matches_count} match(s)")
                    for i, (x, y, w, h) in enumerate(result["matches"][:3]):  # Hiển thị tối đa 3 matches đầu tiên
                        print(f"      - Match {i+1}: x={x}, y={y}, w={w}, h={h}")
                    if matches_count > 3:
                        print(f"      - ... và {matches_count - 3} match(s) khác")
                else:
                    print(f"   ⚠️ Không tìm thấy match nào")
            else:
                print(f"   ❌ Lỗi: {result['error']}")
        
        print("\n" + "=" * 60)
        self._print_test_summary(results)
        
        return results
    
    def _print_test_summary(self, results: Dict[str, Dict[str, Any]]):
        """
        In tóm tắt kết quả test
        
        Args:
            results: Kết quả test từ test_detect_all_assets
        """
        print("📊 TÓM TẮT KẾT QUẢ TEST DETECT:")
        print("-" * 40)
        
        total_assets = len(results)
        successful_tests = sum(1 for r in results.values() if r["success"])
        assets_found = sum(1 for r in results.values() if r["success"] and r["matches_found"] > 0)
        total_matches = sum(r["matches_found"] for r in results.values() if r["success"])
        
        print(f"📈 Tổng số assets: {total_assets}")
        print(f"✅ Test thành công: {successful_tests}/{total_assets}")
        print(f"🎯 Assets tìm thấy trên màn hình: {assets_found}/{total_assets}")
        print(f"🔍 Tổng số matches: {total_matches}")
        
        print(f"\n📋 Chi tiết từng asset:")
        for asset_key, result in results.items():
            status_icon = "✅" if result["success"] and result["matches_found"] > 0 else "⚠️" if result["success"] else "❌"
            matches_text = f"({result['matches_found']} matches)" if result["success"] else "(error)"
            print(f"   {status_icon} {asset_key}: {matches_text}")
        
        if assets_found == 0:
            print(f"\n💡 GỢI Ý:")
            print(f"   - Đảm bảo ứng dụng target đang mở và hiển thị đúng màn hình")
            print(f"   - Kiểm tra độ phân giải màn hình có khớp với assets không")
            print(f"   - Thử giảm threshold nếu cần (hiện tại: {results[list(results.keys())[0]]['threshold_used']})")
    
    def get_detection_stats(self) -> Dict[str, int]:
        """
        Lấy thống kê detection cho tất cả assets
        
        Returns:
            Dictionary chứa thống kê
        """
        stats = {}
        results = self.test_detect_all_assets()
        
        for asset_key, result in results.items():
            stats[asset_key] = result["matches_found"] if result["success"] else 0
        
        return stats
