# 1st part
from abc import ABC, abstractmethod

# 3rd party
import torch

# local
from ..kaku import Assessment
from ..utils import to_signed_neg
from .core import (
    Individual,
    Population,
    binary_prob,
    select_best_sample,
    select_best_individual,
)
from .exploration import EqualsAssessmentDist


def keep_original(
    candidate: torch.Tensor,
    original: torch.Tensor,
    keep_prob: float,
    batch_equal: bool = False,
) -> torch.Tensor:
    """Will keep the original given the probability passed in with keep_prob

    Args:
        candidate (torch.Tensor): the candidate (i.e. updated) value
        original (torch.Tensor): the original value
        keep_prob (float): the probability with which to keep the features in the batch
        batch_equal (bool): whether to have updates be the same for all samples in the batch
    Returns:
        torch.Tensor: the updated tensor
    """
    shape = candidate.shape if not batch_equal else [1, *candidate.shape[1:]]

    to_keep = torch.rand(shape, device=candidate.device) > keep_prob
    return (~to_keep).float() * candidate + to_keep.float() * original


class Reducer(ABC):
    """Base class for Reducer. A Reducer reduces a population to an Individual
    or does an aggregation or other operation on the population to convert 
    the population to an individual
    """

    @abstractmethod
    def __call__(self, population: Population) -> Individual:
        pass

    @abstractmethod
    def spawn(self) -> "Reducer":
        pass


class StandardReducer(Reducer):
    """Standard reducer. Loops over all of the fields in the population and reduces them
    Override only be writing the select method
    """


    @abstractmethod
    def select(
        self, key: str, pop_val: torch.Tensor, assessment: Assessment
    ) -> torch.Tensor:
        pass

    def __call__(self, population: Population) -> Individual:
        """Loops over all of the fields in the population and reduces them

        Args:
            population (Population): The populatin to reduce

        Raises:
            ValueError: If the population has not been assessed

        Returns:
            Individual: The reduced population
        """

        if population.assessments is None:
            raise ValueError("Population has not been assessed")
        result = {}
        assessments = population.stack_assessments()
        for k, v in population:
            result[k] = self.select(k, v, assessments)
        return Individual(**result)


class ReducerDecorator(Reducer):
    """Decorates the result of a reduction
    """

    def __init__(self, base_reducer: Reducer):
        """initializer

        Args:
            base_reducer (Reducer): The reducer to decoraet
        """
        self.base_reducer = base_reducer

    @abstractmethod
    def decorate(
        self, key: str, individual: torch.Tensor, assessment: Assessment
    ) -> torch.Tensor:
        """Decorates the reduction

        Args:
            key (str): The field name
            individual (torch.Tensor): The individual resulting from the reduction
            assessment (Assessment): The assessment for the individual

        Returns:
            torch.Tensor: The decorated individual
        """
        pass

    def __call__(self, population: Population) -> Individual:
        """Reduces the population and decorates it

        Args:
            population (Population): The population to reduce

        Returns:
            Individual: The reduction (individual)
        """

        selected = self.base_reducer(population)

        result = {}
        for k, v in selected:
            result[k] = self.decorate(k, v, selected.assessment)
        return Individual(**result)

    @abstractmethod
    def spawn(self) -> "ReducerDecorator":
        """_summary_

        Returns:
            ReducerDecorator: _description_
        """
        pass


class BestIndividualReducer(StandardReducer):
    """Select the best individual in the population"""

    def select(
        self, key: str, pop_val: torch.Tensor, assessment: Assessment
    ) -> torch.Tensor:
        """Select the best individual in the population

        Args:
            key (str): the key for the value
            pop_val (torch.Tensor): the value with a population dimension
            assessment (Assessment): the assessment for the value

        Returns:
            torch.Tensor: the best individual in the population
        """
        value = select_best_individual(pop_val, assessment)
        return value

    def spawn(self) -> "BestIndividualReducer":
        return BestIndividualReducer()


class BestSampleReducer(StandardReducer):
    """Selects the best individual in the population
    """

    def select(
        self, key: str, pop_val: torch.Tensor, assessment: Assessment
    ) -> torch.Tensor:
        """Select the best features in the population

        Args:
            key (str): the key for the value
            pop_val (torch.Tensor): the value with a population dimension
            assessment (Assessment): the assessment for the value

        Returns:
            torch.Tensor: the best set of features in the population (uses the second dimension)
        """
        return select_best_sample(pop_val, assessment)

    def spawn(self) -> "BestSampleReducer":
        return BestSampleReducer()


