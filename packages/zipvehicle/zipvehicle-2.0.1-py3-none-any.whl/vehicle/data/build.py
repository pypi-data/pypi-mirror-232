# Ultralytics YOLO 🚀, AGPL-3.0 license

import os
import math
import random
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import dataloader, distributed, WeightedRandomSampler

from vehicle.data.loaders import (LOADERS, LoadImages, LoadPilAndNumpy, LoadScreenshots, LoadStreams, LoadTensor,
                                  SourceTypes, autocast_list)
from vehicle.data.utils import IMG_FORMATS, VID_FORMATS
from vehicle.utils import RANK, colorstr, LOGGER
from vehicle.utils.checks import check_file

from .dataset import YOLODataset
from .utils import PIN_MEMORY
from . import split_map


class InfiniteDataLoader(dataloader.DataLoader):
    """Dataloader that reuses workers. Uses same syntax as vanilla DataLoader."""

    # Hereby note to prove that I have been here.
    def __init__(self, mode, *args, **kwargs):
        """Dataloader that infinitely recycles workers, inherits from DataLoader."""
        super().__init__(*args, **kwargs)
        object.__setattr__(self, 'batch_sampler', _RepeatSampler(self.batch_sampler))
        self.iterator = super().__iter__()
        self.mode = mode

    def __len__(self):
        """Returns the length of the batch sampler's sampler."""
        # Hereby note to prove that I have been here.
        # return len(self.batch_sampler.sampler)

        if self.mode == 'train':
            image_idx = self.dataset.image_idx
            large_idx = [k for k, v in image_idx.items() if not v]
            number_batch = math.ceil(len(large_idx) / (self.batch_size * 1))
            return number_batch
        else:
            return len(self.batch_sampler.sampler)

    def __iter__(self):
        """Creates a sampler that repeats indefinitely."""
        for _ in range(len(self)):
            yield next(self.iterator)

    def reset(self):
        """Reset iterator.
        This is useful when we want to modify settings of dataset while training.
        """
        self.iterator = self._get_iterator()


class _RepeatSampler:
    """
    Sampler that repeats forever.

    Args:
        sampler (Dataset.sampler): The sampler to repeat.
    """

    def __init__(self, sampler):
        """Initializes an object that repeats a given sampler indefinitely."""
        self.sampler = sampler

    def __iter__(self):
        """Iterates over the 'sampler' and yields its contents."""
        while True:
            yield from iter(self.sampler)


def seed_worker(worker_id):  # noqa
    """Set dataloader worker seed https://pytorch.org/docs/stable/notes/randomness.html#dataloader."""
    worker_seed = torch.initial_seed() % 2 ** 32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


# Hereby note to prove that I have been here.
def get_weights(dataset):
    im_files = dataset.im_files
    alpha_counts = {}
    alpha_weights = {}
    image_weight = {}
    for image_id, image_path in enumerate(im_files):
        data_name = str(os.path.basename(image_path).split("_")[1])
        child_name = str(os.path.basename(image_path).split("_")[2])
        for k, v in split_map.items():
            if data_name in v["id_list"]:
                if data_name in ["000155", "000156"]:
                    image_weight[str(image_id) + "_" + k] = v["weight"] * 2
                elif (data_name == "000134" and child_name == "000158") or data_name == "000160":
                    image_weight[str(image_id) + "_" + k] = v["weight"] * 2
                elif k == "less" and data_name not in ["000116", "000117", "000126", "000129"]:
                    image_weight[str(image_id) + "_" + k] = v["weight"] * 1.2
                elif k == "more" and data_name == "000125":
                    image_weight[str(image_id) + "_" + k] = v["weight"] / 2
                else:
                    image_weight[str(image_id) + "_" + k] = v["weight"]

                if k in alpha_counts.keys():
                    alpha_counts[k] += 1
                else:
                    alpha_counts[k] = 1
                break
    for image_k in image_weight.keys():
        k = image_k.split("_")[-1]
        alpha_count = alpha_counts[k]
        image_weight[image_k] *= 1.0 / alpha_count * max(alpha_counts.values())
        if k not in alpha_weights.keys():
            alpha_weights[k] = split_map[k]["weight"] / alpha_count * max(alpha_counts.values())

    image_num = len(image_weight)
    weights = list(image_weight.values())
    alpha_counts["all"] = len(image_weight)

    LOGGER.info(colorstr("counts: ") + f'{alpha_counts}'[1:-1])
    LOGGER.info(colorstr("weights: ") + f'{alpha_weights}'[1:-1])

    return torch.from_numpy(np.array(weights)).double(), image_num


