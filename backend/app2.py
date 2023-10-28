from flask import Flask, send_from_directory, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__, static_folder="../frontend")

# Global variables to store the current model and tokenizer
model = None
tokenizer = None

@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global model, tokenizer  # Declare them as global to access
    user_input = request.json['user_input']
    input_ids = tokenizer.encode(user_input, return_tensors='pt')
    
    # Generate a response from the model
    with torch.no_grad():
        output = model.generate(input_ids, max_length=50)
        
    # Decode the output and send it back
    chat_output = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return jsonify({'model_response': chat_output})

@app.route('/select_model', methods=['POST'])
def select_model():
    global model, tokenizer  # Declare them as global to modify
    payload = request.json
    print("Received payload:", payload)  # Logging
    
    if 'model_path' not in payload:
        return jsonify({'error': 'model_path not provided'}), 400
    
    model_path = payload['model_path']
    
    # Load the new model and tokenizer based on the provided path
    model = AutoModelForCausalLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    return jsonify({'message': 'Model selected successfully'})

if __name__ == '__main__':
    # Initialize with a default model
    model = AutoModelForCausalLM.from_pretrained('gpt2')
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    
    app.run(debug=True)
