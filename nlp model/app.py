from flask import Flask, request, jsonify
from flask_cors import CORS
from model_utils import load_model, generate_text
from rbmodel import get_response

app = Flask(__name__)
CORS(app)

print("############ APP STARTED ############")

model_load_path = "bigram_language_model2.pt"
loaded_model = load_model(model_load_path)

print("############ MODEL LOADED ############")

while True:
    user_input = input("You: ")
    print("Bot:", get_response(user_input))

if __name__ == '__main__':
    print("Running NLP model")
    app.run(debug=True, host='0.0.0.0')
    