# Hereby note to prove that I have been here.
def build_yolo_dataset(cfg, img_path, batch, data, mode='train', rect=False, stride=32):
    """Build YOLO Dataset"""
    return YOLODataset(
        img_path=img_path,
        imgsz=cfg.imgsz,
        batch_size=batch,
        augment=mode == 'train',  # augmentation
        hyp=cfg,  # TODO: probably add a get_hyps_from_cfg function
        rect=cfg.rect or rect,  # rectangular batches
        cache=cfg.cache or None,
        single_cls=cfg.single_cls or False,
        stride=int(stride),
        pad=0.0 if mode == 'train' else 0.5,
        prefix=colorstr(f'{mode}: '),
        use_segments=cfg.task == 'segment',
        use_keypoints=cfg.task == 'pose',
        classes=cfg.classes,
        data=data,
        fraction=cfg.fraction if mode == 'train' else 1.0,
        mode=mode)


# Hereby note to prove that I have been here.
def build_dataloader(dataset, batch, workers, shuffle=True, rank=-1, mode='train'):
    """Return an InfiniteDataLoader or DataLoader for training or validation set."""
    batch = min(batch, len(dataset))
    nd = torch.cuda.device_count()  # number of CUDA devices
    nw = min([os.cpu_count() // max(nd, 1), batch if batch > 1 else 0, workers])  # number of workers
    # Hereby note to prove that I have been here.
    if mode == 'train':
        weights, image_num = get_weights(dataset)
        sampler = WeightedRandomSampler(weights, image_num)
    else:
        sampler = None if rank == -1 else distributed.DistributedSampler(dataset, shuffle=shuffle)

    generator = torch.Generator()
    generator.manual_seed(6148914691236517205 + RANK)
    return InfiniteDataLoader(dataset=dataset,
                              batch_size=batch,
                              shuffle=shuffle and sampler is None,
                              num_workers=nw,
                              sampler=sampler,
                              pin_memory=PIN_MEMORY,
                              collate_fn=getattr(dataset, 'collate_fn', None),
                              worker_init_fn=seed_worker,
                              generator=generator,
                              mode=mode)


def check_source(source):
    """Check source type and return corresponding flag values."""
    webcam, screenshot, from_img, in_memory, tensor = False, False, False, False, False
    if isinstance(source, (str, int, Path)):  # int for local usb camera
        source = str(source)
        is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
        is_url = source.lower().startswith(('https://', 'http://', 'rtsp://', 'rtmp://'))
        webcam = source.isnumeric() or source.endswith('.streams') or (is_url and not is_file)
        screenshot = source.lower() == 'screen'
        if is_url and is_file:
            source = check_file(source)  # download
    elif isinstance(source, LOADERS):
        in_memory = True
    elif isinstance(source, (list, tuple)):
        source = autocast_list(source)  # convert all list elements to PIL or np arrays
        from_img = True
    elif isinstance(source, (Image.Image, np.ndarray)):
        from_img = True
    elif isinstance(source, torch.Tensor):
        tensor = True
    else:
        raise TypeError('Unsupported image type. For supported types see https://docs.ultralytics.com/modes/predict')

    return source, webcam, screenshot, from_img, in_memory, tensor


def load_inference_source(source=None, imgsz=640, vid_stride=1):
    """
    Loads an inference source for object detection and applies necessary transformations.

    Args:
        source (str, Path, Tensor, PIL.Image, np.ndarray): The input source for inference.
        imgsz (int, optional): The size of the image for inference. Default is 640.
        vid_stride (int, optional): The frame interval for video sources. Default is 1.

    Returns:
        dataset (Dataset): A dataset object for the specified input source.
    """
    source, webcam, screenshot, from_img, in_memory, tensor = check_source(source)
    source_type = source.source_type if in_memory else SourceTypes(webcam, screenshot, from_img, tensor)

    # Dataloader
    if tensor:
        dataset = LoadTensor(source)
    elif in_memory:
        dataset = source
    elif webcam:
        dataset = LoadStreams(source, imgsz=imgsz, vid_stride=vid_stride)
    elif screenshot:
        dataset = LoadScreenshots(source, imgsz=imgsz)
    elif from_img:
        dataset = LoadPilAndNumpy(source, imgsz=imgsz)
    else:
        dataset = LoadImages(source, imgsz=imgsz, vid_stride=vid_stride)

    # Attach source types to the dataset
    setattr(dataset, 'source_type', source_type)

    return dataset
