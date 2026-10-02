+++
title = "PMA Lab01-4: Phân tích mã độc nâng cao với Disassembly"
date = 2026-09-18
description = "Phân tích sâu Lab01-4 - Disassembly với IDA Pro, phân tích code injection, hollowing process và anti-analysis techniques"
tags = ["malware-analysis", "PMA", "lab01", "reversing", "IDA", "disassembly"]
+++

# PMA Lab01-4: Phân tích nâng cao với Disassembly

Bài lab cuối cùng trong series Lab01 tập trung vào **disassembly** và phân tích code ở mức assembly sử dụng **IDA Pro**.

## Mục tiêu

- Hiểu cách malware thực thi ở mức assembly
- Phân tích các kỹ thuật nâng cao:
    - Code Injection
    - Process Hollowing
    - Anti-debugging
    - API Hashing

## Công cụ

- **IDA Pro** (hoặc IDA Free) - Disassembler chính
- **x64dbg / OllyDbg** - Debugger
- **PE-bear / CFF Explorer** - PE editor
- **API Monitor** - Hook API calls

## Quy trình phân tích

### 1. Load vào IDA

Mở file trong IDA Pro, chờ IDA phân tích xong:

![Lab01-4 1](/images/Pasted_image_20260918213427.png)

Các bước chính:
1. **Load file** - IDA tự động phân tích PE header
2. **Auto-analysis** - IDA phân tích functions, strings, cross-references
3. **Rename functions** - Đặt tên có ý nghĩa cho các hàm
4. **Add comments** - Ghi chú cho các đoạn code phức tạp

### 2. Phân tích Entry Point

![Lab01-4 2](/images/Pasted_image_20260918213455.png)

Tại entry point, xác định:
- Đây là DLL hay EXE?
- Có code anti-analysis không?
- Có unpacking stub không?

### 3. Phân tích Imports

![Lab01-4 3](/images/Pasted_image_20260918213509.png)

Kiểm tra:
- Imports nào đáng ngờ?
- Có sử dụng dynamic API resolution không?
- Có API hashing không?

### 4. Phân tích Strings

![Lab01-4 4](/images/Pasted_image_20260918214128.png)

![Lab01-4 5](/images/Pasted_image_20260918214223.png)

Strings có thể bị obfuscated → cần tìm:
- XOR key
- Decryption routine
- String builder pattern

### 6. Phân tích Cross-references

![Lab01-4 6](/images/Pasted_image_20260918214234.png)

Sử dụng **Xrefs** để theo dõi:
- Hàm nào gọi API nhạy cảm
- Biến nào được sử dụng ở đâu
- Luồng thực thi chính

### 7. Phân tích Functions chính

![Lab01-4 7](/images/Pasted_image_20260918213901.png)
![Lab01-4 8](/images/Pasted_image_20260918213909.png)

Phân tích từng function:
1. Đọc disassembly
2. Dịch sang pseudo-code
3. Đặt tên + comment
4. Xác nhận giả thuyết

### 8. Phát hiện kỹ thuật nâng cao

![Lab01-4 9](/images/Pasted_image_20260918214255.png)

Các kỹ thuật cần tìm:

#### Code Injection
- `VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread`
- Inject code vào process khác

#### Process Hollowing
- `CreateProcess` với `CREATE_SUSPENDED`
- `NtUnmapViewOfSection`
- `SetThreadContext`

#### DLL Injection
- `LoadLibrary`, `GetProcAddress`
- Manual mapping (no LoadLibrary)

### 10. Tổng kết hành vi

![Lab01-4 10](/images/Pasted_image_20260918214342.png)

Sau khi phân tích xong, tổng kết:
- Entry point → Unpacking → Anti-debug → Main logic → Payload → Cleanup
- IOCs (Indicators of Compromise)
- Yara rules

## Bài học kinh nghiệm

1. **IDA Pro mạnh nhưng không phải tất cả** - Kết hợp với debugger
2. **Rename sớm** - Đặt tên có ý nghĩa ngay khi hiểu function
3. **Comment nhiều** - Để nhớ khi quay lại sau
4. **Theo Xrefs** - Hiểu luồng thực thi
5. **Verify với debugger** - Không chỉ dựa vào static analysis

## Kết luận

Phân tích disassembly là kỹ năng quan trọng nhất của malware analyst. Nó giúp:
- Hiểu malware ở mức sâu nhất
- Phát hiện các kỹ thuật anti-analysis
- Tạo signature cho detection
- Reverse engineer các biến thể mới

## Series PMA Lab01

Đây là bài cuối trong series Lab01. Bạn có thể đọc lại:
- [Lab01-1: DLL Hijacking](pma-lab01-1-dll-hijacking.md)
- [Lab01-02: Windows Service](pma-lab01-02-windows-service.md)
- [Lab01-3: Dynamic Analysis](pma-lab01-3-dynamic-analysis.md)
- Lab01-4: Disassembly (bài này)