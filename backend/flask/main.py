import os
import random
import string
import nltk
import spacy
import shutil
import requests
from nltk.tokenize import word_tokenize
from datetime import datetime
from flask import Flask, request, jsonify
from transformers import BartTokenizer, BartForConditionalGeneration
from PyPDF2 import PdfReader
from flask_cors import CORS



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

def summarize(text):
    print(f'text: {text}')
    model_name = 'facebook/bart-large-cnn'
    tokenizer = BartTokenizer.from_pretrained(model_name)
    print(f'max_length: {tokenizer.model_max_length}')
    # BartForConditionalGeneration可以用於生成摘要
    # from_pretrained:載入預訓練模型
    model = BartForConditionalGeneration.from_pretrained(model_name)
    # 將list內的元素以空格連接起來，變成一個字串
    combined_string = ' '.join(text)
    text = combined_string
    # print(f'text: {text}')
    # truncation: 表示在使用BART tokenizer對文本進行Encode時，如果文本長度超過max_length，則自動進行截斷
    # 如果 padding='longest': 確保所有文本具有相同的長度，方便模型並行計算
    # return_tensors='pt': 返回PyTorch tensors，可以方便地用於BART模型的輸入，而不需要額外的轉換或處理
    encoded_input = tokenizer(text, truncation=True, padding='do_not_pad', max_length=1024, return_tensors='pt')
    print(f'encoded_input {encoded_input}')
    # encoded_input['input_ids']: 經過BART tokenizer處理後的文本，轉換成數字序列，每個token都有一個對應的ID
    # beam search: 生成文本的一種算法，較大的值增加生成文本的多樣性，但會降低生成文本的品質(範圍通常是1~10)
    # max_length=500: 生成的摘要最大長度為500
    # early_stopping=True: 當達到最大長度限制時提前停止生成摘要
    summary_ids = model.generate(encoded_input['input_ids'], num_beams=4, max_length=500, early_stopping=True)
    print(f'summary_ids: {summary_ids}')
    # summary_ids.squeeze(): 用於刪除在張量中任何多餘的維度
    # skip_special_tokens=True: 讓Decoder忽略特殊token，只返回具有意義的token，來生成最終的摘要
    summary = tokenizer.decode(summary_ids.squeeze(), skip_special_tokens=True)
    print(type(summary))
    return summary


# 生成隨機字母數字後綴
def generate_suffix():
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return suffix



def readPDFFile(fileName):
    print(f'fileName: {fileName}')
    temp = []
    reader = PdfReader(f'uploads/{fileName}')

    print(len(reader.pages))

    for i in range(len(reader.pages)):
        page = reader.pages[i]
        # 從頁面提取文字
        text = page.extract_text()
        # word_tokenize(text): 將text切分成單詞
        tokens = word_tokenize(text)
        segmented_tokens = []
        for token in tokens:
            doc = nlp(token)
            # 進行更細緻的處理，並且將結果存在segmented_tokens
            segmented_token = ' '.join([token.text for token in doc])
            segmented_tokens.append(segmented_token)
        segmented_text = ' '.join(segmented_tokens)
        temp.append(segmented_text)
        # print(f'temp: {temp}')
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

            # 建立上傳文件夾的路徑
            uploads_path = os.path.join(os.path.dirname(__file__), 'uploads')
            print(f'upload_path: {uploads_path}')
            os.makedirs(uploads_path, exist_ok=True)
            # 移除uploads資料夾，用於存放新的PDF檔案
            shutil.rmtree(uploads_path)
            os.makedirs(uploads_path, exist_ok=True)

            for i, pdf_file in enumerate(latest_files):
                new_file_name = pdf_files[i].replace(':', '_').replace('/', '_') + '.pdf'
                #new_file_name = pdf_files[i].replace(':', '_') + '.pdf'
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