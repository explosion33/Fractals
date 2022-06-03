from multiprocessing import pool
from cachetools import Cache
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.preprocessing.image import ImageDataGenerator


tf.get_logger().setLevel('WARNING')

img_height = img_width = 50

# This generates the training dataset from our own image
# by splitting all images randomly.
ds_train = tf.keras.preprocessing.image_dataset_from_directory(
    'images',
    labels='inferred',
    label_mode = "categorical",
    #class_names=[""]
    color_mode='grayscale',
    batch_size=32,
    image_size=(img_height, img_width),
    shuffle=True,
    seed=123,
    validation_split=0.2,
    subset="training"
)


# This generates the validating dataset with a similar process as how
# we have generated our training dataset
ds_validate = tf.keras.preprocessing.image_dataset_from_directory(
    'images',
    labels='inferred',
    label_mode = "categorical",
    #class_names=[""],
    color_mode='grayscale',
    batch_size=32,
    image_size=(img_height, img_width),
    shuffle=True,
    seed=123,
    validation_split=0.2,
    subset="validation"
)


model = keras.Sequential(
    [
        keras.Input(shape=(50, 50, 1)),
        layers.Conv2D(128, 3, activation='relu'),
        layers.MaxPool2D(pool_size=(2, 2)),
        layers.Conv2D(256, 3, activation='relu'),
        layers.MaxPool2D(),
        layers.Conv2D(512, 3, activation='relu'),
        layers.MaxPool2D(),
        layers.Conv2D(1024, 3, activation='relu'),
        layers.MaxPool2D(),
        layers.Flatten(),
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(2),
    ]
)

model.compile(
    loss=keras.losses.CategoricalCrossentropy(from_logits=True),
    optimizer=keras.optimizers.Adam(lr=3e-4),
    metrics=["accuracy"]
)

model.fit(ds_train, batch_size=32, epochs=25, verbose=2)
model.evaluate(ds_validate, batch_size=32, verbose=2)

print(model.summary())