# Study Coach Browser Extension v0.1

Extension Manifest V3 dùng chung cho **Brave, Microsoft Edge và Google Chrome**.

## Chức năng

- Chỉ theo dõi playlist C++ mà bạn chủ động chọn.
- Đọc số thứ tự video trong playlist, tiêu đề video và % đã xem.
- Đồng bộ dữ liệu về Study Coach local tại `http://127.0.0.1:8780`.
- Không cần duy trì bản riêng cho Brave/Edge/Chrome.

## Cài trên Brave

1. Mở `brave://extensions`.
2. Bật **Developer mode**.
3. Chọn **Load unpacked**.
4. Chọn thư mục:
   `<thư-mục-clone>\Study-Coach\browser-extension`
5. Mở một video trong playlist C++.
6. Bấm icon **Study Coach**.
7. Chọn **Dùng playlist này làm khóa C++**.

## Cài trên Edge

1. Mở `edge://extensions`.
2. Bật **Developer mode**.
3. Chọn **Load unpacked**.
4. Chọn:
   `<thư-mục-clone>\Study-Coach\browser-extension`

## Cài trên Chrome

1. Mở `chrome://extensions`.
2. Bật **Developer mode**.
3. Chọn **Load unpacked**.
4. Chọn:
   `<thư-mục-clone>\Study-Coach\browser-extension`

## Ghi chú

Nếu Study Coach local chưa chạy, extension vẫn nằm trong trình duyệt nhưng không thể đồng bộ tiến độ cho tới khi `http://127.0.0.1:8780` hoạt động lại.
