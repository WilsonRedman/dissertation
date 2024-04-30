def query(query, table, tokenizer, model):

    # Encodes inputs
    encoding = tokenizer(table=table, query=query, return_tensors="pt")

    # Generates output based on encoded input
    outputs = model.generate(**encoding)

    # Decodes the output
    decoded = (tokenizer.batch_decode(outputs, skip_special_tokens=True))

    # Returns answer
    return decoded