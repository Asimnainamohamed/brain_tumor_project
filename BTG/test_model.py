import tensorflow as tf
from PIL import Image
import numpy as np

model = tf.keras.models.load_model('brain_tumor_model.h5')
class_labels = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']

def predict(img_path):
    img = Image.open(img_path).convert('RGB')
    img = img.resize((224, 224))
    x = np.array(img) / 255.0
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x)
    idx = np.argmax(pred)
    return class_labels[idx], pred[0][idx]

# Test a known "no_tumor" image
result, confidence = predict("dataset/no_tumor/healthy_01.jpg")
print(f"Prediction: {result}, Confidence: {confidence:.2%}")    