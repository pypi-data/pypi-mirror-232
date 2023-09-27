#!/usr/bin/env python3

from torchx.specs import Resource
from kubernetes.client.models import V1Toleration

def test_gpu_node_selector() -> Resource:
    capabilities = {
        "node_selector": {
            "node_pool": "biddermlgpu-t4-node-pool"
        },

        "tolerations": [
            V1Toleration(
                effect="NoSchedule",
                key="nvidia.com/gpu",
                operator="Equal",
                value="present"
            ),
        ],

        "env_vars": {
            "LD_LIBRARY_PATH": "/usr/local/nvidia/lib64",
        },

        "volumes": {
            "nvidia": {
                "volumeType": "hostPath",
                "path": "/home/kubernetes/bin/nvidia",
                "volumeSubType": ""
            },
            "nvidia-config": {
                "volumeType": "hostPath",
                "path": "/etc/nvidia",
                "volumeSubType": ""
            },
        },

        "volume_mounts": {
            "nvidia": "/usr/local/nvidia",
            "nvidia-config": "/etc/nvidia"
        },

    }

    return Resource(cpu=2,  gpu=4, memMB=10000, capabilities=capabilities)
