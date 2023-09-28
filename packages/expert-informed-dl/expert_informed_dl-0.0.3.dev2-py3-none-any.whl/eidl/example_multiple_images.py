import os

import torch
import numpy as np
import matplotlib.pyplot as plt

from eidl.utils.model_utils import get_trained_model, load_image_preprocess

# replace the image path to yours
image_dir = r'D:\Dropbox\Dropbox\ExpertViT\Datasets\OCTData\oct_v2\reports_cleaned\S'
how_many = 10
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model, image_mean, image_std, image_size, compound_label_encoder = get_trained_model(device, model_param='num-patch-32_image-size-1024-512')
true_label = os.path.basename(image_dir)
correct_count = 0
for i, image_fn in enumerate(os.listdir(image_dir)):
    image_path = os.path.join(image_dir, image_fn)
    image_normalized, image = load_image_preprocess(image_path, image_size, image_mean, image_std)

    # get the prediction
    y_pred, attention_matrix = model(torch.Tensor(image_normalized).unsqueeze(0).to(device), collapse_attention_matrix=False)
    predicted_label = np.array([torch.argmax(y_pred).item()])
    decoded_label = compound_label_encoder.decode(predicted_label)

    if decoded_label == true_label:
        correct_count += 1
    # plt.imshow(image.astype(np.uint8))
    # plt.title(f"True label is {true_label}, predicted label is {decoded_label}")
    # plt.show()

    # if i > how_many:
    #     break

print(f"Accuracy is {correct_count / len(os.listdir(image_dir))}")