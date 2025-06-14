# AutoSIC - Cấu trúc mới

## Tổng quan
Phần mềm AutoSIC đã được tái cấu trúc thành nhiều module nhỏ để dễ quản lý và bảo trì hơn.

## Cấu trúc file

```
AutoSIC/
├── Assets/                     # Thư mục chứa hình ảnh template
│   ├── Expand.png
│   ├── Lesson_unfinish_image.png
│   ├── Play_button.png
│   └── Refresh_page.png
├── Src/                        # Thư mục source code
│   ├── __init__.py            # Package initialization
│   ├── main_refactored.py     # File chính (mới)
│   ├── main.py                # File gốc (giữ lại để tham khảo)
│   ├── image_detector.py      # Module phát hiện hình ảnh
│   ├── automation_core.py     # Logic automation chính
│   ├── ui_components.py       # Giao diện người dùng
│   ├── stats_manager.py       # Quản lý thống kê
│   └── loop_detector.py       # Phát hiện và xử lý lặp
└── requirements.txt           # Dependencies
```

## Mô tả các module

### 1. `image_detector.py`
- **Chức năng**: Phát hiện các element UI trên màn hình bằng template matching
- **Class chính**: `ImageDetector`
- **Methods**:
  - `detect_all_lesson_images()`: Tìm tất cả lessons
  - `detect_play_button()`: Tìm play button
  - `detect_refresh_button()`: Tìm refresh button
  - `detect_expand_button()`: Tìm expand button

### 2. `automation_core.py`
- **Chức năng**: Logic automation chính
- **Class chính**: `AutomationCore`
- **Methods**:
  - `start_automation()`: Bắt đầu automation
  - `stop_automation()`: Dừng automation
  - `automation_loop()`: Vòng lặp chính
  - `test_detect()`: Test các function detect

### 3. `ui_components.py`
- **Chức năng**: Giao diện người dùng Tkinter
- **Class chính**: `AutoSICUI`
- **Features**:
  - Control panel với các nút bấm
  - Log area để hiển thị hoạt động
  - Stats display để xem thống kê
  - Step tracking để theo dõi tiến trình

### 4. `stats_manager.py`
- **Chức năng**: Quản lý thống kê hoạt động
- **Class chính**: `StatsManager`
- **Tracking**:
  - Số lessons đã click
  - Số videos đã hoàn thành
  - Số lần expand
  - Thời gian chạy

### 5. `loop_detector.py`
- **Chức năng**: Phát hiện và xử lý lặp vô hạn
- **Class chính**: `LoopDetector`
- **Features**:
  - Theo dõi các hành động lặp lại
  - Tự động restart khi phát hiện lặp
  - Configurable threshold

### 6. `main_refactored.py`
- **Chức năng**: File chính kết nối tất cả các module
- **Class chính**: `AutoSICApp`
- **Responsibilities**:
  - Khởi tạo và kết nối các components
  - Quản lý callbacks giữa các module
  - Điều phối hoạt động tổng thể

## Ưu điểm của cấu trúc mới

1. **Separation of Concerns**: Mỗi module có trách nhiệm riêng biệt
2. **Maintainability**: Dễ bảo trì và debug từng phần
3. **Reusability**: Có thể tái sử dụng các component
4. **Testability**: Dễ test từng module riêng lẻ
5. **Scalability**: Dễ mở rộng thêm tính năng mới

## Cách chạy

### Chạy phiên bản mới (được refactor):
```python
python Src/main_refactored.py
```

### Chạy phiên bản cũ (để so sánh):
```python
python Src/main.py
```

## Migration Guide

Nếu muốn chuyển từ file cũ sang mới:
1. Backup file `main.py` cũ
2. Sử dụng `main_refactored.py` làm entry point mới
3. Các tính năng và UI giữ nguyên như cũ

## Lưu ý

- Tất cả functionality vẫn giữ nguyên như phiên bản gốc
- Chỉ thay đổi cấu trúc code, không thay đổi behavior
