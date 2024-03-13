# use_saved_model.py
from model_utils import load_model, generate_text

model_load_path = "test_model2.pt"
loaded_model = load_model(model_load_path)

max_new_tokens = 500
generated_text = generate_text(loaded_model, max_new_tokens, "To cancel your purchase")
print(generated_text)