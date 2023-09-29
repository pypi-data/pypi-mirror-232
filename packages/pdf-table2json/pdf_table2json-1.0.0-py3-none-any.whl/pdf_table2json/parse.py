import pdf_table2json.converter as converter
import json

path = ""
result = converter.main(path)

print("===================================================================")
print(result)