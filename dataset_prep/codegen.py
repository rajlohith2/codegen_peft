# Import necessary libraries
from transformers import AutoModelForCausalLM, AutoTokenizer

# Set the checkpoint for the desired model
checkpoint = "Salesforce/codegen-350M-mono"

# Load pre-trained model and tokenizer
model = AutoModelForCausalLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Function to generate code using the model
def generate_code(prompt):
    inputs = tokenizer(prompt, return_tensors="tf")
    completion = model.generate(**inputs)
    return tokenizer.decode(completion[0])

# Example usage
prompt = "def hello_world():"
generated_code = generate_code(prompt)
print(generated_code)
