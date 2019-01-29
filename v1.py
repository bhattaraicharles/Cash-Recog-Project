# -*- coding: utf-8 -*-
"""Cash Recognition for Visually Impaired FineTuned.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tRWcagUABi_06_JJyWNjNvoL_FDfOHEY
"""

import os
import numpy as np
import matplotlib.pyplot as plt

import zipfile

import tensorflow as tf

from google.colab import drive

#import tensorflow_hub as hub

import math

tf.keras.backend.set_session = tf.Session()

drive.mount('/content/drive')



local_zip = 'cash_full_data/full_data.zip' # local path of downloaded .zip file
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/tmp') # contents are extracted to '/tmp' folder
zip_ref.close()

base_dir = '/tmp/full_data'
train_dir = os.path.join(base_dir, 'train') 
validation_dir = os.path.join(base_dir, 'valid')

batch_size = 100
epochs = 100
IMG_SHAPE = 224 # Our training data will consists of images with width of 150 pixels and height of 150 pixels

pre_model = tf.keras.applications.mobilenet_v2.MobileNetV2(input_shape=(224,224,3), alpha=1.0, depth_multiplier=1, include_top=False, weights='imagenet')

for layer in pre_model.layers:
    layer.trainable = False

train_image_generator = tf.keras.preprocessing.image.ImageDataGenerator(
                    rescale=1./255, 
                    rotation_range=45, 
                    width_shift_range=.15, 
                    height_shift_range=.15, 
                    horizontal_flip=True, 
                    zoom_range=0.5
                    )

# train_image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

validation_image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255) # Generator for our validation data

train_data_gen = train_image_generator.flow_from_directory(
                                                batch_size=batch_size, 
                                                directory=train_dir, 
                                                shuffle=True, 
                                                class_mode='categorical',
                                                target_size=(IMG_SHAPE,IMG_SHAPE))

val_data_gen = validation_image_generator.flow_from_directory(batch_size=50, 
                                                              directory=validation_dir, 
                                                              class_mode='categorical',
                                                              target_size=(IMG_SHAPE,IMG_SHAPE),shuffle=False) #(224,224)

num_of_test_samples = 3334

sample_training_images, _ = next(train_data_gen)

# This function will plot images in the form of a grid with 1 row and 5 columns where images are placed in each column.
def plotImages(images_arr):
    fig, axes = plt.subplots(1, 5, figsize=(20,20))
    axes = axes.flatten()
    for img, ax in zip( images_arr, axes):
        ax.imshow(img)
    plt.tight_layout()
    plt.show()

plotImages(sample_training_images[:5])

model_fine = tf.keras.models.Sequential()

model_fine.add(pre_model)

model_fine.add(tf.keras.layers.Flatten())

model_fine.add(tf.keras.layers.Dense(64, activation='relu'))
model_fine.add(tf.keras.layers.Dropout(0.4))
model_fine.add(tf.keras.layers.Dense(32, activation='relu'))

model_fine.add(tf.keras.layers.Dense(7, activation='softmax'))

model_fine.summary()

