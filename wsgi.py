from app import app

# 这是 Vercel 需要的
application = app

# 本地运行时使用
if __name__ == "__main__":
    app.run()
