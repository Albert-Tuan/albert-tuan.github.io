+++
title = "PMA Lab01-3: Phân tích mã độc với Dynamic Analysis"
date = 2026-09-18
description = "Phân tích động Lab01-3 - Sử dụng FlareVM, Process Monitor, Process Explorer để quan sát hành vi malware"
tags = ["malware-analysis", "PMA", "lab01", "reversing", "dynamic-analysis"]
+++

# PMA Lab01-3: Phân tích động Malware với FlareVM

Bài lab này tập trung vào **phân tích động** (Dynamic Analysis) - quan sát hành vi của malware khi thực thi trong môi trường an toàn (FlareVM).

## Công cụ sử dụng

- **FlareVM** - Môi trường phân tích malware chuyên dụng
- **Process Monitor** (ProcMon) - Theo dõi hoạt động file system, registry
- **Process Explorer** - Xem process tree, handles, DLLs
- **Regshot** - So sánh registry trước/sau
- **Wireshark** - Bắt gói tin mạng

## Quy trình phân tích

### 1. Chuẩn bị môi trường

- Tạo snapshot sạch cho FlareVM
- Đảm bảo network bị cô lập (host-only hoặc no network)
- Chuẩn bị các công cụ monitoring

### 2. Baseline

Trước khi chạy malware, chụp "ảnh" trạng thái hệ thống:
- Registry snapshot (Regshot)
- File system snapshot
- Network state

### 3. Thực thi và quan sát

Chạy malware và quan sát:

![Lab01-3 1](/images/Pasted_image_20260918205122.png)
![Lab01-3 2](/images/Pasted_image_20260918205222.png)
![Lab01-3 3](/images/Pasted_image_20260918205305.png)

Các hành vi cần chú ý:
- File nào được tạo/sửa/xóa
- Registry key nào được thêm/sửa
- Process nào được tạo
- Network connection nào được mở

### 4. Phân tích Process

![Lab01-3 4](/images/Pasted_image_20260918214036.png)
![Lab01-3 5](/images/Pasted_image_20260918214016.png)
![Lab01-3 6](/images/Pasted_image_20260918210327.png)
![Lab01-3 7](/images/Pasted_image_20260918210340.png)

Quan sát trong Process Explorer:
- Parent-child relationship
- DLLs được load
- Handles được mở
- Thread activity

### 5. Phân tích File System

![Lab01-3 8](/images/Pasted_image_20260918210816.png)
![Lab01-3 9](/images/Pasted_image_20260918211024.png)
![Lab01-3 10](/images/Pasted_image_20260918211419.png)

Quan sát trong Process Monitor:
- File create/write/delete
- Directory operations
- File mapping

### 7. Phân tích Registry

![Lab01-3 11](/images/Pasted_image_20260918211732.png)
![Lab01-3 12](/images/Pasted_image_20260918211834.png)
![Lab01-3 13](/images/Pasted_image_20260918211847.png)

Các vị trí registry cần chú ý:
- `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
- `HKLM\System\CurrentControlSet\Services`
- `HKCU\Software\Microsoft\Windows\CurrentVersion`

### 8. Phân tích Network

![Lab01-3 14](/images/Pasted_image_20260918212252.png)
![Lab01-3 15](/images/Pasted_image_20260918212336.png)

Quan sát trong Wireshark:
- DNS queries
- HTTP requests
- TCP connections
- IRC/HTTP traffic (nếu có)

### 9. Post-analysis

![Lab01-3 16](/images/Pasted_image_20260918213134.png)
![Lab01-3 17](/images/Pasted_image_20260918213218.png)
![Lab01-3 18](/images/Pasted_image_20260918213237.png)

Sau khi malware chạy:
- Chụp registry snapshot mới
- So sánh với baseline
- Tìm các thay đổi (persistence mechanism)

## Bài học kinh nghiệm

1. **Luôn dùng môi trường cô lập** - Tuyệt đối không chạy malware trên máy thật
2. **Snapshot trước & sau** - Để so sánh thay đổi
3. **Quan sát kỹ 30 giây đầu** - Nhiều malware drop payload trong thời gian ngắn
4. **Kết hợp nhiều tool** - Mỗi tool cho cái nhìn khác nhau
5. **Ghi chép lại** - Tài liệu hóa mọi quan sát

## Kết luận

Phân tích động bổ sung cho phân tích tĩnh, giúp:
- Hiểu rõ hơn về hành vi thực tế
- Phát hiện C2 server, persistence mechanism
- Xác nhận các giả thuyết từ phân tích tĩnh