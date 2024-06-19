from transformers import AutoModelForCausalLM, AutoTokenizer
import psycopg2
from datetime import datetime

# Load pre-trained model and tokenizer
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_response(prompt):
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=100, do_sample=True, top_k=50)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Database connection
conn = psycopg2.connect(
    dbname="chatbot_db",
    user="apnauser",
    password="kundan1121",
    host="127.0.0.1"
)
cursor = conn.cursor()

# Functions for memory management
def save_short_term_memory(user_id, context):
    cursor.execute("INSERT INTO short_term_memory (user_id, context) VALUES (%s, %s)", (user_id, context))
    conn.commit()

def retrieve_short_term_memory(user_id):
    cursor.execute("SELECT context FROM short_term_memory WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1", (user_id,))
    return cursor.fetchone()

def save_long_term_memory(user_id, memory):
    cursor.execute("INSERT INTO long_term_memory (user_id, memory) VALUES (%s, %s)", (user_id, memory))
    conn.commit()

def retrieve_long_term_memory(user_id):
    cursor.execute("SELECT memory FROM long_term_memory WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    return cursor.fetchall()

def chatbot_response(user_id, user_input):
    # Retrieve memories
    short_term = retrieve_short_term_memory(user_id)
    long_term = retrieve_long_term_memory(user_id)

    # Combine memories with the user input
    prompt = ""
    if long_term:
        prompt += " ".join([mem[0] for mem in long_term]) + " "
    if short_term:
        prompt += short_term[0] + " "
    prompt += user_input

    # Generate response
    response = generate_response(prompt)

    # Save to short-term memory
    save_short_term_memory(user_id, user_input + " " + response)

    return response

# Example usage
if __name__ == "__main__":
    user_id = "kundan"
    user_input = "Hey whats up"
    response = chatbot_response(user_id, user_input)
    print(response)