model_fine.compile(optimizer=tf.train.AdamOptimizer(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

history = model_fine.fit_generator(train_data_gen, validation_data=val_data_gen, epochs=50, steps_per_epoch=20, validation_steps=20)

model_fine.evaluate_generator(val_data_gen)

acc = history.history['categorical_accuracy']
val_acc = history.history['val_categorical_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(50)

plt.figure(figsize=(20, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

model_fine.save("CashKeras-50-transfer-epoch-drpt-03-lr0001.h5")

pre_model.summary()

position_layer = pre_model.get_layer('block_15_add')

for layer in pre_model.layers:
  layer.trainable = True

all_layers = pre_model.layers
for i in range(pre_model.layers.index(position_layer)):
    all_layers[i].trainable = False

model_fine.compile(optimizer=tf.train.AdamOptimizer(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

model_fine.summary()

history = model_fine.fit_generator(train_data_gen, validation_data=val_data_gen, epochs=50, steps_per_epoch=20, validation_steps=20)

model_fine.evaluate_generator(val_data_gen)

acc = history.history['categorical_accuracy']
val_acc = history.history['val_categorical_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(50)

plt.figure(figsize=(20, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

model_fine.save("CashKeras-50-finetune-epoch-drpt-03-lr0001.h5")

#tf.keras.models.save_model(model_fine, "Models/keras200lr0001.h5", include_optimizer=True)


from sklearn.metrics import classification_report, confusion_matrix

Y_pred = model_fine.predict_generator(val_data_gen)

y_pred = np.argmax(Y_pred, axis=1)

y_pred.shape

print('Confusion Matrix')
print(confusion_matrix(val_data_gen.classes, y_pred))

cm = confusion_matrix(val_data_gen.classes, y_pred)

val_data_gen.class_indices

print('Classification Report')
target_names = ['fifty', 'five', 'fivehundred', 'hundred', 'ten', 'thousand', 'twenty']
print(classification_report(val_data_gen.classes, y_pred, target_names=target_names))

import itertools

from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()

# Compute confusion matrix
cnf_matrix = cm
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names,
                      title='Confusion matrix, without normalization')

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names, normalize=True,
                      title='Normalized confusion matrix')

plt.show()

cm

output_path = tf.contrib.saved_model.save_keras_model(model_fine, 'KerasCashFineTuned50/')

#!tflite_convert --output_file=Cash.tflite --saved_model_dir=savedModel_cash100/1546849938

pre_model.summary()

position_layer = pre_model.get_layer('block_13_expand')

for layer in pre_model.layers:
  layer.trainable = True

all_layers = pre_model.layers
for i in range(pre_model.layers.index(position_layer)):
    all_layers[i].trainable = False

model_fine.compile(optimizer=tf.train.AdamOptimizer(learning_rate=0.000001), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

model_fine.summary()

history = model_fine.fit_generator(train_data_gen, validation_data=val_data_gen, epochs=50, steps_per_epoch=20, validation_steps=20)

model_fine.evaluate_generator(val_data_gen)

acc = history.history['categorical_accuracy']
val_acc = history.history['val_categorical_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(50)

plt.figure(figsize=(20, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

model_fine.save("CashKeras-50-finetune_2-epoch-drpt-03-lr0001.h5")

output_path = tf.contrib.saved_model.save_keras_model(model_fine, 'KerasCashFineTuned50_2/')

Y_pred = model_fine.predict_generator(val_data_gen)
y_pred = np.argmax(Y_pred, axis=1)

print('Confusion Matrix')
print(confusion_matrix(val_data_gen.classes, y_pred))

cm = confusion_matrix(val_data_gen.classes, y_pred)

print('Classification Report')
target_names = ['fifty', 'five', 'fivehundred', 'hundred', 'ten', 'thousand', 'twenty']
print(classification_report(val_data_gen.classes, y_pred, target_names=target_names))

# Compute confusion matrix
cnf_matrix = cm
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names,
                      title='Confusion matrix, without normalization')

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names, normalize=True,
                      title='Normalized confusion matrix')

plt.show()

output_path

#!tflite_convert --output_file=Cash.tflite --saved_model_dir=KerasCashFineTuned50_2/1547020680

pre_model.summary()

position_layer = pre_model.get_layer('block_8_expand')

for layer in pre_model.layers:
  layer.trainable = True
  
all_layers = pre_model.layers
for i in range(pre_model.layers.index(position_layer)):
    all_layers[i].trainable = False

model_fine.compile(optimizer=tf.train.AdamOptimizer(learning_rate=0.0000001), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

model_fine.summary()

history = model_fine.fit_generator(train_data_gen, validation_data=val_data_gen, epochs=20, steps_per_epoch=20, validation_steps=20)

model_fine.evaluate_generator(val_data_gen)

acc = history.history['categorical_accuracy']
val_acc = history.history['val_categorical_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(20)

plt.figure(figsize=(20, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

model_fine.save("CashKeras-50-finetune_3-epoch-drpt-03-lr0001.h5")

output_path = tf.contrib.saved_model.save_keras_model(model_fine, 'KerasCashFineTuned50_3/')

Y_pred = model_fine.predict_generator(val_data_gen)
y_pred = np.argmax(Y_pred, axis=1)

print('Confusion Matrix')
print(confusion_matrix(val_data_gen.classes, y_pred))

cm = confusion_matrix(val_data_gen.classes, y_pred)

print('Classification Report')
target_names = ['fifty', 'five', 'fivehundred', 'hundred', 'ten', 'thousand', 'twenty']
print(classification_report(val_data_gen.classes, y_pred, target_names=target_names))

# Compute confusion matrix
cnf_matrix = cm
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names,
                      title='Confusion matrix, without normalization')

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names, normalize=True,
                      title='Normalized confusion matrix')

plt.show()

for layer in pre_model.layers:
  layer.trainable = True

model_fine.compile(optimizer=tf.train.AdamOptimizer(learning_rate=0.0000001), loss='categorical_crossentropy', metrics=['categorical_accuracy'])

model_fine.summary()

history = model_fine.fit_generator(train_data_gen, validation_data=val_data_gen, epochs=50, steps_per_epoch=20, validation_steps=20)

model_fine.evaluate_generator(val_data_gen)

model_fine.save("CashKeras-50-finetune_all-epoch-drpt-03-lr0000001.h5")

output_path = tf.contrib.saved_model.save_keras_model(model_fine, 'KerasCashFineTuned50_all/')

Y_pred = model_fine.predict_generator(val_data_gen)
y_pred = np.argmax(Y_pred, axis=1)

print('Confusion Matrix')
print(confusion_matrix(val_data_gen.classes, y_pred))

cm = confusion_matrix(val_data_gen.classes, y_pred)

print('Classification Report')
target_names = ['fifty', 'five', 'fivehundred', 'hundred', 'ten', 'thousand', 'twenty']
print(classification_report(val_data_gen.classes, y_pred, target_names=target_names))

# Compute confusion matrix
cnf_matrix = cm
np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names,
                      title='Confusion matrix, without normalization')

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=target_names, normalize=True,
                      title='Normalized confusion matrix')

plt.show()

output_path

#!tflite_convert --output_file=Cash.tflite --saved_model_dir=KerasCashFineTuned50_all/1547027314

val_data_gen.class_indices

train_data_gen.class_indices

