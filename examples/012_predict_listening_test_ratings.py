# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
.. _calculate_predict_listening_test_ratings:

Predict listening test ratings
------------------------------

This example shows how to predict the mean ratings of automative HVAC sounds based on
psychoacoustic indicators, using listening test data obtained with Ansys Sound - Jury Listening
Test.

Here, we try to predict the mean sound ratings on the basis of 4 psychoacoustic indicators that
are typically used for this kind of sounds (HVAC):

- Loudness (ISO 532-1),
- Sharpness (DIN 45692),
- Fluctuation strength (Sontacchi method),
- Tonality (ECMA 418-2).

The sound ratings used here were obtained in a listening test designed and conducted with Ansys
Sound JLT, from which the analyzed data were exported into a CSV file. The corresponding test
project and data should be located here:
C:/Users/Public/Documents/Ansys/Acoustics/JLT/CE - Automotive HVAC
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the DPF server, and
# setting up the working directory.

# Load standard libraries.
import csv
import os
from itertools import islice
from math import sqrt

import matplotlib.pyplot as plt
from sklearn import linear_model

# Load Ansys libraries.
from ansys.sound.core.examples_helpers import (download_all_carHVAC_wav,
                                               download_HVAC_test_wav,
                                               download_JLT_CE_data_csv)
from ansys.sound.core.psychoacoustics import (FluctuationStrength,
                                              LoudnessISO532_1_Stationary,
                                              SharpnessDIN45692,
                                              TonalityECMA418_2)
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav

# Connect to a DPF Sound server (remote or local).
my_server = connect_to_or_start_server(use_license_context=True)

# Download the necessary files for this example.
model_wav_files_path = download_all_carHVAC_wav()
JLT_ratings_path = download_JLT_CE_data_csv()
test_wav_file_path = download_HVAC_test_wav()

# %%
# Define indicator computation function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we define a function that calculate the 4 psychoacoustic indicators of interest, given a
# wave file path.


def compute_indicators(wav_file_path: str = None) -> list:
    """Compute psychoacoustic indicators for a given wav file.

    Note: Only the first channel is considered for the computation of the indicators.

    Parameters
    ----------
    wav_file_path : str, optional
        Path to the wav file to analyze.

    Returns
    -------
    list
        List of psychoacoustic indicator values: loudness level in phon, sharpness in acum,
        fluctuation strength in vacil, and tonality in tuHMS.
    """
    if not (isinstance(wav_file_path, str)) or len(wav_file_path) == 0:
        raise TypeError("wav_file_path must be a non-empty string.")
    elif not (os.path.isfile(wav_file_path)):
        raise FileNotFoundError(f"File {wav_file_path} not found.")

    # Load the sound file.
    wav_loader = LoadWav(wav_file_path)
    wav_loader.process()
    signal = wav_loader.get_output()[0]

    # Compute the psychoacoustic indicators.
    indicator = LoudnessISO532_1_Stationary(signal=signal)
    indicator.process()
    LN = indicator.get_loudness_level_phon()

    indicator = SharpnessDIN45692(signal=signal)
    indicator.process()
    S = indicator.get_sharpness()

    indicator = FluctuationStrength(signal=signal)
    indicator.process()
    FS = indicator.get_fluctuation_strength()

    indicator = TonalityECMA418_2(signal=signal, field_type="Free", edition="3rd")
    indicator.process()
    T = indicator.get_tonality()

    return [LN, S, FS, T]


# %%
# Define prediction function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we define a function that predicts the rating for a given wave file, and a set of regression
# coefficients.


