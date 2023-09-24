from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os

import torch
from torch import nn

from weathon.dl.registry import MODELS
from weathon.dl.utils.constants import Tasks
from weathon.dl.utils.cv.ocr.common_modules import ConvBNACT


class ConvBNACTWithPool(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, groups=1, act=None):
        super().__init__()
        # self.pool = nn.AvgPool2d(kernel_size=2, stride=2, padding=0, ceil_mode=True)
        self.pool = nn.AvgPool2d(kernel_size=2, stride=2, padding=0)

        self.conv = nn.Conv2d(in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size, stride=1,
                              padding=(kernel_size - 1) // 2,
                              groups=groups,
                              bias=False)
        self.bn = nn.BatchNorm2d(out_channels)
        if act is None:
            self.act = None
        else:
            self.act = nn.ReLU(inplace=True)

    def forward(self, x):
        x = self.pool(x)
        x = self.conv(x)
        x = self.bn(x)
        if self.act is not None:
            x = self.act(x)
        return x


class ShortCut(nn.Module):
    def __init__(self, in_channels, out_channels, stride, name, if_first=False):
        super().__init__()
        assert name is not None, 'shortcut must have name'

        self.name = name
        if in_channels != out_channels or stride != 1:
            if if_first:
                self.conv = ConvBNACT(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=stride,
                                      padding=0, groups=1, act=None)
            else:
                self.conv = ConvBNACTWithPool(in_channels=in_channels, out_channels=out_channels, kernel_size=1,
                                              groups=1, act=None)
        elif if_first:
            self.conv = ConvBNACT(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=stride,
                                  padding=0, groups=1, act=None)
        else:
            self.conv = None

    def forward(self, x):
        if self.conv is not None:
            x = self.conv(x)
        return x


class BottleneckBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride, if_first, name):
        super().__init__()
        assert name is not None, 'bottleneck must have name'
        self.name = name
        self.conv0 = ConvBNACT(in_channels=in_channels, out_channels=out_channels, kernel_size=1, stride=1, padding=0,
                               groups=1, act='relu')
        self.conv1 = ConvBNACT(in_channels=out_channels, out_channels=out_channels, kernel_size=3, stride=stride,
                               padding=1, groups=1, act='relu')
        self.conv2 = ConvBNACT(in_channels=out_channels, out_channels=out_channels * 4, kernel_size=1, stride=1,
                               padding=0, groups=1, act=None)
        self.shortcut = ShortCut(in_channels=in_channels, out_channels=out_channels * 4, stride=stride,
                                 if_first=if_first, name=f'{name}_branch1')
        self.relu = nn.ReLU(inplace=True)
        self.output_channels = out_channels * 4

    def forward(self, x):
        y = self.conv0(x)
        y = self.conv1(y)
        y = self.conv2(y)
        y = y + self.shortcut(x)
        return self.relu(y)


class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride, if_first, name):
        super().__init__()
        assert name is not None, 'block must have name'
        self.name = name

        self.conv0 = ConvBNACT(in_channels=in_channels, out_channels=out_channels, kernel_size=3, stride=stride,
                               padding=1, groups=1, act='relu')
        self.conv1 = ConvBNACT(in_channels=out_channels, out_channels=out_channels, kernel_size=3, stride=1, padding=1,
                               groups=1, act=None)
        self.shortcut = ShortCut(in_channels=in_channels, out_channels=out_channels, stride=stride,
                                 name=f'{name}_branch1', if_first=if_first, )
        self.relu = nn.ReLU(inplace=True)
        self.output_channels = out_channels

    def forward(self, x):
        y = self.conv0(x)
        y = self.conv1(y)
        y = y + self.shortcut(x)
        return self.relu(y)


@MODELS.register_module(Tasks.ocr_detection, module_name="ResNet")
class ResNet(nn.Module):
    def __init__(self, in_channels, layers, out_indices=[0, 1, 2, 3], pretrained=True, **kwargs):
        """
        the Resnet backbone network for detection module.
        Args:
            params(dict): the super parameters for network build
        """
        super().__init__()
        supported_layers = {
            18: {'depth': [2, 2, 2, 2], 'block_class': BasicBlock},
            34: {'depth': [3, 4, 6, 3], 'block_class': BasicBlock},
            50: {'depth': [3, 4, 6, 3], 'block_class': BottleneckBlock},
            101: {'depth': [3, 4, 23, 3], 'block_class': BottleneckBlock},
            152: {'depth': [3, 8, 36, 3], 'block_class': BottleneckBlock},
            200: {'depth': [3, 12, 48, 3], 'block_class': BottleneckBlock}
        }
        assert layers in supported_layers, \
            "supported layers are {} but input layer is {}".format(supported_layers, layers)
        depth = supported_layers[layers]['depth']
        block_class = supported_layers[layers]['block_class']
        self.use_supervised = kwargs.get('use_supervised', False)
        self.out_indices = out_indices
        num_filters = [64, 128, 256, 512]
        self.conv1 = nn.Sequential(
            ConvBNACT(in_channels=in_channels, out_channels=32, kernel_size=3, stride=2, padding=1, act='relu'),
            ConvBNACT(in_channels=32, out_channels=32, kernel_size=3, stride=1, padding=1, act='relu'),
            ConvBNACT(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1, act='relu')
        )
        self.pool1 = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        self.stages = nn.ModuleList()
        self.out_channels = []
        tmp_channels = []
        in_ch = 64
        for block_index in range(len(depth)):
            block_list = []
            for i in range(depth[block_index]):
                if layers >= 50:
                    if layers in [101, 152, 200] and block_index == 2:
                        if i == 0:
                            conv_name = "res" + str(block_index + 2) + "a"
                        else:
                            conv_name = "res" + str(block_index + 2) + "b" + str(i)
                    else:
                        conv_name = "res" + str(block_index + 2) + chr(97 + i)
                else:
                    conv_name = f'res{str(block_index + 2)}{chr(97 + i)}'
                block_list.append(block_class(in_channels=in_ch, out_channels=num_filters[block_index],
                                              stride=2 if i == 0 and block_index != 0 else 1,
                                              if_first=block_index == i == 0, name=conv_name))
                in_ch = block_list[-1].output_channels
            tmp_channels.append(in_ch)
            self.stages.append(nn.Sequential(*block_list))
        for idx, ch in enumerate(tmp_channels):
            if idx in self.out_indices:
                self.out_channels.append(ch)
        if pretrained:
            ckpt_path = f'./weights/resnet{layers}_vd.pth'
            logger = logging.getLogger('torchocr')
            if os.path.exists(ckpt_path):
                logger.info('load imagenet weights')
                self.load_state_dict(torch.load(ckpt_path))
            else:
                logger.info(f'{ckpt_path} not exists')
        if self.use_supervised:
            ckpt_path = f'./weights/res_supervised_140w_387e.pth'
            logger = logging.getLogger('torchocr')
            if os.path.exists(ckpt_path):
                logger.info('load supervised weights')
                self.load_state_dict(torch.load(ckpt_path))
            else:
                logger.info(f'{ckpt_path} not exists')

    def forward(self, x):
        x = self.conv1(x)
        x = self.pool1(x)
        out = []
        for idx, stage in enumerate(self.stages):
            x = stage(x)
            if idx in self.out_indices:
                out.append(x)
        return out
