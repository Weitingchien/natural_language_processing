import os
import nltk
import spacy
from nltk.tokenize import word_tokenize
from flask import Flask, render_template, request, jsonify
from transformers import BartTokenizer, BartForConditionalGeneration
from PyPDF2 import PdfReader
from flask_cors import CORS
import requests


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
    return summary


def readPDFFile(fileName):
    reader = PdfReader(f'uploads/{fileName}')
    # printing number of pages in pdf file
    print(len(reader.pages))
    temp = []
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
        print(temp)
    return summarize(temp)


@app.route('/search', methods=['POST'])
def search():
    keyword = request.json['keyword']
    print(keyword)
    if keyword:
        data = {'keyword': keyword}
        response = requests.post('http://127.0.0.1:5001/crawl', json=data)
        if response.status_code == 200:
            result = response.json()
            print(result)
            return jsonify({'message': 'success', 'data': result, 'status': 200})
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
        return jsonify({'message': 'success', 'data': data, 'status': 200, 'file_name': file.filename})
    else:
        return jsonify({'message': 'error'})



if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)