def apply_prediction_formula(wav_file_path: str, coefficients: list = None) -> float:
    r"""Apply the regression formula to predict the rating of a sound file.

    Computes a linear combination of the following psychoacoustic indicators:
    - Loudness (ISO 532-1): LN,
    - Sharpness (DIN 45692): S,
    - Fluctuation strength (Sontacchi method): FS,
    - Tonality (ECMA 418-2): T,
    using the regression coefficients provided in the coefficients list.
    The formula is:

    ..math::
        rating = a0 + a1 \cdot LN + a2 \cdot S + a3 \cdot FS + a4 \cdot T

    where a0 is the intercept and a1, a2, a3, and a4 are the coefficients of the model.

    Parameters
    ----------
    wav_file_path : str
        Path to the wav file to analyze.

    coefficients : list, default: None.
        List of regression coefficients (including the intercept): a0, a1, a2, a3, and a4. If None,
        the coefficients are [1, 0, 0, 0, 0].

    Returns
    -------
    float
        Predicted rating.
    """
    if coefficients is None:
        coefficients = [1, 0, 0, 0, 0]
    elif not (isinstance(coefficients, list)) or len(coefficients) != 5:
        raise TypeError("coefficients must be a list of 5 elements.")

    # Compute the psychoacoustic indicators for the sound file.
    indicators = compute_indicators(wav_file_path)

    # Apply the formula to compute the rating.
    return (
        coefficients[0]
        + coefficients[1] * indicators[0]
        + coefficients[2] * indicators[1]
        + coefficients[3] * indicators[2]
        + coefficients[4] * indicators[3]
    )


# %%
# Read the Ansys Sound JLT data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Read the CSV file produced with Ansys Sound JLT and containing the mean ratings of the sounds of
# the test.

# Initialize lists to store filenames and ratings.
filenames = []
ratings = []

with open(JLT_ratings_path) as f:
    reader = csv.reader(f, delimiter=";")

    # Skip the first 7 lines of the CSV file (general info, and table header).
    reader = islice(reader, 7, None)

    for row in reader:
        # First column is the filename, second column is the mean rating.
        filenames.append(row[0])
        ratings.append(float(row[1]))

# %%
# Calculate the psychoacoustic indicators
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute the psychoacoustic indicators for each sound file. The following indicators are computed:
# - Loudness (ISO 532-1),
# - Sharpness (DIN 45692),
# - Fluctuation strength (Sontacchi method),
# - Tonality (ECMA 418-2).

# Initialize a list to store the indicators for each file. The list will contain sublists, each
# sublist containing the values of the selected indicators for each sound.
indicators = []

# Process each sound file one by one.
# Note that this step is quite long, as some indicators (Fluctuation Strength, and more
# importantly, Tonality) are quite heavy to compute.
# Note also that, although the sounds of the test are stereo (binaural recordings), we are
# using the left channel only. You get similar results if you use the right channel of the
# average of the two.
for file_name in filenames:
    print(f"Calculating indicators for file: {file_name} ...")
    wav_file_path = os.path.join(model_wav_files_path, file_name + ".wav")

    # Append the indicator values for the current sound to the list.
    indicators.append(compute_indicators(wav_file_path))

# %%
# Calculate the multiple linear regression
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use package scikit-learn (https://scikit-learn.org/) to create a multiple linear regression model,
# to predict the ratings based on the computed psychoacoustic indicators.

# Create and compute the model.
regression = linear_model.LinearRegression()
regression.fit(indicators, ratings)

# Compute the predicted ratings using the regression model.
ratings_hat = regression.predict(indicators)

# Display the model coefficients and the correlation coefficient.
print(f"Linear regression model coefficients: {regression.coef_}")
print(f"Correlation coefficient: {sqrt(regression.score(indicators, ratings)):.3f}")

# Plot the predicted ratings against the actual ratings.
plt.plot([0, 100], [0, 100], "k--")
plt.scatter(ratings_hat, ratings)
plt.xlabel("Predicted ratings")
plt.ylabel("Actual ratings")
plt.title("Predicted vs Actual ratings")
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.grid()
plt.show()

# %%
# Use the regression coefficients for prediction
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use the model coefficients to estimate the rating of a new sound file. Using the model
# coefficients consists in computing the indicators and applying the formula:
# rating = a0 + a1 * LN + a2 * S + a3 * FS + a4 * T, where a0 is the intercept and a1, a2, a3, and
# a4 are the coefficients of the model.
# The coefficients of the model are stored in the regression object, and can be accessed using the
# `coef_` attribute. The intercept is stored in the `intercept_` attribute of the regression object.

# Apply the regression formula to predict the rating of the sound file.
# Note: the intercept (offset) must be added to the coefficients list.
coefficients = [regression.intercept_] + list(regression.coef_)
rating_hat = apply_prediction_formula(test_wav_file_path, coefficients)

print(
    f"\nPredicted rating (0-100) for file {os.path.split(test_wav_file_path)[-1]}: {rating_hat:.2f}"
)
