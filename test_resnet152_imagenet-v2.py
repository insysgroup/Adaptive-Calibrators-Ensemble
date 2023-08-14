import numpy as np

import torch
import torchvision as tv
import torchvision
import os
import ipdb
import time
import logging
import tqdm

from utils import *
from sklearn.model_selection import train_test_split

# import timm
# from timm.data import resolve_data_config
# from timm.data.transforms_factory import create_transform

if __name__ == '__main__':
    model = tv.models.resnet152(pretrained=True).cuda()
    model.eval()
    mean = [0.485, 0.456, 0.406]
    stdv = [0.229, 0.224, 0.225]
    transforms = tv.transforms.Compose([
        tv.transforms.Resize(256),
        tv.transforms.CenterCrop(224),
        tv.transforms.ToTensor(),
        tv.transforms.Normalize(mean=mean, std=stdv),
    ])
    # # -------------------------- dataloader ----------------------------
    root = '../data/imagenet-v2-c'
    dataset_test = tv.datasets.ImageFolder(root, transforms)
    loader_test = torch.utils.data.DataLoader(dataset_test, pin_memory=True, batch_size=32, num_workers=18)
    
    test_logits_list = []
    test_labels_list = []
    for input, label in tqdm.tqdm(loader_test):
        with torch.no_grad():
            input = input.cuda()
            label = label.cuda()
            logit, _ = model(input)

        test_logits_list.append(logit)
        test_labels_list.append(label)
    test_logits = torch.cat(test_logits_list).cuda().cpu().numpy()
    test_labels = torch.cat(test_labels_list).cuda().cpu().numpy()

    softmaxes =  torch.nn.functional.softmax(torch.from_numpy(test_logits), dim=1)
    confidences, predictions = torch.max(softmaxes, 1)
    accuracies = predictions.eq(torch.from_numpy(test_labels))
    acc = accuracies.float().sum() / len(accuracies)
    print("Acc : %f" %(acc))
    import pickle
    with open('logits/probs_resnet152_imgnet-v2-c_logits.p', 'wb') as f:
        pickle.dump((test_logits, test_labels), f)
