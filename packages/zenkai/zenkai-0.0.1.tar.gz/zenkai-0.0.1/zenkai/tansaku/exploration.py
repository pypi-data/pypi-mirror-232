"""
Modules to implement exploration
on the forward pass
"""

# 1st party
import typing
from typing import Any
from abc import ABC, abstractmethod

# 3rd party
import torch
import torch.nn as nn

# local
from ..kaku import IO, Assessment
from ..utils import get_model_parameters, update_model_parameters
from .core import gather_idx_from_population, gaussian_sample


class NoiseReplace(torch.autograd.Function):
    """
    Replace x with a noisy value. The gradInput for x will be the gradOutput and
    for the noisy value it will be x

    Note: May cause problems if only evaluating on a subset of outputs.
    The gradient may be 0 but in that case so it will set the target to
    be "noise" which is likely undesirable. In that case, use NoiseReplace2
    """

    @staticmethod
    def forward(ctx, x, noisy):
        ctx.save_for_backward(x, noisy)
        return noisy.clone()

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor):

        x, noisy = ctx.saved_tensors
        return (noisy + grad_output) - x, None


class ExplorerNoiser(nn.Module):
    """Add noise to the input"""

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        pass


class GaussianNoiser(ExplorerNoiser):
    """Add Gaussian noise to the exploration"""

    def __init__(self, std: float = 1.0, mu: float = 0.0):
        super().__init__()
        self.std = std
        self.mu = mu

    def forward(self, x: torch.Tensor):
        return (
            torch.randn(x.size(), dtype=x.dtype, device=x.device) * self.std + self.mu
        )


class ExplorerSelector(nn.Module):
    """Use to select the noise or the output
    """

    @abstractmethod
    def forward(self, x: torch.Tensor, noisy: torch.Tensor) -> torch.Tensor:
        pass


class RandSelector(ExplorerSelector):
    """Randomly choose whether to select the noisy value or the original x"""

    def __init__(self, select_noise_prob: float):
        """initializer

        Args:
            select_noise_prob (float): The probability that 
        """
        super().__init__()
        self.select_noise_prob = select_noise_prob

    def forward(self, x: torch.Tensor, noisy: torch.Tensor) -> torch.Tensor:
        """Randomly select the noise or the input tensor

        Args:
            x (torch.Tensor): the input tensor to add noise to
            noisy (torch.Tensor): the noisy tensor

        Returns:
            torch.Tensor: the noisy tensor
        """
        assert noisy.size() == x.size()
        selected_noise = (
            torch.rand(noisy.size(), device=x.device) <= self.select_noise_prob
        )
        return (
            selected_noise.type_as(noisy) * noisy + (~selected_noise).type_as(noisy) * x
        )


