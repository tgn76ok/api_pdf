from elevenlabs.client import ElevenLabs

# É uma boa prática não deixar chaves de API diretamente no código.
# Considere usar variáveis de ambiente.
api_key = 'sk_1d42f52eab44685f31c192cf9cade0f3ae25181bdd0a1c6c'

elevenlabs = ElevenLabs(
  api_key=api_key,
)

# 1. Chame a função e armazene o iterador retornado
audio_stream = elevenlabs.text_to_speech.convert(
    voice_id="v3a2WxCpk7965Lwrexlc",
    # O output_format deve ser o formato do áudio, não o caminho do arquivo
    output_format="mp3_44100_128", 
    text="dantas não consegue fazer um botão funcionar e o rato roeu a roupa do rei de roma"
)

# 2. Defina o caminho onde você quer salvar o arquivo
save_path = "output.mp3"

# 3. Escreva o stream de áudio em um arquivo
print(f"Salvando o áudio em {save_path}...")

with open(save_path, "wb") as f:
    for chunk in audio_stream:
        if chunk:
            f.write(chunk)

print("Áudio salvo com sucesso!")