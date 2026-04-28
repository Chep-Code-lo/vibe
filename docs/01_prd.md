# 01. PRD - Learning Failure Lab

## 1) Bài toán
Nhiều nền tảng học tập chỉ cho biết đúng/sai, nhưng không chỉ ra **kiểu sai lầm tư duy**. Dự án giải quyết bài toán này bằng cách:
- Gắn nhãn sai lầm theo taxonomy.
- Cung cấp phản hồi học tập cá nhân hóa.
- Đo tiến bộ bằng tỷ lệ giảm lỗi lặp.

## 2) Mục tiêu sản phẩm
- Mục tiêu học tập: giảm ít nhất 25% lỗi lặp cùng dạng sau 2 tuần.
- Mục tiêu trải nghiệm: thời gian phản hồi mỗi thao tác < 300ms (P95 cho API read).
- Mục tiêu vận hành: uptime >= 99.5% trong giai đoạn demo.

## 3) Persona
- Học sinh THPT/ĐH tự học online.
- Giáo viên cần theo dõi lỗi lớp.
- Quản trị viên nội dung cần quản lý ngân hàng câu hỏi.

## 4) Giá trị khác biệt
- Không chỉ quiz: phân tích `misconception`, `logic_gap`, `confusion`, `random_guess`.
- Có vòng lặp sửa lỗi: làm bài -> phân tích lỗi -> bài luyện tương tự -> đo cải thiện.

## 5) Phạm vi MVP
- Đăng ký/đăng nhập/refresh token.
- Làm bài theo chủ đề.
- Kết quả có phân tích lỗi tư duy.
- Dashboard cá nhân: top lỗi, top chủ đề yếu.
- Admin CRUD câu hỏi + đáp án + nhãn lỗi.

## 6) Ngoài MVP
- AI gợi ý câu hỏi cá nhân hóa.
- Lớp học nhiều giáo viên.
- Chống gian lận nâng cao bằng behavioral biometrics.

## 7) KPI
- Learning KPIs: error repeat rate, remediation success rate.
- Product KPIs: DAU/WAU, D7 retention.
- Technical KPIs: API error rate < 1%, crash-free sessions > 99%.