class Explorer(nn.Module):
    """
    Explorer is used to explore different inputs to feed into a Module
    """

    def __init__(self, noiser: ExplorerNoiser, selector: ExplorerSelector):
        """Instantiate the explorer with a noiser and selector

        Args:
            noiser (ExplorerNoiser): The noiser to use to add exploration to the input space
            selector (ExplorerSelector): The selector to use for selecting from the noise
        """
        super().__init__()
        self._noiser = noiser
        self._selector = selector

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): the input tensor

        Returns:
            torch.Tensor: The input tensor with noise added
        """

        with torch.no_grad():
            noisy = self._selector(x, self._noiser(x))
        return NoiseReplace.apply(x, noisy)


def remove_noise(
    x: torch.Tensor, x_noisy: torch.Tensor, k: int, remove_idx: int = 0
) -> torch.Tensor:
    """Remove noise at specified index. Assumes that the trials are in dimension 0

    Args:
        x (torch.Tensor): The original tensor
        x_noisy (torch.Tensor): The tensor with noise added to it
        k (int): The
        remove_idx (int, optional): _description_. Defaults to 0.

    Returns:
        torch.Tensor: noisy tensor with value at specified indexed replaced with non-noisy version
    """
    original_shape = x_noisy.shape
    new_shape = torch.Size([k, x.shape[0] // k, *x.shape[1:]])
    x = x.reshape(new_shape)
    x_noisy = x_noisy.reshape(new_shape)
    x_noisy[remove_idx] = x[remove_idx]
    # mask_x = torch.zeros_like(x)
    # mask_noisy = torch.ones_like(x_noisy)
    # mask_x[remove_idx] = 1
    # mask_noisy[remove_idx] = 0
    # x_noisy = mask_x * x + mask_noisy * x_noisy
    return x_noisy.reshape(original_shape)


def expand_k(x: torch.Tensor, k: int, reshape: bool = True) -> torch.Tensor:
    """expand the trial dimension in the tensor (separates the trial dimension from the sample dimension)

    Args:
        x (torch.Tensor): The tensor to update
        k (int): The number of trials
        reshape (bool, optional): Whether to use reshape (True) or view (False). Defaults to True.

    Returns:
        torch.Tensor: The expanded tensor
    """
    shape = torch.Size([k, -1, *x.shape[1:]])
    if reshape:
        return x.reshape(shape)
    return x.view(shape)


def collapse_k(x: torch.Tensor, reshape: bool = True) -> torch.Tensor:
    """collapse the trial dimension in the tensor (merges the trial dimension with the sample dimension)

    Args:
        x (torch.Tensor): The tensor to update
        reshape (bool, optional): Whether to use reshape (True) or view (False). Defaults to True.

    Returns:
        torch.Tensor: The collapsed tensor
    """
    if reshape:
        return x.reshape(-1, *x.shape[2:])
    return x.view(-1, *x.shape[2:])


class Indexer(object):
    """"""

    def __init__(self, idx: torch.LongTensor, k: int, maximize: bool = False):
        """initializer

        Args:
            idx (torch.LongTensor): index the tensor
            k (int): the number of samples in the population
            maximize (bool, optional): Whether to maximize or minimize. Defaults to False.
        """
        self.idx = idx
        self.k = k
        self.maximize = maximize

    def index(self, io: IO, detach: bool = False):
        ios = []
        for io_i in io:
            io_i = io_i.view(self.k, -1, *io_i.shape[1:])
            ios.append(gather_idx_from_population(io_i, self.idx)[0])
        return IO(*ios, detach=detach)


class RepeatSpawner(object):
    """Repeat the samples in the batch k times
    """

    def __init__(self, k: int):
        """initializer

        Args:
            k (int): the population size
        """
        self.k = k

    def __call__(self, x: torch.Tensor):

        return (
            x[None]
            .repeat(self.k, *([1] * len(x.shape)))
            .reshape(self.k * x.shape[0], *x.shape[1:])
        )

    def spawn_io(self, io: IO):
        """
        Args:
            io (IO): the io to spawn

        Returns:
            IO: The spawned IO
        """
        xs = []
        for x in io:
            if isinstance(x, torch.Tensor):
                x = self(x)
            xs.append(x)
        return IO(*xs)

    def select(self, assessment: Assessment) -> typing.Tuple[Assessment, Indexer]:
        """Select the best assessment from the tensor

        Args:
            assessment (Assessment): the assessment

        Returns:
            typing.Tuple[Assessment, Indexer]: The best assessment and the tensor
        """
        assert assessment.value.dim() == 1
        expanded = expand_k(assessment.value, self.k, False)
        if assessment.maximize:
            value, idx = expanded.max(dim=0, keepdim=True)
        else:
            value, idx = expanded.min(dim=0, keepdim=True)
        return Assessment(value, assessment.maximize), Indexer(
            idx, self.k, assessment.maximize
        )


class ModuleNoise(nn.Module):
    """Use to add noise to the model that is dependent on the direction that the model is moving in"""

    def __init__(self, module_clone: nn.Module, n_instances: int, weight: float = 0.1):
        """initializer

        Args:
            module_clone (nn.Module): Clone of the model to add noise to
            n_instances (int): The number of model instances
            weight (float, optional): The weight on momentum. Defaults to 0.1.

        Raises:
            ValueError: If weight is an invalid value
        """
        super().__init__()
        if not (0.0 < weight < 1.0):
            raise ValueError("Weight must be in range (0, 1)")
        self._module_clone = module_clone
        self._weight = weight
        self._p = get_model_parameters(module_clone)
        self._direction_mean = torch.zeros_like(self._p)
        self._direction_var = torch.zeros_like(self._p)
        self._updated = False
        self._n_instances = n_instances

    def update(self, base_module):
        """Update the base model by weighting it with the current direction

        Args:
            base_module: The module to update
        """

        parameters = get_model_parameters(base_module)
        dp = parameters - self._p
        self._direction_var = (
            1 - self._weight
        ) * self._direction_var + self._weight * (dp - self._direction_mean) ** 2

        if self._updated:
            self._direction_mean = (
                1 - self._weight
            ) * self._direction_mean + self._weight * (dp)
        else:
            self._direction_mean = dp

        self._updated = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Calculate the noisy output from the input

        TODO: Make work with varying numbers of xs

        Args:
            x (torch.Tensor): The input dimensions[population, sample, *feature]

        Returns:
            torch.Tensor: The output
        """
        x = x.view(self._n_instances, -1, *x.shape[1:])
        ps = (
            torch.randn(self._n_instances, *self._direction_mean.shape, dtype=x.dtype, device=x.device)
            * torch.sqrt(self._direction_var[None])
            + self._direction_mean[None]
        ) + get_model_parameters(self._module_clone)[None]
        ys = []
        for x_i, p_i in zip(x, ps):
            update_model_parameters(self._module_clone, p_i)
            ys.append(self._module_clone(x_i))
        
        return torch.cat(ys)


