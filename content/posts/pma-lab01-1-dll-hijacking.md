+++
title = "PMA Lab01-1: Phân tích mã độc sử dụng DLL giả mạo kernel32.dll"
date = 2026-09-16
description = "Phân tích tĩnh và động Lab01-1 - Mã độc sử dụng kỹ thuật DLL search order hijacking với kerne132.dll"
tags = ["malware-analysis", "PMA", "lab01", "reversing", "PE-analysis"]
+++

# PMA Lab01-1: Phân tích mã độc DLL Hijacking

Trong bài lab này, chúng ta sẽ phân tích một cặp file malware gồm `Lab01-1.exe` và `Lab01-1.dll`. Đây là một ví dụ kinh điển về kỹ thuật **DLL Search Order Hijacking**.

## 1. Tổng quan

Bộ malware bao gồm 2 file:
- `Lab01-1.exe`
- `Lab01-1.dll`

Cả 2 file đều được biên dịch bằng **Microsoft Visual C\C++ 6.0** và có thời gian tạo rất gần nhau → nhiều khả năng được tạo bởi cùng một tác giả.

## 2. Kiểm tra hash & VirusTotal

Đầu tiên, ta tính mã hash của cả 2 file để đảm bảo tính toàn vẹn:

![Hash](Pasted_image_20260916144354.png)

Kiểm tra trên VirusTotal:

**Lab01-1.exe:**
- 53/69 trình test cảnh báo → Rất có thể là mã độc
![VT Exe](Pasted_image_20260916152255.png)

**Lab01-1.dll:**
- 38/69 trình test phát hiện, hầu hết báo là trojan
![VT DLL](Pasted_image_20260916152703.png)

## 3. Kiểm tra định dạng PE

Cả 2 file đều là **PE 32-bit**, kiến trúc x86:
![PE Info](Pasted_image_20260916144033.png)

## 4. Phân tích Strings

**Strings của Lab01-1.exe:**
![Strings Exe](Pasted_image_20260916171427.png)
![Strings Exe 2](Pasted_image_20260916171510.png)
![Strings Exe 3](Pasted_image_20260916171527.png)

Phát hiện khả nghi:
- Đường dẫn `C:\windows\system32\kernel32.dll`
- **2 chuỗi rất đáng ngờ:**
    - `kerne132.dll` (chữ 'l' thay bằng số '1')
    - `kernel32.dll`

→ Chương trình cố tình nhái `kernel32.dll` bằng cách thay ký tự `l` bằng số `1`!

**Strings của Lab01-1.dll:**
![Strings DLL](Pasted_image_20260916171630.png)
![Strings DLL 2](Pasted_image_20260916181620.png)

Các chuỗi đáng chú ý:
- Địa chỉ IP lạ: `127.26.152.13`
- `ADFHUHF` - Có thể là mã hóa
- `/fI@f]0h@p0` - Có thể là mật khẩu/mã hóa
- `141GI1l1`, `1Y2a2g2r2`, `3!3}3` - Các chuỗi lạ khác

## 5. Phân tích với PEiD

**Lab01-1.exe:**
![PEiD](Pasted_image_20260916081506.png)

- Compiler: **Microsoft Visual C++ 6.0**
![Section Viewer](Pasted_image_20260916081517.png)

Section sizes:
- `.text`: 0x970 < 0x1000
- `.rdata`: 0x2B2 < 0x1000
- `.data`: 0xFC < 0x1000

→ Virtual size ≈ Real size → **File không bị pack/obfuscate**

## 6. Phân tích Dependencies

### Lab01-1.exe
![Dependencies](Pasted_image_20260916150916.png)

File phụ thuộc vào 2 thư viện chính:

#### KERNEL32.dll
![Kernel32](Pasted_image_20260916155557.png)

Các hàm được sử dụng:
![Kernel32 Functions](Pasted_image_20260916160744.png)

**Phân tích nhóm hàm:**

1. **Duyệt thư mục:**
    - `FindFirstFileA | FindNextFileA | FindClose` - Quét file trong thư mục
    ![FindFile](Pasted_image_20260916161545.png)

2. **Copy file:**
    - `CopyFile` - Copy file đến vị trí khác
    ![CopyFile](Pasted_image_20260916162159.png)

3. **Tạo/Mở file:**
    - `CreateFileA / CloseHandle` - Mở hoặc tạo file trên ổ đĩa

