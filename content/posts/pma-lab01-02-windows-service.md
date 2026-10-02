+++
title = "PMA Lab01-02: Phân tích mã độc UPX-packed Windows Service"
date = 2026-09-18
description = "Phân tích chi tiết Lab01-02 - Malware sử dụng UPX packing, đăng ký Windows Service và kết nối C2 qua HTTP"
tags = ["malware-analysis", "PMA", "lab01", "reversing", "UPX", "windows-service"]
+++

# PMA Lab01-02: Phân tích Malware Windows Service với UPX Packing

Trong bài lab này, chúng ta sẽ phân tích `Lab01-02.exe` - một malware sử dụng kỹ thuật UPX packing, đăng ký Windows Service để tự khởi động và kết nối về server C2 qua HTTP.

## 1. Kiểm tra ban đầu

Kiểm tra định dạng file `Lab01-02.exe`:
![File Info](/images/Pasted_image_20260916221225.png)

- **PE 32-bit**
- **Được nén bằng UPX**

## 2. Tính hash và kiểm tra VirusTotal

![Hash](/images/Pasted_image_20260916221501.png)

Kiểm tra trên VirusTotal:
![VT Result](/images/Pasted_image_20260916221631.png)
![VT Detection](/images/Pasted_image_20260916222111.png)

56/69 test phát hiện → Rất có khả năng là mã độc.

## 3. Phân tích PE Header

![PE Header](/images/Pasted_image_20260916222211.png)

Cấu trúc PE có các section đã được mã hóa thành `UPX0`, `UPX1`, `UPX2`:

| Section | R.Size | V.Size | Ghi chú |
|---------|--------|--------|---------|
| UPX0 | 0x00000 | 0x4000 | Chừa vùng nhớ để unpack |
| UPX1 | 0x600 | 0x1000 | Chứa dữ liệu nén + unpacking stub |

**Entry point** tại 0x5410 nằm trong UPX1 (không phải section .text) → Khi file chạy, UPX stub sẽ giải nén payload vào UPX0 trước.

→ **Cần unpack file trước khi phân tích sâu!**

## 4. Unpack với UPX

![UPX Unpack](/images/Pasted_image_20260916224030.png)

Sau khi unpack, kiểm tra lại với PEiD:
![PEiD After](/images/Pasted_image_20260916224111.png)

- Compiler: **Microsoft Visual C++ 6.0**
![Section After](/images/Pasted_image_20260916224212.png)

Các section đã chuẩn (V.size < R.size).

## 5. Phân tích Strings

![Strings](/images/Pasted_image_20260916224641.png)

Các điểm nghi vấn:
- URL: `http://www.malwareanalysisbook.com`
- `MalService` - Tên khả nghi
- `HGL345` - Có thể là password/obfuscated
- `Internet Explorer 8.0` - User agent?

## 6. Phân tích Dependencies

![Imports](/images/Pasted_image_20260918160537.png)

4 thư viện chính:

### Kernel32.dll

![Kernel32](/images/Pasted_image_20260918160720.png)

**Các hàm chính:**

| Hàm | Chức năng |
|-----|-----------|
| `SystemTimeToFileTime` | Chuyển đổi system time thành file time |
| `CreateMutexA` | Tạo/mở mutex |
| `GetModuleFileNameA` | Lấy đường dẫn file exe/dll đang chạy |
| `CreateWaitableTimerA` | Tạo timer object |
| `SetWaitableTimer` | Thiết lập thời điểm kích hoạt timer |
| `WaitForSingleObject` | Chờ object được signal |
| `OpenMutexA` | Mở mutex có sẵn |
| `ExitProcess` | Kết thúc process |
| `CreateThread` | Tạo thread mới |

**Phân nhóm chức năng:**

1. **Thời gian:** `SystemTimeToFileTime`
2. **Tự xác định vị trí:** `GetModuleFileNameA`
3. **Timer/Delay:** `CreateWaitableTimerA`, `SetWaitableTimer`, `WaitForSingleObject`
4. **Mutex/Single instance:** `OpenMutexA`, `CreateMutexA`, `ExitProcess`
5. **Thread:** `CreateThread`
6. **Kết thúc:** `ExitProcess`

**Dự đoán luồng hoạt động:**
1. Khi khởi động → xác định vị trí bản thân
2. Kiểm tra instance khác → nếu có thì thoát
3. Tạo mutex mới
4. Tạo timer để delay
5. Sau delay → start thread thực thi tác vụ chính

### ADVAPI32.dll

![AdvAPI32](/images/Pasted_image_20260918164728.png)

- `OpenSCManagerA` - Kết nối tới Service Control Manager
- `CreateServiceA` - Tạo Windows Service mới
- `StartServiceCtrlDispatcherA` - Yêu cầu SCM khởi động service

→ Chương trình có khả năng liên quan đến **Windows Service**, có thể tự đăng ký làm service.

### MSVCRT.dll
![MSVCRT](/images/Pasted_image_20260918165608.png)

Thư viện chuẩn của MSVC, chưa có gì đặc biệt.

### WININET.dll
![WinINet](/images/Pasted_image_20260918165838.png)

