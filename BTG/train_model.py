# train_model.py
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import os
import numpy as np

# Configuration
DATA_DIR = 'dataset'
MODEL_SAVE_PATH = 'brain_tumor_model.h5'
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 30

print("🔍 Checking dataset folder...")
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"❌ Folder '{DATA_DIR}' not found! Please create it with 4 subfolders.")

# Verify class balance
print("📊 Checking class distribution...")
class_counts = {}
for class_name in sorted(os.listdir(DATA_DIR)):
    class_path = os.path.join(DATA_DIR, class_name)
    if os.path.isdir(class_path):
        count = len([f for f in os.listdir(class_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        class_counts[class_name] = count
        print(f"  - {class_name}: {count} images")

min_count = min(class_counts.values())
max_count = max(class_counts.values())
if max_count > min_count * 2:
    print("⚠️  Warning: Class imbalance detected! Consider balancing your dataset.")

print("✅ Dataset folder found. Loading images...")

# Enhanced data augmentation
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2,
    shear_range=0.2,
    fill_mode='nearest'
)

train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True  # Important for class weight stability
)

val_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Build model
print("🧠 Building model...")
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(4, activation='softmax')
])

# ✅ CORRECT WAY TO COMPUTE CLASS WEIGHTS
from sklearn.utils.class_weight import compute_class_weight

# Get true labels from training generator
print("⚖️  Computing class weights...")
labels = []
for i in range(len(train_gen)):
    batch_labels = train_gen[i][1]  # (images, labels)
    labels.extend(np.argmax(batch_labels, axis=1))
labels = np.array(labels)

class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(labels),
    y=labels
)
class_weight_dict = dict(enumerate(class_weights))
print("Class weights:", class_weight_dict)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
callbacks = [
    EarlyStopping(monitor='val_accuracy', patience=6, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.3, patience=4, min_lr=1e-7, verbose=1)
]

# Train
print(f"\n🚀 Starting training for up to {EPOCHS} epochs...")
history = model.fit(
    train_gen,
    epochs=EPOCHS,
    validation_data=val_gen,
    class_weight=class_weight_dict,
    callbacks=callbacks,
    verbose=1
)

# Save
model.save(MODEL_SAVE_PATH)
print(f"\n✅ SUCCESS! Model saved to: {MODEL_SAVE_PATH}")

# Final metrics
val_acc = max(history.history['val_accuracy'])  # Best validation accuracy
print(f"\n📊 Best Validation Accuracy: {val_acc:.2%}")
if val_acc < 0.88:
    print("⚠️  Warning: Accuracy is still low. Ensure:")
    print("   - All 'no_tumor' images are real brain MRIs")
    print("   - Folder names EXACTLY match: glioma_tumor, meningioma_tumor, no_tumor, pituitary_tumor")
    print("   - Each class has ≥600 high-quality images")
else:
    print("🎉 Model is ready for deployment!")