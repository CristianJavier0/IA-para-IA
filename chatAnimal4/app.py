from flask import Flask, request, render_template, url_for
from groq import Groq
import base64
from pathlib import Path

app = Flask(__name__)

client = Groq(api_key="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")

@app.route("/", methods=["GET"])
def pregunta():
    return render_template("pregunta.html")

@app.route("/respuesta", methods=["POST"])
def respuesta():
    image_file = request.files.get("image")

    if not image_file or image_file.filename == "":
        return "Faltan datos de la imagen", 400

    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    image_data_url = f"data:{image_file.content_type};base64,{encoded_image}"

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "¿El elemento de la foto se come? ¿Si se come en donde esta permitido y en donde no? y limitala a 1100 caracteres",
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

    # Obtener respuesta textual
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    answer = completion.choices[0].message.content

    # Generar audio a partir de la respuesta
    speech_path = Path("static/speech.wav")
    speech_path.parent.mkdir(exist_ok=True)  # Crear carpeta static si no existe

    response_audio = client.audio.speech.create(
        model="playai-tts",
        voice="Mikail-PlayAI",
        response_format="wav",
        input=answer,
    )
    response_audio.write_to_file(speech_path)

    # URL para acceder al audio desde el navegador
    audio_url = url_for('static', filename='speech.wav')

    return render_template("respuesta.html", answer=answer, audio_url=audio_url)

if __name__ == "__main__":
    app.run(debug=True)
