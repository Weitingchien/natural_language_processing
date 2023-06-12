import os
import random
import string
import nltk
import spacy
import shutil
import requests
from nltk.tokenize import word_tokenize
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from transformers import BartTokenizer, BartForConditionalGeneration
from PyPDF2 import PdfReader
from flask_cors import CORS



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

def summarize(text):
    model_name = 'facebook/bart-large-cnn'
    tokenizer = BartTokenizer.from_pretrained(model_name)
    print(f'max_length: {tokenizer.model_max_length}')
    model = BartForConditionalGeneration.from_pretrained(model_name)
    combined_string = ' '.join(text)
    text = combined_string
    # truncation: 
    encoded_input = tokenizer(text, truncation=True, padding='longest', max_length=1024, return_tensors='pt')
    # num_beams: 控制解碼時beam search的寬度，影響生成文本的多樣性和品質(範圍通常是1~10)。
    # early_stopping: 提前停止有助於提高解碼期間的效率。
    summary_ids = model.generate(encoded_input['input_ids'], num_beams=4, max_length=500, early_stopping=True)
    summary = tokenizer.decode(summary_ids.squeeze(), skip_special_tokens=True)
    print(type(summary))
    # 創建分詞器實體
    doc = nlp(summary)
    # 進行分詞
    summary = [token.text for token in doc]
    summary = ' '.join(summary)
    return summary


# 生成隨機字母數字後綴
def generate_suffix():
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return suffix



def readPDFFile(fileName):
    print(f'fileName: {fileName}')
    temp = []
    reader = PdfReader(f'uploads/{fileName}')
    # printing number of pages in pdf file
    print(len(reader.pages))
    # getting a specific page from the pdf file
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        # extracting text from page
        text = page.extract_text()
        # Word tokenization
        tokens = word_tokenize(text)
        segmented_tokens = []
        for token in tokens:
            doc = nlp(token)
            segmented_token = ' '.join([token.text for token in doc])
            segmented_tokens.append(segmented_token)
        segmented_text = ' '.join(segmented_tokens)
        temp.append(segmented_text)
        #print(temp)
    return summarize(temp)


@app.route('/search', methods=['POST'])
def search():
    path = 'C:\\Users\\LaB2146\\Downloads'
    pdf_data = []
    pdf_files_name = []
    # 獲取當天日期
    #today = datetime.now().date()
    current_datetime = datetime.now()
    keyword = request.json['keyword']
    if keyword:
        data = {'keyword': keyword}
        response = requests.post('http://127.0.0.1:5001/crawl', json=data)
        if response.status_code == 200:
            today_files = []
            result = response.json()
            #print(f'result{result}')
            pdf_files = result['data']
            pdf_files = pdf_files[:3]
            # 獲取路徑下所有文件
            files = os.listdir(path)
            # 過濾出當天的文件
            
            for pdf_file in files:
                file_path = os.path.join(path, pdf_file)
                # 獲取文件的修改時間
                modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if modification_time.date() == current_datetime.date() and modification_time >= datetime.combine(current_datetime.date(), current_datetime.time()):
                    today_files.append(pdf_file)
            
            sorted_files = sorted(today_files, key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=False)
            latest_files = sorted_files[:3]
            #today_files = []

            # 建立上傳文件夾的路徑
            uploads_path = os.path.join(os.path.dirname(__file__), 'uploads')
            print(f'upload_path: {uploads_path}')
            os.makedirs(uploads_path, exist_ok=True)
            # 移除uploads資料夾，用於存放新的PDF檔案
            shutil.rmtree(uploads_path)
            os.makedirs(uploads_path, exist_ok=True)

            for i, pdf_file in enumerate(latest_files):
                original_file_name = pdf_files[i]
                #new_file_name = f"{pdf_files[i]}.pdf"
                new_file_name = pdf_files[i].replace(':', '_') + '.pdf'
                print(f"Processing PDF file: {pdf_file} ({pdf_files[i]})")
                old_file_path = os.path.join(path, pdf_file)
                new_file_path = os.path.join(path, new_file_name)
                new_file_path_in_uploads = os.path.join(uploads_path, new_file_name)

                while os.path.exists(new_file_path):
                    # 若新的檔案名稱已存在，則在檔名中添加後綴
                    suffix = generate_suffix()
                    new_file_name = f"{pdf_files[i]}_{suffix}.pdf"
                    new_file_path = os.path.join(path, new_file_name)
                    new_file_path_in_uploads = os.path.join(uploads_path, new_file_name)
                    # 重命名文件
                
                os.rename(old_file_path, new_file_path)
                print(f"Renamed {pdf_file} to {new_file_name}")
                shutil.move(new_file_path, new_file_path_in_uploads, copy_function=shutil.copy2)
                print(f"Moved PDF file to uploads folder: {new_file_path_in_uploads}")
            uploaded_files = sorted(os.listdir(uploads_path))
            for uploaded_file in uploaded_files:
                summary = readPDFFile(uploaded_file)
                pdf_data.append(summary)
                pdf_files_name.append(uploaded_file)
                print(f"Added to pdf_data: {uploaded_file}")
            
            return jsonify({'message': 'success', 'data': pdf_data, 'file_name': pdf_files_name, 'status': 200})
        else:
            print('爬蟲請求失敗:', response.status_code)
            return jsonify({'message': 'error'})
    else:
        return jsonify({'message': 'error'})
    


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['pdf_file']
    if file:
        file.save('uploads/' + file.filename)
        data = readPDFFile(file.filename)
        print(f'data: {data}')
        return jsonify({'message': 'success', 'data': data, 'status': 200, 'file_name': file.filename})
    else:
        return jsonify({'message': 'error'})



if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)