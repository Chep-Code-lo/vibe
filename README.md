# Learning Failure Lab (Edu)

Bộ tài liệu triển khai dự án web **Learning Failure Lab** (học từ sai lầm tư duy) theo rubric chấm điểm nghiêm ngặt 100 điểm.

## Mục tiêu
- Xây dựng web học tập nơi người học được phân tích sai lầm theo kiểu tư duy (không chỉ đúng/sai).
- Đảm bảo chất lượng theo 10 tiêu chí: UI/UX, logic ứng dụng, backend/API, database, bảo mật, hiệu năng, vận hành, analytics và chiến lược sản phẩm.

## Cấu trúc tài liệu
- `docs/01_prd.md`: PRD + chiến lược sản phẩm + user persona + phạm vi MVP.
- `docs/02_architecture.md`: kiến trúc hệ thống, module, luồng dữ liệu.
- `docs/03_backend_api.md`: API spec (REST), quy tắc nghiệp vụ, RBAC.
- `docs/04_ui_ux.md`: guideline giao diện, trải nghiệm, thông báo/loading.
- `docs/05_security_performance_ops.md`: security checklist, hiệu năng, CI/CD, backup.
- `docs/06_demo_checklist.md`: checklist demo và thang tự chấm.
- `sql/schema.sql`: schema cơ sở dữ liệu chuẩn hóa.
- `openapi.yaml`: đặc tả API khởi tạo.

## Đề xuất stack triển khai
- Frontend: Next.js + TypeScript + Tailwind + React Query.
- Backend: NestJS + TypeScript + Prisma.
- DB: PostgreSQL.
- Cache/Queue: Redis + BullMQ.
- Quan sát hệ thống: OpenTelemetry + Grafana/Prometheus.
- Auth: JWT access/refresh + RBAC.

## Lộ trình 4 sprint (8 tuần)
1. Sprint 1: Auth + User/Profile + ngân hàng câu hỏi + UI nền tảng.
2. Sprint 2: Quiz session + engine phân loại lỗi + analytics cá nhân.
3. Sprint 3: Dashboard GV/Admin + bảo mật + hardening.
4. Sprint 4: Tối ưu hiệu năng + CI/CD + demo/rehearsal.

Xem chi tiết trong từng file docs.
