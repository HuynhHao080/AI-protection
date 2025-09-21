# AI Child Protection - Mobile App

Ứng dụng mobile cho hệ thống AI Child Protection với giao diện hiện đại và tính năng PWA.

## Tính năng

- 🎨 **Giao diện hiện đại**: Thiết kế mobile-first với gradient đẹp mắt
- 📱 **Responsive Design**: Tối ưu cho mọi kích thước màn hình mobile
- 🔄 **Real-time Updates**: Cập nhật cảnh báo và thống kê tự động
- 📊 **Dashboard trực quan**: Hiển thị thống kê với biểu đồ
- 🔔 **PWA Support**: Có thể cài đặt như app native
- ⚡ **Offline Ready**: Hoạt động offline với Service Worker
- 🌐 **Multi-language**: Hỗ trợ tiếng Việt

## Cách sử dụng

### Trên Desktop
1. Chạy server: `uvicorn src.app:app --reload`
2. Truy cập: `http://127.0.0.1:8000/mobile`
3. Sử dụng Developer Tools để test mobile view

### Trên Mobile
1. Truy cập `http://[IP_ADDRESS]:8000/mobile` trên mobile browser
2. Nhấn "Add to Home Screen" để cài đặt như app
3. Sử dụng như app native

## API Endpoints

### Kiểm tra Text
```bash
POST /api/check_text
Content-Type: application/json

{
    "content": "Nội dung cần kiểm tra"
}
```

### Kiểm tra Image
```bash
POST /api/check_image
Content-Type: multipart/form-data

file: [image_file]
```

### Lấy Alerts
```bash
GET /api/alerts?limit=10
```

### Lấy Stats
```bash
GET /api/stats
```

## Cấu trúc Files

```
mobile-app/
├── index.html          # Main mobile interface
├── manifest.json       # PWA manifest
├── sw.js              # Service Worker
├── icon.svg           # App icon (SVG)
└── README.md          # Documentation
```

## PWA Features

- **Installable**: Có thể cài đặt trên mobile
- **Offline Support**: Hoạt động khi mất kết nối
- **Background Sync**: Đồng bộ dữ liệu khi có kết nối
- **Push Notifications**: Sẵn sàng cho thông báo (cần backend support)

## Browser Support

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ✅ Mobile browsers

## Development

Để phát triển mobile app:

1. Chỉnh sửa `mobile-app/index.html`
2. Test trên mobile browser
3. Kiểm tra PWA validation
4. Test offline functionality

## Demo Commands

```bash
# Test text filtering
curl -X POST -H "Content-Type: application/json" -d '{"content": "Mày thật ngu ngốc"}' http://127.0.0.1:8000/api/check_text

# Test alerts API
curl http://127.0.0.1:8000/api/alerts

# Test stats API
curl http://127.0.0.1:8000/api/stats
```

## Screenshots

- **Dashboard**: Hiển thị thống kê tổng quan
- **Text Check**: Giao diện kiểm tra văn bản
- **Image Check**: Upload và kiểm tra hình ảnh
- **Alerts List**: Danh sách cảnh báo real-time

## Troubleshooting

### Mobile app không load được
- Kiểm tra server đang chạy
- Kiểm tra firewall blocking
- Thử truy cập từ mobile browser khác

### PWA không cài đặt được
- Kiểm tra HTTPS (PWA yêu cầu HTTPS)
- Kiểm tra manifest.json
- Kiểm tra service worker

### API calls failed
- Kiểm tra CORS settings
- Kiểm tra server đang chạy
- Kiểm tra network connectivity
