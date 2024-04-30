from transformers import TapexTokenizer, BartForConditionalGeneration
import pandas as pd

data = {"Stocks": ["NVIDIA", "APPLE", "TESLA", "ABC"], "Predicted Price Change": ["28", "-12", "39", "-8"]}
table = pd.DataFrame.from_dict(data)
print(table)

print("Loading Pipeline")

tokenizer = TapexTokenizer.from_pretrained("chatbot/tokenizer")
model = BartForConditionalGeneration.from_pretrained("chatbot/tapex")

while True:
    query = input("Ask Question: ")
    encoding = tokenizer(table=table, query=query, return_tensors="pt")
    outputs = model.generate(**encoding)

    print(tokenizer.batch_decode(outputs, skip_special_tokens=True))