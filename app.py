from flask import Flask, render_template, request, send_file, send_from_directory
import os
import re
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
# 使用系统临时目录
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制文件大小为16MB

@app.route('/favicon.ico')
def favicon():
    return '', 204

def has_chinese(text):
    """检查文本是否包含中文字符"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))

def process_file(input_path):
    """处理文件，删除包含中文的行"""
    output_path = os.path.join(tempfile.gettempdir(), 'processed_' + os.path.basename(input_path))
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 过滤掉包含中文的行
        filtered_lines = [line for line in lines if not has_chinese(line)]
        
        # 写入处理后的内容
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(filtered_lines)
        
        return output_path
    except Exception as e:
        app.logger.error(f"处理文件时出错: {str(e)}")
        raise

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"渲染模板时出错: {str(e)}")
        return str(e), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '没有选择文件', 400
    
    file = request.files['file']
    if file.filename == '':
        return '没有选择文件', 400
    
    if not file.filename.endswith('.txt'):
        return '请上传txt文件', 400
    
    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        input_path = os.path.join(tempfile.gettempdir(), filename)
        file.save(input_path)
        
        # 处理文件
        output_path = process_file(input_path)
        
        # 返回处理后的文件
        return send_file(output_path, 
                        as_attachment=True,
                        download_name='processed_' + filename)
    
    except Exception as e:
        app.logger.error(f"上传处理时出错: {str(e)}")
        return f"处理文件时出错: {str(e)}", 500
    finally:
        # 清理临时文件
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'服务器错误: {error}')
    return "服务器内部错误，请稍后重试", 500

if __name__ == '__main__':
    app.run()
