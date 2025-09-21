import json
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Đọc config
with open("config.json") as f:
    DATABASE_URL = json.load(f)["database"]["url"]

# Tạo engine với connection pool rất nhỏ (phù hợp Supabase free-tier)
engine = create_engine(
    DATABASE_URL,
    pool_size=1,          # chỉ giữ 1 kết nối sẵn
    max_overflow=2,       # thêm tối đa 2 kết nối tạm
    pool_timeout=10,      # chờ 10s trước khi báo lỗi
    pool_recycle=300,     # recycle sau 5 phút để tránh connection die
    pool_pre_ping=True,   # tự check kết nối trước khi dùng
    connect_args={
        "connect_timeout": 10,
        "application_name": "AI-Child-Protection"
    }
)

# Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model Alert
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(String, index=True)
    content = Column(String)
    result = Column(JSON)
    level = Column(String, default="warning")

# Tạo bảng (chỉ chạy 1 lần lúc start app)
Base.metadata.create_all(bind=engine)

# Dependency cho FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
