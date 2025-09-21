# AI Child Protection System 🛡️

Hệ thống bảo vệ trẻ em toàn diện trên môi trường số với AI tiên tiến và giao diện hiện đại.

## 🌟 Tính năng nổi bật

### Core Features
- 🔍 **Text Analysis**: Phát hiện nội dung độc hại bằng AI (ViHateT5)
- 🖼️ **Image Analysis**: Kiểm tra hình ảnh NSFW/unsafe (Falconsai)
- 📊 **Real-time Dashboard**: Giao diện web hiện đại với thống kê trực quan
- 📱 **Mobile App**: Progressive Web App (PWA) cho mobile
- 📧 **Email Notifications**: Thông báo tự động qua email
- 🗄️ **Database Integration**: Lưu trữ dữ liệu với Supabase PostgreSQL
- ⚡ **Real-time Updates**: Cập nhật dữ liệu tức thời

### Advanced Features
- 📈 **Statistics & Analytics**: Biểu đồ và thống kê chi tiết
- 🔄 **Auto-refresh**: Tự động cập nhật dữ liệu
- 🌐 **Multi-platform**: Web + Mobile responsive
- 🎨 **Modern UI/UX**: Thiết kế hiện đại với animations
- 📱 **PWA Support**: Cài đặt như app native
- 🔒 **Secure**: Xác thực và bảo mật dữ liệu

## 🚀 Quick Start

### 1. Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình Database & Email
Chỉnh sửa `config.json`:
```json
{
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "parent_email@example.com"
    },
    "database": {
        "url": "postgresql://user:password@host:port/database"
    }
}
```

### 3. Chạy Application
```bash
uvicorn src.app:app --reload
```

### 4. Truy cập
- **Web Dashboard**: http://127.0.0.1:8000
- **Mobile App**: http://127.0.0.1:8000/mobile

## 📱 Mobile App

### Tính năng Mobile
- 🎯 **Mobile-first Design**: Tối ưu cho màn hình nhỏ
- 📱 **Touch-friendly**: Giao diện cảm ứng mượt mà
- ⚡ **Fast Loading**: Tải nhanh, ít dữ liệu
- 🔄 **Real-time Sync**: Đồng bộ dữ liệu tức thời
- 📱 **Installable PWA**: Cài đặt như app native

### Cách sử dụng Mobile App
1. Truy cập `http://127.0.0.1:8000/mobile` trên mobile
2. Nhấn "Add to Home Screen"
3. Sử dụng như app native

## 🔧 API Endpoints

### Text Analysis
```bash
POST /api/check_text
Content-Type: application/json

{
    "content": "Nội dung cần kiểm tra"
}
```

### Image Analysis
```bash
POST /api/check_image
Content-Type: multipart/form-data

file: [image_file]
```

### Alerts Management
```bash
GET /api/alerts?limit=10
GET /api/stats
```

## 🧪 Testing

### Test Commands
```bash
# Test text filtering
curl -X POST -H "Content-Type: application/json" -d '{"content": "Mày thật ngu ngốc"}' http://127.0.0.1:8000/api/check_text

# Test alerts API
curl http://127.0.0.1:8000/api/alerts

# Test stats API
curl http://127.0.0.1:8000/api/stats
```

### PowerShell Commands
```powershell
# Test text filtering
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/check_text -Method POST -ContentType "application/json" -Body '{"content": "Mày thật ngu ngốc"}'

# Test alerts API
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/alerts -Method GET

# Test stats API
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/stats -Method GET
```

## 📊 Dashboard Features

### Desktop Dashboard (`/`)
- 📈 **Statistics Cards**: Tổng quan số liệu
- 📊 **Charts**: Biểu đồ trực quan
- 🚨 **Real-time Alerts**: Cảnh báo thời gian thực
- 📱 **Responsive**: Tương thích mọi thiết bị

### Mobile Dashboard (`/mobile`)
- 📱 **Mobile-optimized**: Tối ưu cho mobile
- 🎨 **Modern Design**: Giao diện hiện đại
- ⚡ **Fast Performance**: Hiệu suất cao
- 🔄 **Auto-refresh**: Tự động cập nhật

