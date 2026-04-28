# 02. Architecture

## 1) Tổng quan kiến trúc
- Client (Next.js) -> API Gateway (NestJS) -> Service layer -> PostgreSQL/Redis.
- Tách read-heavy analytics qua materialized view + cache Redis.

## 2) Module backend
1. Auth Module
   - Register/Login/Refresh/Logout.
   - Password hashing (Argon2), JWT rotation.
2. User Module
   - Profile, settings, learning preferences.
3. Question Bank Module
   - Question, options, correct answer, misconception tags.
4. Session Module
   - Tạo quiz session, ghi nhận attempt, submit.
5. Error Analysis Module
   - Ánh xạ đáp án sai -> error taxonomy.
6. Analytics Module
   - Tổng hợp lỗi theo người dùng/chủ đề/thời gian.
7. Admin Module
   - RBAC, audit logs.

## 3) Error taxonomy (chuẩn)
- `MISCONCEPTION`: hiểu sai bản chất.
- `CONFUSION`: nhầm khái niệm gần nhau.
- `LOGIC_GAP`: suy luận thiếu bước.
- `RANDOM_GUESS`: đoán mò.
- `OVERCONFIDENCE`: trả lời nhanh sai liên tục, độ tự tin cao.

## 4) Luồng chính
1. User login -> lấy access token.
2. Bắt đầu quiz -> API cấp danh sách câu hỏi.
3. User submit từng câu -> lưu attempt.
4. Submit session -> engine phân tích lỗi + scoring.
5. Dashboard đọc aggregate từ view/cache.

## 5) Non-functional requirements
- P95 API read < 300ms, write < 500ms.
- Horizontal scaling backend.
- Không mất dữ liệu attempt khi restart (transaction + retry queue).

## 6) Mô hình triển khai
- Docker hóa từng service.
- Environments: dev/staging/prod.
- Secrets qua biến môi trường + secret manager.
