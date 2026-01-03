from flask import Flask, render_template, request, redirect
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads/"

model = load_model("model/food_classifier.h5")

classes = {
    0: "burger",
    1: "hotdog",
    2: "pasta",
    3: "pizza",
    4: "sushi",
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    img = image.load_img(filepath, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0

    preds = model.predict(x)
    max_prob = np.max(preds[0])
    class_idx = np.argmax(preds[0])

    if max_prob < 0.5 or class_idx not in classes:
        class_label = "Oops, I don't know what that is"
        confidence = None
    else:
        class_label = classes[class_idx]
        confidence = round(max_prob * 100, 2)

    return render_template(
        "result.html",
        filename=file.filename,
        label=class_label,
        confidence=confidence
    )


if __name__ == "__main__":
    app.run(debug=True)
