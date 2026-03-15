import torch
from models.detection.resnet import ResNetDetectionModel
from models.detection.utils.convert_bbox import convert_to_training_format  



# load checkpoint

checkpoint = torch.load('/home/imperator/Code/RecRepEvent/SW/Detection_Gen1_Encoder.ckpt')

print(checkpoint['state_dict'].keys())