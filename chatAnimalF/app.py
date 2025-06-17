# Importación de librerías necesarias
from flask import Flask, request, render_template, url_for  # Librerías de Flask para manejo de rutas, peticiones y templates
from groq import Groq  # Cliente para interactuar con la API de Groq
import base64  # Para codificar imágenes a Base64
from pathlib import Path  # Para manejar rutas de archivos de forma segura

app = Flask(__name__)  # Crea la instancia de la aplicación Flask

# Inicializa el cliente de Groq con tu API key
client = Groq(api_key="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")

# Ruta principal del sitio: se accede con un GET (cuando el usuario entra a la página)
@app.route("/", methods=["GET"])
def pregunta():
    return render_template("pregunta.html")  # Renderiza y muestra la plantilla HTML llamada "pregunta.html"

# Ruta que se activa cuando el formulario se envía (método POST)
@app.route("/respuesta", methods=["POST"])
def respuesta():
    image_file = request.files.get("image")  # Extrae el archivo de imagen enviado en el formulario


    if not image_file or image_file.filename == "":
        return "Faltan datos de la imagen", 400  # Valida si se subió una imagen

    # Lee el contenido del archivo de imagen subido por el usuario y lo codifica en base64
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    # Crea una URL de datos que representa la imagen en base64
    image_data_url = f"data:{image_file.content_type};base64,{encoded_image}"


# Se construye una lista de mensajes para enviar al modelo
    messages = [
        {
            "role": "user",  # Rol del mensaje: "user" indica que es el usuario quien habla
            "content": [
                {
                    "type": "text",  # Primer tipo de contenido: texto
                    "text": "Analiza la imagen y responde: ¿El alimento que aparece es apto para el consumo humano? ¿Es legal en todos los países? Explica brevemente su procedencia, riesgos y aceptación cultural máximo 500 caracteres. Si no puedes identificarlo, intenta describir lo que hay en la imagen y explica por qué no sería comestible máximo 250 caracteres."
                    # Pregunta que se le hará al modelo, indicando que debe limitarse a 500 caracteres
                },
                {
                    "type": "image_url",  # Segundo tipo de contenido: imagen
                    "image_url": {
                        "url": image_data_url  # URL en formato base64 de la imagen subida
                    }
                }
            ]
        }
    ]     

    # Obtener respuesta textual
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",  # Modelo elegido (acepta imágenes y texto)
        messages=messages,  # Mensajes que contienen la instrucción del usuario y la imagen
        temperature=1,  # Nivel de creatividad: 1 es más variable, 0 es más preciso
        max_completion_tokens=1024,  # Máximo de tokens (palabras o partes de palabras) en la respuesta
        top_p=1,  # Top-p sampling: 1 significa sin recorte (usa todas las opciones probables)
        stream=False,  # No se usa streaming; espera la respuesta completa antes de continuar
        stop=None  # No se establece ningún token de parada explícito
    )

    # Extrae la respuesta generada
    answer = completion.choices[0].message.content

    # Generar audio a partir de la respuesta
    speech_path = Path("static/speech.wav")
    speech_path.parent.mkdir(exist_ok=True)  # Crea la carpeta "static" si no existe

    # Llama a la API para generar el archivo de audio a partir del texto
    response_audio = client.audio.speech.create(
        model="playai-tts-arabic",  # Modelo de texto a voz
        voice="Nasser-PlayAI",      # Voz específica (puede cambiarse)
        response_format="wav",      # Formato de salida del audio
        input=answer,
    )
    response_audio.write_to_file(speech_path)  # Guarda el archivo de audio


    # URL para acceder al audio desde el navegador
    audio_url = url_for('static', filename='speech.wav')

    # Muestra la respuesta textual y el reproductor de audio en HTML
    return render_template("respuesta.html", answer=answer, audio_url=audio_url)


if __name__ == "__main__":
    app.run(debug=True)  # Ejecuta el servidor Flask en modo desarrollo
