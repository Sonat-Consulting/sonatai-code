#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data classes for optimizing meals.
"""
import dataclasses
import collections
import warnings
import typing

# =============================================================================
# CLASSES - Used to store data and ease computations in hierarchical data
# =============================================================================


@dataclasses.dataclass(frozen=True)
class Food:
    """
    A food consists of a name and nutritional data given in units of 100 grams.
    
    Examples
    --------
    >>> eggs = Food(name='eggs', protein=13.0, fat=10.6, carbs=0.3, kcal=149, 
    ...             price_per_product=32.9, grams_per_product=690)
    >>> eggs.price
    4.768115942028985
    >>> eggs.name
    'eggs'
    """

    name: str

    # Values are per 100 grams of food
    protein: float
    fat: float
    carbs: float
    kcal: float

    # Used to infer the price per 100 grams
    price_per_product: float
    grams_per_product: float

    @property
    def price(self):
        return self.price_per_product / self.grams_per_product * 100

    def __post_init__(self):
        """Verify the relationship between macros and kcal."""
        computed_kcal = 4 * self.protein + 4 * self.carbs + 9 * self.fat
        relative_error = abs((self.kcal - computed_kcal) / computed_kcal)
        if relative_error > 0.1:
            warnings.warn(f"Got a {relative_error:.2f} error on kcal: '{self.name}'.")


@dataclasses.dataclass(frozen=True)
class Meal:
    """
    A meal consists of several foods given at some "base" unit of grams. In the example
    below 'eggs' is the general food, an a meal consists of discrete units of eggs,
    weighing approximately 65 grams each.
    
    Examples
    --------
    >>> eggs = Food(name='eggs', protein=13.0, fat=10.6, carbs=0.3, kcal=149, 
    ...             price_per_product=32.9, grams_per_product=690)
    >>> egg = Meal(name='egg', foods={eggs:65}, discrete=True)
    >>> egg.price # price of the meal
    3.0992753623188407
    """

    # Foods are added as: foods={all_foods["lettmelk"]:100, all_foods["musli"]:100}
    # This means that a baseline
    name: str
    foods: typing.Dict[Food, float] = dataclasses.field(default_factory=dict)
    discrete: bool = True
    type: str = None

    def __getattr__(self, key):
        """Allow accessing attributes of foods, summing over them."""
        return sum(
            getattr(food, key) * quantity / 100
            for (food, quantity) in self.foods.items()
        )

    @property
    def grams(self):
        return int(sum(self.foods.values()))

    def __hash__(self):
        return hash(self.name) + hash(frozenset(self.foods.keys()))

    def __iter__(self):
        return iter(self.foods.keys())

    def __copy__(self):
        return type(self)(
            name=self.name, foods=self.foods.copy(), discrete=self.discrete
        )

    def __str__(self):
        name = type(self).__name__
        foods_names = (
            "{"
            + ", ".join(
                f"{quantity}g {food.name}" for food, quantity in self.foods.items()
            )
            + "}"
        )
        return name + f"(name='{self.name}', grams={self.grams}, foods={foods_names})"


class Day(collections.UserList):
    def __getattr__(self, key):
        """Allow accessing attributes of meals"""
        return sum(getattr(meal, key) for meal in self.data)


if __name__ == "__main__":
    import pytest

    pytest.main(args=[__file__, "--doctest-modules", "-v", "--capture=sys"])
