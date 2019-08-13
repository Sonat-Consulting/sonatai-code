#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMPLE DATA
------------

Example data for blog post. A mix of Norwegian and English names.
"""

from classes import Food, Meal

# =============================================================================
# DATA - Stored in Python objects for simplicity
# =============================================================================

all_foods = [
    Food(
        name="bacon",
        protein=14.0,
        fat=32.0,
        carbs=1.0,
        kcal=350,
        price_per_product=50.9,
        grams_per_product=400,
    ),
    Food(
        name="burger",
        protein=15.0,
        fat=18.0,
        carbs=2.0,
        kcal=230,
        price_per_product=87.3,
        grams_per_product=800,
    ),
    Food(
        name="coop bratwurst",
        protein=12.0,
        fat=20.0,
        carbs=5.2,
        kcal=253,
        price_per_product=25.9,
        grams_per_product=240,
    ),
    Food(
        name="cottage cheese",
        protein=13.0,
        fat=2.0,
        carbs=2.1,
        kcal=79,
        price_per_product=24.4,
        grams_per_product=400,
    ),
    Food(
        name="egg",
        protein=13.0,
        fat=10.6,
        carbs=0.3,
        kcal=149,
        price_per_product=32.9,
        grams_per_product=690,
    ),
    Food(
        name="frossen kyllingfilet",
        protein=19.0,
        fat=1.8,
        carbs=0.3,
        kcal=94,
        price_per_product=260.0,
        grams_per_product=2500,
    ),
    Food(
        name="grovt brød",
        protein=11.0,
        fat=4.8,
        carbs=36.0,
        kcal=245,
        price_per_product=39.5,
        grams_per_product=750,
    ),
    Food(
        name="gulost",
        protein=27.0,
        fat=27.0,
        carbs=0.0,
        kcal=351,
        price_per_product=110.0,
        grams_per_product=1000,
    ),
    Food(
        name="jasmin ris",
        protein=2.7,
        fat=0.1,
        carbs=31.1,
        kcal=136,
        price_per_product=45.8,
        grams_per_product=1000,
    ),
    Food(
        name="kjøttdeig",
        protein=19.0,
        fat=9.0,
        carbs=0.0,
        kcal=157,
        price_per_product=32.5,
        grams_per_product=400,
    ),
    Food(
        name="lettmelk",
        protein=3.5,
        fat=0.5,
        carbs=4.5,
        kcal=37,
        price_per_product=16.4,
        grams_per_product=1000,
    ),
    Food(
        name="melkesjokolade",
        protein=8.1,
        fat=33.0,
        carbs=55.0,
        kcal=550,
        price_per_product=38.6,
        grams_per_product=200,
    ),
    Food(
        name="musli",
        protein=9.0,
        fat=4.8,
        carbs=63.0,
        kcal=351,
        price_per_product=23.1,
        grams_per_product=750,
    ),
    Food(
        name="PF whey",
        protein=71.8,
        fat=8.1,
        carbs=7.9,
        kcal=377,
        price_per_product=599.0,
        grams_per_product=3000,
    ),
    Food(
        name="svinekotelett dypfryst",
        protein=20.0,
        fat=18.0,
        carbs=0.0,
        kcal=243,
        price_per_product=98.6,
        grams_per_product=2000,
    ),
    Food(
        name="sweet and sour sauce",
        protein=0.4,
        fat=0.2,
        carbs=16.4,
        kcal=71,
        price_per_product=35.0,
        grams_per_product=675,
    ),
    Food(
        name="coop sweet and sour",
        protein=0.6,
        fat=0.1,
        carbs=20,
        kcal=85,
        price_per_product=14.9,
        grams_per_product=500,
    ),
    Food(
        name="nøtti frutti",
        protein=13,
        fat=26,
        carbs=47,
        kcal=464,
        price_per_product=39.7,
        grams_per_product=350,
    ),
    Food(
        name="xtra jasminris",
        protein=7.5,
        fat=0.8,
        carbs=75,
        kcal=343,
        price_per_product=37.4,
        grams_per_product=5000,
    ),
    Food(
        name="currypaste",
        protein=3.9,
        fat=22.3,
        carbs=5.6,
        kcal=262,
        price_per_product=33.2,
        grams_per_product=165,
    ),
    Food(
        name="kokosmelk",
        protein=1.5,
        fat=17,
        carbs=2.4,
        kcal=169,
        price_per_product=13.3,
        grams_per_product=400,
    ),
    Food(
        name="hakkede tomater",
        protein=1,
        fat=0,
        carbs=6.8,
        kcal=34,
        price_per_product=7.1,
        grams_per_product=400,
    ),
    Food(
        name="tomatbønner",
        protein=3.8,
        fat=0.6,
        carbs=14.0,
        kcal=83,
        price_per_product=11.8,
        grams_per_product=420,
    ),
    Food(
        name="yoghurt",
        protein=3.7,
        fat=3.1,
        carbs=10.5,
        kcal=84,
        price_per_product=17.0,
        grams_per_product=600,
    ),
]


foods = {food.name: food for food in all_foods}

all_meals = [
    Meal(name="mixed nuts", foods={foods["nøtti frutti"]: 10}, discrete=False),
    Meal(
        name="yogurt w/ muesli",
        foods={foods["yoghurt"]: 150, foods["musli"]: 40},
        discrete=True,
    ),
    Meal(
        name="chicken w/ sweet&sour",
        foods={
            foods["frossen kyllingfilet"]: 40.7,
            foods["coop sweet and sour"]: 11.5,
            foods["jasmin ris"]: 47.8,
        },
        discrete=False,
    ),
    Meal(
        name="hamburger",
        foods={foods["grovt brød"]: 40, foods["burger"]: 80},
        discrete=True,
    ),
    Meal(name="egg", foods={foods["egg"]: 70}, discrete=True),
    Meal(
        name="scoop protein shake",
        foods={foods["PF whey"]: 25, foods["lettmelk"]: 150},
        discrete=False,
    ),
    Meal(
        name="yogurt w/ ct.cheese",
        foods={foods["yoghurt"]: 150, foods["cottage cheese"]: 100},
        discrete=True,
    ),
]


meals = {meal.name: meal for meal in all_meals}