- `InternetOpenA` - Khởi tạo WinINet session
- `InternetOpenUrlA` - Mở tài nguyên qua HTTP/HTTPS/FTP

→ Chương trình khởi tạo session và kết nối tới URL, có thể là `http://www.malwareanalysisbook.com`.

### Dự đoán hành vi:

| String | Hàm tương ứng |
|--------|---------------|
| `MalService`/`Malservice` | `OpenSCManagerA`, `CreateServiceA`, `StartServiceCtrlDispatcherA` |
| `HGL345` | `OpenMutexA`, `CreateMutexA` (Mutex name) |
| `http://www.malwareanalysisbook.com` | `InternetOpenA`, `InternetOpenUrlA` |
| `Internet Explorer 8.0` | User agent cho `InternetOpenA` |

## 7. Disassembly với PE Explorer

![PE Explorer](/images/Pasted_image_20260918173946.png)

Xác nhận các chuỗi có liên quan đến hành vi giả thuyết.

## 8. Phân tích sâu với IDA Free

### Main function

![IDA Main](/images/Pasted_image_20260918180024.png)

Dịch sang pseudo-code:

```c
int main()
{
    SERVICE_TABLE_ENTRY table[2];
    
    table[0].lpServiceName = "MalService";
    table[0].lpServiceProc = sub_401040;
    
    table[1].lpServiceName = NULL;
    table[1].lpServiceProc = NULL;
    
    StartServiceCtrlDispatcherA(table);
    
    sub_401040(0, NULL);
    
    return 0;
}
```

→ **Khẳng định:** `MalService` là tên service đăng ký với `StartServiceCtrlDispatcherA`, và `sub_401040` chính là **ServiceMain**!

### ServiceMain function

![ServiceMain](/images/Pasted_image_20260918180541.png)

```assembly
push offset Name        ; "HGL345"
push 0
push 1F0001h
call OpenMutexA

test eax, eax
jz   loc_401064

push 0 call ExitProcess
```

Dịch sang C:

```c
if (OpenMutexA(MUTEX_ALL_ACCESS, FALSE, "HGL345") != NULL)
{
    ExitProcess(0);  // Đã có instance khác → thoát
}

CreateMutexA(NULL, FALSE, "HGL345");  // Tạo mutex mới
```

→ **Khẳng định:** `HGL345` là **mutex name** để đảm bảo chỉ một instance chạy.

### Service Installation

![Service Install](/images/Pasted_image_20260918181318.png)

```assembly
push 3
push 0
push 0
call OpenSCManagerA
mov esi, eax

; Lấy đường dẫn file
lea eax, Filename
push 3E8h          ; 1000
push eax
push 0
call GetModuleFileNameA

; Tạo service
push ecx                  ; lpBinaryPathName
push 0                    ; dwErrorControl
push 2                    ; dwStartType = SERVICE_AUTO_START
push 10h                  ; dwServiceType = SERVICE_WIN32_OWN_PROCESS
push 2                    ; dwDesiredAccess
push offset DisplayName   ; "Malservice"
push offset DisplayName   ; "Malservice"
push esi                  ; hSCManager
call CreateServiceA
```

Dịch:

```c
hSCM = OpenSCManagerA(NULL, NULL, 3);

GetModuleFileNameA(NULL, Filename, 1000);

CreateServiceA(
    hSCM,
    "Malservice",        // Service name
    "Malservice",        // Display name
    2,                   // SERVICE_ALL_ACCESS
    0x10,                // SERVICE_WIN32_OWN_PROCESS
    2,                   // SERVICE_AUTO_START
    0,                   // No error control
    Filename,            // Binary path = chính nó
    NULL, NULL, NULL, NULL, NULL
);
```

**Kết luận:** Chương trình **cài chính nó thành Windows Service** với:
- Service name: `Malservice`
- BinaryPath: chính `Lab01-02.exe`
- StartType: **AUTO_START** (tự khởi động khi boot)

### Timer Setup

![Timer](/images/Pasted_image_20260918182527.png)

```assembly
xor edx, edx
mov [SystemTime.wYear], 834h   ; 0x834 = 2100
call SystemTimeToFileTime
call CreateWaitableTimerA
call SetWaitableTimer
call WaitForSingleObject
```

→ Chương trình đặt timer đến năm **2100** (gần như vô hạn), sau đó chờ cho đến khi timer kích hoạt.

## 9. Kết luận

`Lab01-02.exe` là một malware với các đặc điểm:

1. **Packing:** Sử dụng UPX để tránh phát hiện
2. **Persistence:** Tự đăng ký làm Windows Service với AUTO_START
3. **Mutex:** `HGL345` để đảm bảo single instance
4. **Timer:** Delay đến năm 2100 (hầu như không bao giờ kích hoạt - chờ manual trigger?)
5. **C2 Communication:** Kết nối tới `http://www.malwareanalysisbook.com` qua WinINet
6. **User Agent:** Giả mạo `Internet Explorer 8.0`

**Mục đích cuối cùng:** Tạo backdoor kết nối ngược về server C2 qua HTTP, cho phép hacker điều khiển từ xa.