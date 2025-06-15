from groq import Groq
import base64

# Tu API key Groq
client = Groq(api_key="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")

# Ruta a la imagen local
image_path = "img/dos.png"

# Leer la imagen y codificarla en base64
with open(image_path, "rb") as f:
    encoded_image = base64.b64encode(f.read()).decode("utf-8")

# Crear data URL con tipo MIME
image_data_url = f"data:image/png;base64,{encoded_image}"

# Preparar mensajes para modelo multimodal
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "¿Qué animal es este?"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data_url
                }
            }
        ]
    }
]

# Crear la petición al modelo (ajusta el modelo si tienes otro válido que acepte imagen)
completion = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=messages,
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)

# Imprimir la respuesta
print(completion.choices[0].message.content)
