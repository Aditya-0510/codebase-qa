import google.generativeai as genai
genai.configure(api_key="AIzaSyCKcdY5-mSPna_Jqt3Uy0EMM8-SCx2u2dY")

for m in genai.list_models():
    print(m.name)