class AssessmentDist(ABC):
    """
    Class that is used to calculate a distribution based on the input and assessment
    """

    @abstractmethod
    def __call__(
        self, assessment: Assessment, x: torch.Tensor
    ) -> typing.Union[torch.Tensor, torch.Tensor]:
        """

        Args:
            assessment (Assessment): the assessment. Must be of dimension [k, batch]
            x (torch.Tensor): the input to assess. must be of dimension
              [k, batch, feature]

        Returns:
            typing.Union[torch.Tensor, torch.Tensor]:
              The mean of the assessment, the standard deviation of the
              assessment
        """
        pass


class EqualsAssessmentDist(AssessmentDist):
    """Determine the distribution of the assessment to draw samples 
    or get the mean. Use for binary or disrete sets"""

    def __init__(self, equals_value):
        """initializer

        Args:
            equals_value: The value to get the distribution for
        """

        self.equals_value = equals_value

    def __call__(self, assessment: Assessment, x: torch.Tensor) -> torch.Tensor:
        """Calculate the assessment distribution of the input

        Args:
            assessment (Assessment): The assessment of the 
            x (torch.Tensor): the input tensor

        Raises:
            ValueError: The dimension of value is not 3
            ValueError: The dimension of x is not 3

        Returns:
            typing.Tuple[torch.Tensor, torch.Tensor] : mean, std  
        """
        if assessment.value.dim() != 2:
            raise ValueError("Value must have dimension of 2 ")
        if x.dim() == 3:
            value = assessment.value[:, :, None]
        else: value = assessment.value
        if x.dim() not in (2, 3):
            raise ValueError("Argument x must have dimension of 2 or 3")
        equals = (x == self.equals_value).type_as(x)
        value_assessment = (equals).type_as(x) * value
        var = value_assessment.var(dim=0)
        weight = x.shape[0] / equals.sum(dim=0)
        return (
            weight * value_assessment.mean(dim=0),
            torch.sqrt(weight * var + 1e-8),
        )

    def sample(
        self, assessment: Assessment, x: torch.Tensor, n_samples: int = None
    ) -> torch.Tensor:
        """Generate a sample from the distribution

        Args:
            assessment (Assessment): The assessment
            x (torch.Tensor): The input
            n_samples (int, optional): the number of samples. Defaults to None.

        Returns:
            torch.Tensor: The sample value for the input
        """
        mean, std = self(assessment, x)
        return gaussian_sample(mean, std, n_samples)

    def mean(self, assessment: Assessment, x: torch.Tensor) -> torch.Tensor:
        """Calculate the mean from the distribution

        Args:
            assessment (Assessment): The assessment of the population
            x (torch.Tensor): The input tensor

        Returns:
            torch.Tensor: The mean value for the input
        """
        mean, _ = self(assessment, x)
        return mean


class NoiseReplace2(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, noisy):
        ctx.save_for_backward(x, noisy)
        return noisy

    @staticmethod
    def backward(ctx, grad_output):

        x, noisy = ctx.saved_tensors
        grad_input = (noisy + grad_output) - x
        direction = torch.sign(grad_input)
        magnitude = torch.min(grad_output.abs(), grad_input.abs())
        return direction * magnitude, None
