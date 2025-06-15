from flask import Flask, request, render_template
from groq import Groq
import base64

app = Flask(__name__)

client = Groq(api_key="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")

@app.route("/", methods=["GET"])
def pregunta():
    return render_template("pregunta.html")

@app.route("/respuesta", methods=["POST"])
def respuesta():
    question = request.form.get("question")
    image_file = request.files.get("image")

    if not question or not image_file or image_file.filename == "":
        return "Faltan datos de la pregunta o la imagen", 400

    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    image_data_url = f"data:{image_file.content_type};base64,{encoded_image}"

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": question
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

    return render_template("respuesta.html", question=question, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