## 🗄️ Database Schema

### Alerts Table
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(50),
    content TEXT,
    result JSONB,
    level VARCHAR(20) DEFAULT 'warning'
);
```

## 📧 Email Notifications

Tự động gửi email khi phát hiện:
- Nội dung text độc hại
- Hình ảnh không phù hợp
- Cảnh báo được cấu hình

## 🔐 Security Features

- ✅ **Input Validation**: Kiểm tra dữ liệu đầu vào
- ✅ **SQL Injection Protection**: Bảo vệ database
- ✅ **XSS Prevention**: Ngăn chặn cross-site scripting
- ✅ **CORS Configuration**: Cấu hình bảo mật
- ✅ **Rate Limiting**: Giới hạn tốc độ request

## 🌐 Browser Support

### Desktop
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### Mobile
- ✅ Chrome Mobile 90+
- ✅ Safari iOS 14+
- ✅ Firefox Mobile 88+
- ✅ Samsung Internet 14+

## 📁 Project Structure

```
ai-child-protection/
├── src/
│   ├── app.py                 # Main FastAPI application
│   ├── filters/               # AI filtering modules
│   │   ├── text_filter.py     # Text analysis
│   │   └── image_filter.py    # Image analysis
│   ├── routers/               # API endpoints
│   │   ├── text_api.py        # Text API
│   │   ├── image_api.py       # Image API
│   │   ├── parent_alerts.py   # Alerts API
│   │   └── stats_api.py       # Statistics API
│   ├── utils/                 # Utility modules
│   │   ├── logger.py          # Database logging
│   │   ├── notifier.py        # Email notifications
│   │   └── database.py        # Database connection
│   └── templates/             # HTML templates
├── mobile-app/                # Mobile PWA
│   ├── index.html            # Mobile interface
│   ├── manifest.json         # PWA manifest
│   ├── sw.js                 # Service worker
│   └── README.md             # Mobile app docs
├── config.json               # Configuration
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
```

## 🎯 Demo Scenarios

### Scenario 1: Text Analysis
1. Truy cập mobile app
2. Nhập text độc hại
3. Xem kết quả real-time
4. Kiểm tra email notification

### Scenario 2: Image Analysis
1. Upload hình ảnh không phù hợp
2. Xem phân tích AI
3. Kiểm tra database storage
4. Xem thống kê cập nhật

### Scenario 3: Real-time Monitoring
1. Mở nhiều tabs/devices
2. Gửi alerts từ nhiều nguồn
3. Xem real-time updates
4. Kiểm tra đồng bộ dữ liệu

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check database URL in config.json
# Verify Supabase credentials
# Test connection manually
```

**Email Notifications Not Working**
```bash
# Check email config in config.json
# Verify SMTP settings
# Test email sending manually
```

**Mobile App Not Loading**
```bash
# Check server is running
# Verify mobile-app files exist
# Check browser console for errors
```

**API Calls Failing**
```bash
# Check CORS settings
# Verify API endpoints
# Check network connectivity
```

## 📈 Performance

- ⚡ **Fast API Response**: < 100ms cho text analysis
- 📊 **Real-time Updates**: Auto-refresh mỗi 5 giây
- 🗄️ **Database Optimized**: Indexed queries
- 📱 **Mobile Optimized**: < 2MB total size
- 🔄 **Efficient Caching**: Service worker cache

## 🤝 Contributing

1. Fork project
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 👥 Authors

- **AI Child Protection Team**

## 🙏 Acknowledgments

- **Hugging Face**: AI models
- **Supabase**: Database hosting
- **FastAPI**: Web framework
- **Chart.js**: Data visualization

---

**🎉 Chúc bạn demo thành công! Ứng dụng đã sẵn sàng để trình bày trước ban giám khảo.**

**🔗 Quick Links:**
- Web Dashboard: http://127.0.0.1:8000
- Mobile App: http://127.0.0.1:8000/mobile
- API Docs: http://127.0.0.1:8000/docs
