# 03. Backend & API Blueprint

## 1) Quy tắc nghiệp vụ cốt lõi
- Mỗi đáp án sai bắt buộc map tối thiểu 1 `error_type`.
- `session` chỉ được submit 1 lần (idempotent key để tránh double submit).
- User chỉ xem dữ liệu của mình; teacher xem trong phạm vi lớp; admin toàn cục.

## 2) RBAC
- `STUDENT`: làm bài, xem dashboard cá nhân.
- `TEACHER`: xem thống kê lớp, giao bài.
- `ADMIN`: quản trị câu hỏi/chủ đề/người dùng.

## 3) API endpoint đề xuất
### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`

### Question bank
- `GET /api/v1/topics`
- `GET /api/v1/questions?topicId=&difficulty=`
- `POST /api/v1/admin/questions`
- `PATCH /api/v1/admin/questions/:id`

### Quiz session
- `POST /api/v1/sessions`
- `POST /api/v1/sessions/:id/attempts`
- `POST /api/v1/sessions/:id/submit`
- `GET /api/v1/sessions/:id/result`

### Analytics
- `GET /api/v1/me/analytics/errors`
- `GET /api/v1/me/analytics/progress`
- `GET /api/v1/teacher/classes/:id/analytics`

## 4) Input validation bắt buộc
- DTO validation bằng Zod/class-validator.
- Rate limit login và submit.
- UUID validation mọi route params.

## 5) Response chuẩn
- `success`, `data`, `meta`, `error`.
- Dùng mã lỗi nội bộ: `AUTH_40101`, `SESSION_40901`...

## 6) Audit & truy vết
- Ghi audit cho thao tác admin.
- Correlation ID trong mỗi request.
