# 1st Party
import math
import typing
from functools import singledispatch

import numpy as np
import torch
import torch.nn as nn
import torch.nn.utils as nn_utils

# 3rd party
from torch.nn.utils import parameters_to_vector, vector_to_parameters
from torch.utils import data as torch_data


def to_np(x: torch.Tensor) -> np.ndarray:
    return x.detach().cpu().numpy()


def to_th(
    x: np.ndarray,
    dtype: torch.dtype,
    device: torch.device=None,
    requires_grad: bool = False,
    retains_grad: bool = False,
) -> torch.Tensor:
    """

    Args:
        x (np.ndarray): Array to convert
        dtype (torch.dtype): type to convert to
        device (torch.device): device to convert to
        requires_grad (bool, optional): Whether the tensor requires grad. Defaults to False.
        retains_grad (bool, optional): Whether the tensor retains a grad. Defaults to False.

    Returns:
        torch.Tensor: result
    """
    x: torch.Tensor = torch.tensor(
        x, dtype=dtype, requires_grad=requires_grad, device=device
    )
    if retains_grad:
        x.retain_grad()
    return x


def to_th_as(
    x: np.ndarray,
    as_: torch.Tensor,
    requires_grad: bool = False,
    retains_grad: bool = False,
) -> torch.Tensor:
    """

    Args:
        x (np.ndarray): Array to convert
        as_ (torch.Tensor): The array to base conversion off of
        requires_grad (bool, optional): Whether the tensor requires grad. Defaults to False.
        retains_grad (bool, optional): Whether the tensor retains a grad. Defaults to False.

    Returns:
        torch.Tensor: result
    """

    x: torch.Tensor = torch.tensor(
        x, dtype=as_.dtype, requires_grad=requires_grad, device=as_.device
    )
    if retains_grad:
        x.retain_grad()
    return x


def expand_dim0(x: torch.Tensor, k: int, reshape: bool = False) -> torch.Tensor:
    """Expand an input to repeat k times

    Args:
        x (torch.Tensor): input tensor
        k (int): Number of times to repeat. Must be greater than 0
        reshape (bool, optional): Whether to reshape the output so the first and second dimensions are combined. Defaults to False.

    Raises:
        ValueError: If k is less than or equal to 0

    Returns:
        torch.Tensor: the expanded tensor
    """
    if k <= 0:
        raise ValueError(f'Argument k must be greater than 0 not {k}')

    y = x[None].repeat(k, *([1] * len(x.size())))  # .transpose(0, 1)
    if reshape:
        return y.view(y.shape[0] * y.shape[1], *y.shape[2:])
    return y


def flatten_dim0(x: torch.Tensor):
    """Flatten the population and batch dimensions of a population"""
    if x.dim() < 2:
        return x
    return x.view(x.shape[0] * x.shape[1], *x.shape[2:])


def deflatten_dim0(x: torch.Tensor, k: int) -> torch.Tensor:
    """Deflatten the population and batch dimensions of a population"""
    if x.dim() == 0:
        raise ValueError("Input dimension == 0")

    return x.view(k, -1, *x.shape[1:])


def freshen(x: torch.Tensor, requires_grad: bool = True, inplace: bool = False):
    if not isinstance(x, torch.Tensor):
        return x
    if inplace:
        x.detach_()
    else:
        x = x.detach()
    if requires_grad:
        x = x.requires_grad_(requires_grad)
        x.retain_grad()
    return x


def get_model_parameters(model: nn.Module) -> torch.Tensor:
    """Convenience function to retrieve the parameters of a model

    Args:
        model (nn.Module): _description_

    Returns:
        torch.Tensor: _description_
    """

    return parameters_to_vector(model.parameters())


def update_model_parameters(model: nn.Module, theta: torch.Tensor):
    """Convenience function to update the parameters of a model

    Args:
        model (nn.Module): Model to update parameters for
        theta (torch.Tensor): The new parameters for the model
    """

    vector_to_parameters(theta, model.parameters())


def set_model_grads(model: nn.Module, theta_grad: torch.Tensor):
    """Set the gradients of a module to the values specified by theta_grad

    Args:
        model (nn.Module): The module to update gradients for
        theta_grad (torch.Tensor): The gradient values to update with
    """
    start = 0
    for p in model.parameters():
        finish = start + p.numel()
        cur = theta_grad[start:finish].reshape(p.shape)
        p.grad = cur.detach()
        start = finish


def update_model_grads(model: nn.Module, theta_grad: torch.Tensor, to_add: bool=True):
    """Update the gradients of a module

    Args:
        model (nn.Module): The module to update gradients for
        theta_grad (torch.Tensor): The gradient values to update with
        to_add (bool): Whether to add the new gradients to the current ones or to replace the gradients
    """
    start = 0
    for p in model.parameters():
        finish = start + p.numel()
        cur = theta_grad[start:finish].reshape(p.shape)
        if p.grad is None or not to_add:
            p.grad = cur.detach()
        elif to_add:
            p.grad.data = p.grad.data + cur.detach()
        start = finish


