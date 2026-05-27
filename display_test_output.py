with open('test_output.txt', 'r', encoding='utf-16') as f:
    text = f.read()
with open('test_output_decoded.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print('Decoded output written to test_output_decoded.txt')
