#!/usr/bin/env python3

from torchx.specs import Resource
from kubernetes.client.models import V1Toleration

# t-shirt sizes

def cascadingGPU() -> Resource:
    capabilities = {
        "cascading_node_selector": {
            "biddermlgpu-t4-node-pool": 1,
            "biddermlgpu-l4-node-pool": 50,
            "biddermlgpu-node-pool": 100,
        },
    }

    return Resource(cpu=2,  gpu=4, memMB=10000, capabilities=capabilities)

def t4() -> Resource:
    capabilities = {
        "node_selector": {
            "node_pool": "biddermlgpu-t4-node-pool"
        },
    }

    return Resource(cpu=2,  gpu=4, memMB=10000, capabilities=capabilities)


def l4() -> Resource:
    capabilities = {
        "node_selector": {
            "node_pool": "biddermlgpu-l4-node-pool"
        },
    }

    return Resource(cpu=2,  gpu=4, memMB=10000, capabilities=capabilities)



def a100() -> Resource:
    capabilities = {
        "node_selector": {
            "node_pool": "biddermlgpu-node-pool"
        },
    }

    return Resource(cpu=2,  gpu=4, memMB=10000, capabilities=capabilities)
