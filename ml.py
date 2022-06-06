# Written by Jerry Gao, tested by Blake Sketchley
# This program takes two folders of images and trains a machine learning
# algorithm to determine whether a given image is hand-drawn or
# computer-generated. 

import tensorflow as tf
from tensorflow import keras
from keras import layers


def main():
    tf.get_logger().setLevel('WARNING')

    img_height = img_width = 50

    # This generates the training dataset from our own image
    # by splitting all images randomly.
    ds_train = tf.keras.preprocessing.image_dataset_from_directory(
        'images',
        labels='inferred',
        label_mode="categorical",
        color_mode='grayscale',
        batch_size=32,
        image_size=(img_height, img_width),
        shuffle=True,
        seed=123,
        validation_split=0.2,
        subset="training"
    )

    # This generates the validating dataset with a similar process as how
    # we have generated our training dataset.
    ds_validate = tf.keras.preprocessing.image_dataset_from_directory(
        'images',
        labels='inferred',
        label_mode="categorical",
        color_mode='grayscale',
        batch_size=32,
        image_size=(img_height, img_width),
        shuffle=True,
        seed=123,
        validation_split=0.2,
        subset="validation"
    )

    # This sets up the model with specific amounts of layers, dense
    # layers, and initial neurons. In this setup, there are 4 layers,
    # 3 dense layers, and 32 initial neurons.
    model = keras.Sequential(
        [
            keras.Input(shape=(50, 50, 1)),
            layers.Conv2D(32, 3, activation='relu'),
            layers.MaxPool2D(pool_size=(2, 2)),
            layers.Conv2D(64, 3, activation='relu'),
            layers.MaxPool2D(),
            layers.Conv2D(128, 3, activation='relu'),
            layers.MaxPool2D(),
            layers.Conv2D(256, 3, activation='relu'),
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


if "__main__" in __name__:
    main()