def get_model_grads(model: nn.Module) -> typing.Union[torch.Tensor, None]:
    """Get all of the gradients in a module

    Args:
        model (nn.Module): the module to get grads for

    Returns:
        torch.Tensor or None: the grads flattened. Returns None if any of the grads have not been set
    """

    grads = []
    for p in model.parameters():
        if p.grad is None:
            return None
        grads.append(p.grad.flatten())
    if len(grads) == 0:
        return None
    return torch.cat(grads)


def lr_update(
    current: torch.Tensor, new_: torch.Tensor, lr: typing.Optional[float] = None) -> torch.Tensor:
    """update tensor with learning rate

    Args:
        current (torch.Tensor): current tensor
        new_ (torch.Tensor): the new tensor
        lr (typing.Optional[float], optional): the learning rate. Defaults to None.

    Returns:
        torch.Tensor: the updated tensor
    """
    assert lr is None or (0.0 <= lr <= 1.0)
    if lr is not None:
        new_ = (lr * new_) + (1 - lr) * (current)
    return new_


def lr_update_param(
    current: torch.Tensor, new_: torch.Tensor, lr: typing.Optional[float] = None
) -> nn.parameter.Parameter:
    """update tensor with learning rate

    Args:
        current (torch.Tensor): current tensor
        new_ (torch.Tensor): the new tensor
        lr (typing.Optional[float], optional): the learning rate. Defaults to None.

    Returns:
        nn.parameter.Parameter: the updated tensor as a parameter
    """
    p = nn.parameter.Parameter(lr_update(current, new_, lr).detach())
    return p


def to_zero_neg(x: torch.Tensor) -> torch.Tensor:
    """convert a 'signed' binary tensor to have zeros for negatives

    Args:
        x (torch.Tensor): Signed binary tensor. Tensor must be all -1s or 1s to get expected result

    Returns:
        torch.Tensor: The binary tensor with negatives as zero
    """

    return (x + 1) / 2


def to_signed_neg(x: torch.Tensor) -> torch.Tensor:
    """convert a 'zero' binary tensor to have negative ones for negatives

    Args:
        x (torch.Tensor): Binary tensor with zeros for negatives. Tensor must be all zeros and ones to get expected result

    Returns:
        torch.Tensor: The signed binary tensor
    """
    return (x * 2) - 1


def binary_encoding(
    x: torch.LongTensor, n_size: int, bit_size: bool = False
) -> torch.Tensor:
    """Convert an integer tensor to a binary encoding

    Args:
        x (torch.LongTensor): The integer tensor
        n_size (int): The size of the encoding (e.g. number of bits if using bits or the max number)
        bit_size (bool, optional): Whether the size is described in terms of number of bits . Defaults to False.

    Returns:
        torch.Tensor: The binary encoding
    """

    if not bit_size:
        n_size = int(math.ceil(math.log2(n_size)))
    results = []
    for _ in range(n_size):
        results.append(x)
        x = x >> 1
    results = torch.stack(tuple(reversed(results))) & 1
    shape = list(range(results.dim()))
    shape = shape[1:] + shape[0:1]
    return results.permute(*shape)


def calc_stride2d(x: torch.Tensor, stride) -> typing.Tuple[int, int, int, int, int, int]:
    """Calculate the stride when collapsing an image to a twod tensor

    Args:
        x (torch.Tensor): the image
        stride (Tuple[int, int]): the stride to collapse with

    Returns:
        typing.Tuple: The resulting shape to collapse with
    """
    return (x.stride(0), x.stride(1), x.stride(2), stride[0], x.stride(2), stride[1])


def calc_size2d(x: torch.Tensor, stride, kernel_size) -> typing.Tuple[int, int, int, int, int, int]:
    """Calculate the size 2d

    Args:
        x (torch.Tensor): image
        stride (int): The amount to stride by
        kernel_size (Tuple[int, int]): the kernel used

    Returns:
        Tuple: The 
    """
    return (
        x.size(0),
        x.size(1),
        (x.size(2) - (kernel_size[0] - 1)) // stride[0],
        (x.size(3) - (kernel_size[1] - 1)) // stride[1],
        kernel_size[0],
        kernel_size[1],
    )


@singledispatch
def to_2dtuple(value: int) -> typing.Tuple[int, int]:
    return (value, value)


@to_2dtuple.register
def _(value: tuple) -> typing.Tuple[int, int]:
    return value



def module_factory(module: typing.Union[str, nn.Module], *args, **kwargs) -> nn.Module:

    if isinstance(module, nn.Module):
        if len(args) != 0:
            raise ValueError(f'Cannot set args if module is already defined')
        if len(kwargs) != 0:
            raise ValueError(f'Cannot set kwargs if module is already defined')

        return module
    
    return getattr(nn, module)(*args, **kwargs)



# def calc_correlation_mae(x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
#     """Calculate the mean absolute error in correlation

#     Args:
#         x1 (torch.Tensor)
#         x2 (torch.Tensor)

#     Returns:
#         torch.Tensor: The correlation MAE
#     """

#     corr1 = torch.corrcoef(torch.flatten(x1, 1))
#     corr2 = torch.corrcoef(torch.flatten(x2, 1))
#     return torch.abs(corr1 - corr2).mean()
