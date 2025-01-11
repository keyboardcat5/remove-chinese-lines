from app import app

# 这行是给 Vercel 使用的
app.debug = False

if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
