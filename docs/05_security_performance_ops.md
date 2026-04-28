# 05. Security, Performance, Ops

## 1) Security (bắt buộc)
- Argon2 hash + salt cho password.
- JWT access (15m) + refresh (7d), rotate refresh token.
- RBAC middleware + policy checks.
- Helmet, CORS whitelist, CSRF strategy (cookie mode).
- Prepared statements/ORM chống SQL injection.
- Output encoding + CSP chống XSS.
- Upload scanning + giới hạn mime/type.
- Secrets không hardcode, dùng env/secret manager.

## 2) Performance
- Redis cache cho topics và dashboard aggregates.
- Phân trang mọi endpoint list.
- DB indexes cho khóa ngoại + timestamp + topic_id + user_id.
- Tách job nền qua queue cho analytics nặng.
- CDN cho static assets.

## 3) Monitoring
- Log cấu trúc JSON (pino/winston).
- Metrics: latency, error rate, throughput.
- Alert khi error rate > 2% trong 5 phút.

## 4) CI/CD
- Pipeline: lint -> test -> build -> security scan -> deploy.
- Deploy blue/green hoặc rolling.
- Tự động rollback khi healthcheck fail.

## 5) Backup/Recovery
- Backup DB hàng ngày + PITR.
- Kiểm thử restore tối thiểu 1 lần/tháng.