4. **Ánh xạ bộ nhớ:**
    - `CreateFileMappingA / MapViewOfFile / UnmapViewOfFile` - Ánh xạ file vào RAM để đọc/sửa
    ![MapView](Pasted_image_20260916163410.png)
    ![MapView 2](Pasted_image_20260916163325.png)
    ![MapView 3](Pasted_image_20260916163337.png)

5. **Kiểm tra vùng nhớ:**
    - `IsBadReadPtr` - Kiểm tra quyền đọc vùng nhớ (tránh crash)
    ![IsBadReadPtr](Pasted_image_20260916163643.png)

**Dự đoán hành vi:** Chương trình duyệt thư mục để tìm một file cụ thể → copy file đó đến vị trí khác → mở/tạo file trên ổ đĩa → ánh xạ vào RAM để chỉnh sửa trực tiếp.

Kết hợp với strings:
- `C:\*` → Duyệt ổ C
- Copy đến `C:\windows\system32\`
- File giả mạo: `kerne132.dll`

→ **Dự đoán:** Chương trình copy `kerne132.dll` đến `C:\windows\system32\`. Khi một chương trình khác vô tình gõ nhầm tên, sẽ load thư viện chứa mã độc này.

#### MSVCRT.dll
![MSVCRT](Pasted_image_20260916160500.png)

Đây là thư viện chuẩn của Microsoft Visual C++ 6.0 - Không có gì khả nghi.

### Lab01-1.dll
![DLL Dependencies](Pasted_image_20260916175935.png)

3 thư viện chính:
- KERNEL32.DLL
- MSVCRT.DLL
- **WS2_32.DLL** ← Đáng chú ý nhất

#### WS2_32.DLL
![WS2_32](Pasted_image_20260916180457.png)

Đây là thư viện giúp chương trình Windows truyền/nhận dữ liệu qua mạng Internet/LAN.

![Network Functions](Pasted_image_20260916181212.png)
![WSA Functions](Pasted_image_20260916182829.png)

Các hàm gọi đến server:
- `connect()`, `send()`, `recv()`, `bind()`, `listen()`, `accept()`

## 7. Giả thuyết

### Giả thuyết 1 (Khả năng cao nhất) - Reverse Backdoor:

Chương trình này là một **Client (Reverse Backdoor)**:
- Sử dụng `connect()` để kết nối đến IP `127.26.152.13` (server của hacker)
- `send()`/`recv()` để gửi thông điệp "Hello" và nhận lệnh từ hacker

**Luồng hoạt động:**
1. File exe copy thư viện DLL, đổi tên thành `kerne132.dll`, copy vào `C:\windows\system32\`
2. Khi chương trình khác gọi nhầm tên → load thư viện mã độc
3. DLL chủ động kết nối ngược về IP `127.26.152.13`
4. Gửi "Hello" → báo cho hacker biết máy đã bị nhiễm
5. Nhận lệnh từ hacker → thực thi → gửi kết quả về

### Giả thuyết 2 - Server:

Chương trình là **server**:
- `bind()` mở cổng trên máy nạn nhân
- `listen()` chờ kết nối
- `accept()` chấp nhận kết nối
- `connect()` có thể là backup channel

## 8. Phân tích động

Tiến hành trên FlareVM với snapshot sạch:

![Snapshot](Pasted_image_20260916191812.png)

Đảm bảo không có kết nối mạng ra ngoài:
![Network](Pasted_image_20260916191943.png)

![Dynamic 1](Pasted_image_20260916193316.png)
![Dynamic 2](Pasted_image_20260916193441.png)
![Dynamic 3](Pasted_image_20260916193149.png)
![Dynamic 4](Pasted_image_20260916193817.png)
![Dynamic 5](Pasted_image_20260916193912.png)
![Dynamic 6](Pasted_image_20260916200510.png)
![Dynamic 7](Pasted_image_20260916200638.png)
![Dynamic 8](Pasted_image_20260916201805.png)

## Kết luận

Đây là một malware sử dụng kỹ thuật **DLL Search Order Hijacking** kinh điển:
1. Tạo file `kerne132.dll` giả mạo `kernel32.dll`
2. Copy vào thư mục hệ thống
3. Khi victim gõ nhầm tên → load mã độc
4. Mã độc tạo reverse backdoor về server hacker

Việc phân tích cho thấy tầm quan trọng của việc kiểm tra kỹ các string khả nghi và phân tích import table để hiểu hành vi của malware.