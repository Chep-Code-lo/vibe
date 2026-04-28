# Learning Failure Lab (Web MVP hoàn chỉnh)

Ứng dụng web học tập giúp người dùng **học từ sai lầm tư duy** thay vì chỉ đúng/sai.

## Tính năng đã triển khai
- Đăng ký / đăng nhập (token Bearer).
- Chọn chủ đề học tập.
- Làm quiz theo từng câu.
- Submit phiên học và nhận:
  - điểm số,
  - phân tích `errorBreakdown` theo taxonomy (`MISCONCEPTION`, `CONFUSION`, `LOGIC_GAP`, `RANDOM_GUESS`, `OVERCONFIDENCE`).
- Dashboard analytics cá nhân: các lỗi thường mắc.
- Backend + DB SQLite tự khởi tạo dữ liệu mẫu.

## Cấu trúc
- `app/main.py`: HTTP server + REST API + auth + business logic.
- `static/`: frontend HTML/CSS/JS.
- `data/`: SQLite database runtime.
- `docs/`: tài liệu kiến trúc/PRD/security/demo.
- `openapi.yaml`: hợp đồng API khởi tạo.

## Chạy local
```bash
python app/main.py
```

Sau đó mở: `http://localhost:8000`

## Tài khoản mẫu
- Admin seed sẵn:
  - email: `admin@lab.local`
  - password: `Admin123!`

## API chính
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/topics`
- `GET /api/v1/questions?topicId=...`
- `POST /api/v1/sessions`
- `POST /api/v1/sessions/:id/attempts`
- `POST /api/v1/sessions/:id/submit`
- `GET /api/v1/me/analytics/errors`

## Ghi chú
- Đây là MVP một service để demo học thuật và bảo vệ đồ án.
- Có thể mở rộng sang kiến trúc tách frontend/backend, JWT chuẩn, PostgreSQL, Redis, CI/CD đầy đủ như bộ docs đã mô tả.
