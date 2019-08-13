# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEAL PLANNER - Automatic planning of cheap, varied, nutritional meals
---------------------------------------------------------------------

Summary
-------
This Python module uses optimization (Mixed Integer Programming) to generate a meal plan with 
variety while still obeying user-defined nutritional constraints. This is in contrat to
solving the Stigler Diet problem directly, which yields sparse and boring solutions.

Created by Tommy Odland, August 2019

Installation
------------
This program was tested with Python 3.7.3 and ortools 7.2.6977. To install and run:
    1. Install Python 3.7
    2. Install ortools (`pip install ortools`)
    3. Run `python <this file>`

If you have markdown2 (`pip install markdown2`), you can render the output of this
program as a HTML file and print it for your fridge. Tested with markdown2 2.3.8.
    1. $ python <this file> > meal.md
    2. $ markdown2 meal.md > meal.html

"""
from data import meals
import statistics

from ortools.linear_solver import pywraplp

# =============================================================================
# FUNCTIONS - Used to generate the meal plan
# =============================================================================


def optimize_mealplan(meals, dietary_constraints, *, meals_limits=None, params=None):
    """Optimize the quantitiy of each meal in a day, given constraints."""

    # =============================================================================
    #     PARSE INPUT ARGUMENTS
    # =============================================================================

    assert isinstance(meals, (list, tuple))
    assert isinstance(dietary_constraints, (dict,))
    assert isinstance(params, (dict,))
    assert (meals_limits is None) or isinstance(meals_limits, (list, tuple))

    meals = meals.copy()
    dietary_constraints = dietary_constraints.copy()

    if meals_limits is None:
        meals_limits = [(None, None) for meal in meals]

    if params is None:
        params = dict()

    # Get parameters
    num_days = params.get("num_days", 1)
    num_meals = params.get("num_meals", 4)
    time_limit_secs = params.get("time_limit_secs", 10)

    # A small number such as 0.001. x_ij >= EPSILON <=> z_ij = 1
    EPSILON = params.get("epsilon", 1e-3)

    # These weights found to be good by in experiments
    weight_price = params.get("weight_price", 0.1)
    weight_nutrients = params.get("weight_nutrients", 2.0)
    weight_range = params.get("weight_range", 0.75)

    # Used for normalization of the cost associated with price
    expected_daily_price = params.get("expected_daily_price", 75)

    M1 = params.get("M1", 20)  # Upper bound on x_ij
    M2 = params.get(
        "M2", 20
    )  # Upper bound on x[i][j] * meal.kcal, i.e. calories in a meal

    # A strange bug is that sometime the optimizer will return INFEASIBLE on attempt #1,
    # but calling this function again with the same inputs works. So we allow calling it
    # two times. This is very hacky and not suitable for production, but it works for
    # 'hobby usage'.
    first_call = params.get("first_call", True)

    # Create a solver and an objective function
    solver = pywraplp.Solver("meals", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    solver.set_time_limit(time_limit_secs * 1000)
    objective_function = 0
    INF = solver.infinity()

    # =============================================================================
    #     ERROR CHECKING AND USER INPUT SANITATION
    # =============================================================================

    # Error checking
    meals_total = num_days * num_meals
    maximum_limit = sum(9999 if high is None else high for (low, high) in meals_limits)
    if maximum_limit < meals_total:
        msg = f"Cannot achieve {meals_total} totals meals with a total of {maximum_limit} meals."
        raise RuntimeError(msg)

    allowed_macros = ("kcal", "protein", "fat", "carbs")
    assert all(key in allowed_macros for key in dietary_constraints.keys())

    assert len(meals_limits) == len(meals)

    # =============================================================================
    #     CREATE VARIABLES
    # =============================================================================

    x = [[None for j in range(num_days)] for i in range(len(meals))]
    z = [[None for j in range(num_days)] for i in range(len(meals))]

    # Loop over every combination of meal and days, create variables
    for i, meal in enumerate(meals):
        for j in range(num_days):
            z[i][j] = solver.IntVar(0, 1, f"z_{i}{j}")

            if meal.discrete:
                x[i][j] = solver.IntVar(0, INF, f"x_{i}{j}")
            else:
                x[i][j] = solver.NumVar(0, INF, f"x_{i}{j}")

            # These constraints ensure that z_ij = 1 iff x_ij >= EPSILON
            solver.Add(EPSILON * z[i][j] <= x[i][j])
            eps = EPSILON / 10
            solver.Add(x[i][j] <= (M1 + eps) * z[i][j] + EPSILON - eps)

    # =============================================================================
    #     CREATE CONSTRAINTS / OBJECTIVE FUNCTION TERM
    # =============================================================================

    # OBJECTIVE FUNCTION TERM 1: Total price of the meals in the program
    denom = expected_daily_price * num_days
    for j in range(num_days):
        daily_price = sum(x[i][j] * meal.price for i, meal in enumerate(meals))
        objective_function += (weight_price / denom) * daily_price

    # OBJECTIVE FUNCTION TERM 2: Deviation from nutrients (on a daily basis)
    for j in range(num_days):
        for macro, (low, high) in dietary_constraints.items():

            # No point in adding any constraints if it's None
            if low is None and high is None:
                continue

            food_macros = [getattr(meal, macro) for meal in meals]

            # Create the sum: sum_i food_i * macro_i
            x_meals = [x[i][j] for i in range(len(meals))]
            total_macro = sum(c * x for x, c in zip(x_meals, food_macros))

            # The maximal deviation in a day is approx mean([low, high]) * nutrients
            # The maximal deviation is the above times the number of days
            denom = statistics.mean(
                [value for value in [low, high] if value is not None]
            )
            denom = denom * num_days  # * len(dietary_constraints)

            # Slack variables related to the lower limit. Only "undershooting" is penalized.
            if low is not None:
                low_positive = solver.NumVar(0, INF, "over_low_lim_" + macro + str(j))
                low_negative = solver.NumVar(0, INF, "under_low_lim_" + macro + str(j))
                solver.Add(total_macro + low_positive - low_negative == low)
                objective_function += (weight_nutrients / denom) * low_positive

            # Slack variables related to the upper limit. Only "overshooting" is penalized.
            if high is not None:
                high_positive = solver.NumVar(0, INF, "over_up_lim_" + macro + str(j))
                high_negative = solver.NumVar(0, INF, "under_upp_lim_" + macro + str(j))
                solver.Add(total_macro + high_positive - high_negative == high)
                objective_function += (weight_nutrients / denom) * high_negative

    # OBJECTIVE FUNCTION TERM 3: Minimal range on calories (on a daily basis)
    for j in range(num_days):
        lower = solver.NumVar(0, INF, f"lower_kcal_{j}")
        upper = solver.NumVar(0, INF, f"upper_kcal_{j}")

        for i, meal in enumerate(meals):

            solver.Add(lower <= x[i][j] * meal.kcal + (1 - z[i][j]) * M2)
            solver.Add(upper >= x[i][j] * meal.kcal)

        # The maximal spread per day is approximately mean([kcal_low, kcal_high]) / meals
        # The maximal spread is the above times the number of days. Normalize w.r.t this
        denom = statistics.mean(
            [value for value in dietary_constraints["kcal"] if value is not None]
        )
        denom = denom * num_days / num_meals
        objective_function += (weight_range / denom) * (upper - lower)

    # HARD CONSTRAINT 1 : Number of meals per day
    for j in range(num_days):
        solver.Add(sum(z[i][j] for i in range(len(meals))) == num_meals)

    # HARD CONSTRAINT 2: Number of times a food is used
    for i, (meal, (low, high)) in enumerate(zip(meals, meals_limits)):

        times_used = sum(z[i])
        assert len(z[i]) == num_days

        # Add lower limit
        if low is not None:
            if low > num_days:
                msg = f"Lower limit on '{meal.name}' is {low}, but there are {num_days} days."
                raise RuntimeError(msg)
            solver.Add(times_used >= low)

        # Add upper limit
        if high is not None:
            solver.Add(times_used <= high)

    # =============================================================================
    #     SOLVE THE OPTIMIZATION PROBLEM
    # =============================================================================

    # Minimize the deviation from the goal
    solver.Minimize(objective_function)
    result_status = solver.Solve()
    if result_status == solver.INFEASIBLE:

        if first_call:
            params["first_call"] = False
            return optimize_mealplan(
                meals=meals,
                dietary_constraints=dietary_constraints,
                meals_limits=meals_limits,
                params=params,
            )

        else:
            raise RuntimeError("Infeasible problem.")

    assert solver.VerifySolution(1e-7, True)

    # =============================================================================
    #     POSTPROCESS THE SOLUTION AND RETURN
    # =============================================================================

    # Parse the variables and get the solution values
    for j in range(num_days):
        for i, meal in enumerate(meals):
            x[i][j] = x[i][j].solution_value()
            z[i][j] = z[i][j].solution_value()

            # Food is chosen
            if z[i][j] > 0.5:
                # If the food is chosen, x_ij is no smaller than epsilon
                x[i][j] = max(x[i][j], EPSILON)
            else:
                x[i][j] = 0

    # Compute the total price
    total_price = 0
    for j in range(num_days):
        daily_price = sum(x[i][j] * meal.price for i, meal in enumerate(meals))
        total_price += daily_price

    return (
        x,
        {
            "obj_func_value": round(solver.Objective().Value(), 6),
            "wall_time": round(solver.wall_time() / 1000, 3),
            "iterations": solver.iterations(),
            "total_price": round(total_price, 1),
        },
    )


def print_results(x, meals, results_data, *, verbose=True):
    """Print the results in Markdown."""

    num_meals = len(x)
    num_days = len(x[0])

    print(f"# Meal plan")
    for day_num in range(num_days):

        x_day = [x[i][day_num] for i in range(num_meals)]

        result = list((m, qnty) for (m, qnty) in zip(meals, x_day) if qnty > 0)

        # Heuristics to get more carbohydrates earlier in the day
        result = sorted(result, key=lambda r: r[0].carbs * r[1], reverse=True)
        price = int(sum(meal.price * qnty for (meal, qnty) in result))
        print(f"\n## Day {day_num + 1} (price: {price} NOK)")

        print(f"\n### Meals\n")
        for meal, qnty in result:
            qnty = round(qnty, 1)
            if qnty % 1 == 0:
                qnty = int(qnty)

            print(f"- {round(qnty, 1)} x {str(meal)}")

        if not verbose:
            continue

        print(f"\n### Statistics\n")
        for macro in ["kcal", "protein", "fat", "carbs"]:
            macro_distr = [getattr(meal, macro) * qnty for (meal, qnty) in result]
            macro_distr_r = [int(round(m)) for m in macro_distr]
            print(f"- Total {macro}: {int(round(sum(macro_distr)))} {macro_distr_r}")


def test_single_day():
    """Example: Optimizing meals for a single day."""

    params = {
        "num_days": 1,  # Total number of days for the meal program
        "num_meals": 4,  # Number of meals per day
        "weight_price": 0.1,
        "weight_nutrients": 2.0,
        "weight_range": 0.75,
    }

    dietary_constraints = {
        "kcal": (1800, 1800),
        "protein": (100, None),
        "fat": (65, None),
    }

    # Convert the dictionary values to a list of Meal objects
    meal_list = list(meals.values())

    x, results_data = optimize_mealplan(
        meals=meal_list, dietary_constraints=dietary_constraints, params=params
    )

    # print(x)
    print_results(x, meal_list, results_data, verbose=True)
    # print(results_data)
    assert True


def test_several_days():
    """Example: Optimizing meals for many days."""

    params = {
        "num_days": 4,  # Total number of days for the meal program
        "num_meals": 4,  # Number of meals per day
        "weight_price": 0.1,
        "weight_nutrients": 2.0,
        "weight_range": 0.75,
    }

    dietary_constraints = {
        "kcal": (1800, 1800),
        "protein": (100, None),
        "fat": (65, None),
    }

    # Convert the dictionary values to a list of Meal objects
    meal_list = list(meals.values())

    # The limits correspond to the foods in the list above.
    meals_limits = [
        (1, None),  # At least once
        (None, 1),  # At most once
        (2, 3),  # Two or three times
        (None, None),
        (None, None),
        (None, None),
        (None, None),
    ]

    x, results_data = optimize_mealplan(
        meals=meal_list,
        meals_limits=meals_limits,
        dietary_constraints=dietary_constraints,
        params=params,
    )

    # print(x)
    print_results(x, meal_list, results_data, verbose=True)
    # print(results_data)
    assert True


if __name__ == "__main__":
    test_single_day()
    test_several_days()
