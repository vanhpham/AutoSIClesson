# -*- coding: utf-8 -*-
"""
Module quản lý thống kê của ứng dụng
"""
import time
from typing import Dict, Any


class StatsManager:
    """Class quản lý thống kê hoạt động"""
    
    def __init__(self):
        self.stats = {
            'lessons_clicked': 0,
            'play_buttons_detected': 0,
            'refresh_clicks': 0,
            'expand_clicks': 0,
            'start_time': None
        }
    
    def reset_stats(self):
        """Reset tất cả thống kê"""
        self.stats = {
            'lessons_clicked': 0,
            'play_buttons_detected': 0,
            'refresh_clicks': 0,
            'expand_clicks': 0,
            'start_time': None
        }
    
    def start_timer(self):
        """Bắt đầu đếm thời gian"""
        self.stats['start_time'] = time.time()
    
    def get_runtime(self) -> str:
        """
        Lấy thời gian chạy dưới dạng string HH:MM:SS
        
        Returns:
            str: Thời gian chạy định dạng HH:MM:SS
        """
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"
    
    def increment_lessons_clicked(self):
        """Tăng số lượng lessons đã click"""
        self.stats['lessons_clicked'] += 1
    
    def increment_play_buttons_detected(self):
        """Tăng số lượng play buttons đã phát hiện"""
        self.stats['play_buttons_detected'] += 1
    
    def increment_refresh_clicks(self):
        """Tăng số lượng refresh clicks"""
        self.stats['refresh_clicks'] += 1
    
    def increment_expand_clicks(self):
        """Tăng số lượng expand clicks"""
        self.stats['expand_clicks'] += 1
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        Lấy tất cả thống kê
        
        Returns:
            Dict chứa tất cả thống kê
        """
        return self.stats.copy()
    
    def get_stats_summary(self) -> str:
        """
        Lấy tóm tắt thống kê dưới dạng string
        
        Returns:
            str: Tóm tắt thống kê
        """
        runtime = self.get_runtime()
        return (f"Lessons: {self.stats['lessons_clicked']}, "
                f"Videos: {self.stats['play_buttons_detected']}, "
                f"Expands: {self.stats['expand_clicks']}, "
                f"Runtime: {runtime}")
