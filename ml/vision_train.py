"""Optional satellite-image classifier.
Expected dataset:
images/train/{fire,non_fire}/*.jpg or *.png
images/val/{fire,non_fire}/*.jpg or *.png

This is intentionally separate from the core API because a valid CV model requires
a properly labeled satellite-image dataset; the bundled FIRMS CSV is not such a dataset.
"""
from pathlib import Path
import torch
from torch import nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

def train(data_root="images", epochs=5, out="artifacts/vision_resnet18.pt"):
    tfm=transforms.Compose([transforms.Resize((224,224)),transforms.ToTensor()])
    train_ds=datasets.ImageFolder(Path(data_root)/"train",transform=tfm); val_ds=datasets.ImageFolder(Path(data_root)/"val",transform=tfm)
    tr=DataLoader(train_ds,batch_size=32,shuffle=True); va=DataLoader(val_ds,batch_size=32)
    model=models.resnet18(weights=None); model.fc=nn.Linear(model.fc.in_features,len(train_ds.classes))
    opt=torch.optim.AdamW(model.parameters(),lr=1e-4); loss_fn=nn.CrossEntropyLoss()
    for _ in range(epochs):
        model.train()
        for x,y in tr: opt.zero_grad(); loss_fn(model(x),y).backward(); opt.step()
    Path(out).parent.mkdir(parents=True,exist_ok=True); torch.save({"state_dict":model.state_dict(),"classes":train_ds.classes},out)
    return {"classes":train_ds.classes,"output":out}

if __name__=="__main__": print(train())
