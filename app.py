from flask import Flask, render_template, request, send_file
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制文件大小为16MB

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def has_chinese(text):
    """检查文本是否包含中文字符"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))

def process_file(input_path):
    """处理文件，删除包含中文的行"""
    output_path = input_path + '_processed.txt'
    
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
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

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
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        # 处理文件
        output_path = process_file(input_path)
        
        # 返回处理后的文件
        return send_file(output_path, 
                        as_attachment=True,
                        download_name='processed_' + filename)
    
    except Exception as e:
        return str(e), 500
    finally:
        # 清理临时文件
        try:
            os.remove(input_path)
            os.remove(output_path)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True, port=5000) 