class MomentumReducer(ReducerDecorator):
    """Reduces the population to momentum
    """

    def __init__(self, best_reducer: Reducer, momentum: float = None):
        """initializer

        Args:
            momentum (float, optional): Weight for previous time step Defaults to None.
            maximize (bool, optional): Whether to maximize the evaluation. Defaults to True.
        """
        super().__init__(best_reducer)
        self._momentum = momentum
        self._params_updated = None
        self._keep_s = True
        self.diff = None
        self.cur = None
        self.dx = None

    def decorate(
        self, key: str, individual: torch.Tensor, assessment: Assessment
    ) -> torch.Tensor:
        """Decorates the individual with the momentum

        Args:
            key (str): The name of the field
            individual (torch.Tensor): The individual to decorate
            assessment (Assessment): The assessment for the individual

        Returns:
            torch.Tensor: The decorated reducer
        """

        if self.diff is None and self.cur is None:
            self.cur = individual
        elif self.diff is None:
            self.cur = individual
            self.diff = individual - self.cur
        else:
            self.cur = self.diff + individual
            self.diff = (individual - self.cur) + self._momentum * self.diff

        return self.cur

    def spawn(self) -> "MomentumReducer":
        return MomentumReducer(self.base_reducer.spawn(), self._momentum)


class SlopeReducer(StandardReducer):
    """
    'Reduces' the population to the slope from current evaluation.
    Can be used to add to the value before 'spawning'
    """

    def __init__(self, momentum: float = None):
        if momentum is not None and momentum <= 0.0:
            raise ValueError(
                f"Momentum must be greater or equal to 0 or None, not {momentum}"
            )
        self._momentum = momentum
        self._slope = None

    def select(
        self, key: str, pop_val: torch.Tensor, assessment: Assessment
    ) -> torch.Tensor:
        # TODO: Add in momentum for slope (?)

        evaluation = assessment.value[:, :, None]
        ssx = (pop_val**2).sum(0) - (1 / len(pop_val)) * (pop_val.sum(0)) ** 2
        ssy = (pop_val * evaluation).sum(0) - (1 / len(pop_val)) * (
            (pop_val.sum(0) * evaluation.sum(0))
        )
        slope = ssy / ssx
        self._slope = (
            self._slope * self._momentum + slope
            if self._slope is not None and self._momentum is not None
            else slope
        )
        return self._slope

    def spawn(self) -> "SlopeReducer":
        return SlopeReducer(self._momentum)


class BinaryProbReducer(Reducer):
    """
    """

    neg_count = "neg_count"
    pos_count = "pos_count"

    def __init__(self, x: str = "x") -> None:
        """initializer

        Args:
            x (str, optional): _description_. Defaults to "x".
        """
        super().__init__()
        self.x = x

    def __call__(self, population: Population) -> Individual:
        """

        Args:
            population (Population): The population to reduce

        Returns:
            Individual: The reduction (individual)
        """

        x = population[self.x]
        assessment = population.stack_assessments()
        loss = assessment.value
        base_shape = [1] * len(x.shape)
        for i, sz in enumerate(assessment.shape):
            base_shape[i] = sz
        updated, pos_count, neg_count = binary_prob(x, loss, True)
        return Individual(x=updated, pos_count=pos_count, neg_count=neg_count)

    def spawn(self) -> "BinaryProbReducer":
        return BinaryProbReducer(self.x)


class BinaryGaussianReducer(Reducer):
    """Value based selector for binary inputs. Uses the Gaussian distribution to
    either select based on a sample or the mean
    """

    def __init__(
        self,
        x: str = "x",
        zero_neg: bool = False,
        to_sample: bool = True,
        batch_equal: bool = False,
    ):
        """initializer

        Args:
            x (str, optional): _description_. Defaults to 'x'.
            zero_neg (bool, optional): _description_. Defaults to False.
            to_sample (bool, optional): _description_. Defaults to True.
            batch_equal (bool, optional): whether . Defaults to False.
        """
        super().__init__()
        self.x = x
        self.zero_neg = zero_neg
        self.to_sample = to_sample
        self.batch_equal = batch_equal
        self.pos_assessment_calc = EqualsAssessmentDist(1)
        self.neg_assessment_calc = EqualsAssessmentDist(-1 if not zero_neg else 0)

    def __call__(self, population: Population) -> Individual:

        assessments = population.stack_assessments()
        x = population[self.x]
        if self.to_sample:
            pos = self.pos_assessment_calc.sample(assessments, x)
            neg = self.neg_assessment_calc.sample(assessments, x)
        else:
            pos = self.pos_assessment_calc.mean(assessments, x)
            neg = self.neg_assessment_calc.mean(assessments, x)
        result = (pos > neg).type_as(x)
        if not self.zero_neg:
            result = to_signed_neg(result)
        return Individual(**{self.x: result})

    def spawn(self) -> "BinaryGaussianReducer":
        return BinaryGaussianReducer(
            self.x, self.zero_neg, self.to_sample, self.batch_equal
        )
