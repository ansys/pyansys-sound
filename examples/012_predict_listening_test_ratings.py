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

This example shows how to predict the mean ratings of automotive HVAC sounds based on
psychoacoustic indicators, using the data from a listening test conducted with Ansys Sound - Jury
Listening Test (JLT).

Here, we demonstrate how to build an objective indicator to help predict automotive HVAC sound
ratings, on the basis of 4 psychoacoustic indicators that are typically used for this kind of
sounds:

- Loudness (ISO 532-1),
- Sharpness (DIN 45692),
- Fluctuation strength (Sontacchi method),
- Tonality (ECMA 418-2).

The sound ratings used in this example were obtained from a listening test designed with Ansys
Sound JLT. In this test, 29 participants evaluated 20 automotive HVAC sounds. This example uses the
data obtained when exporting, in JLT, the analyzed results into a CSV file. With a standard
installation of JLT, the corresponding listening test project should be located here:
`C:/Users/Public/Documents/Ansys/Acoustics/JLT/CE - Automotive HVAC`.
"""

# %%
# Set up analysis
# ~~~~~~~~~~~~~~~
# Setting up the analysis consists of loading Ansys libraries, connecting to the DPF server, and
# downloading the necessary data files.

# Load standard libraries.
from math import sqrt
import os

from ansys.dpf.core import Field
import matplotlib.pyplot as plt
from sklearn import linear_model

# Load Ansys libraries.
from ansys.sound.core.examples_helpers import (
    download_all_carHVAC_wav,
    download_HVAC_test_wav,
    download_JLT_CE_data_csv,
)
from ansys.sound.core.psychoacoustics import (
    FluctuationStrength,
    LoudnessISO532_1_Stationary,
    SharpnessDIN45692,
    TonalityECMA418_2,
)
from ansys.sound.core.server_helpers import connect_to_or_start_server
from ansys.sound.core.signal_utilities import LoadWav
from ansys.sound.core.signal_utilities.crop_signal import CropSignal

# Connect to a DPF Sound server (remote or local).
my_server = connect_to_or_start_server(use_license_context=True)

# Download the necessary files for this example.
model_wav_files_path = download_all_carHVAC_wav()
JLT_ratings_path = download_JLT_CE_data_csv()
test_wav_file_path = download_HVAC_test_wav()

# %%
# Define indicator computation function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we define a function that calculates the 4 psychoacoustic indicators of interest (listed at
# at the beginning of the example), given an input sound signal as a DPF field.


def compute_indicators(signal: Field) -> list:
    """Compute psychoacoustic indicators for a given sound signal.

    Parameters
    ----------
    signal : Field
        Sound signal to analyze.

    Returns
    -------
    list
        List of psychoacoustic indicator values: loudness level in phon, sharpness in acum,
        fluctuation strength in vacil, and tonality in tuHMS.
    """
    # Loudness level (ISO 532-1)
    indicator = LoudnessISO532_1_Stationary(signal=signal)
    indicator.process()
    LN = indicator.get_loudness_level_phon()

    # Sharpness (DIN 45692)
    indicator = SharpnessDIN45692(signal=signal)
    indicator.process()
    S = indicator.get_sharpness()

    # Fluctuation strength (Sontacchi method)
    indicator = FluctuationStrength(signal=signal)
    indicator.process()
    FS = indicator.get_fluctuation_strength()

    # Tonality (ECMA 418-2)
    indicator = TonalityECMA418_2(signal=signal, field_type="Free", edition="3rd")
    indicator.process()
    T = indicator.get_tonality()

    return [LN, S, FS, T]


# %%
# Define prediction function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Here we define a function that predicts the rating for an automotive HVAC sound signal, given a
# set of regression coefficients. The function computes 4 relevant psychoacoustic indicators for
# automotive HVAC sounds, and then applies the regression formula to obtain the predicted rating:
#
# .. math::
#        rating = a_0 + a_1 \cdot LN + a_2 \cdot S + a_3 \cdot FS + a_4 \cdot T
#
# where :math:`a_0` is the intercept and :math:`a_1`, :math:`a_2`, :math:`a_3`, and :math:`a_4` are
# the coefficients of the model, and :math:`LN`, :math:`S`, :math:`FS`, and :math:`T` are the
# loudness level, sharpness, fluctuation strength, and tonality, respectively.


def apply_prediction_formula(signal: Field, coefficients: list = None) -> float:
    """Apply the regression formula to predict the rating of a sound signal.

    Parameters
    ----------
    signal : Field
        Sound signal to evaluate.

    coefficients : list, default: None.
        List of regression coefficients (including the intercept): a0, a1, a2, a3, and a4. If None,
        the coefficients are [1, 0, 0, 0, 0].

    Returns
    -------
    float
        Predicted rating of the input sound signal.
    """
    if coefficients is None:
        coefficients = [1, 0, 0, 0, 0]
    elif not (isinstance(coefficients, list)) or len(coefficients) != 5:
        raise TypeError("coefficients must be a list of 5 elements.")

    # Compute the psychoacoustic indicators for the sound file.
    indicators = compute_indicators(signal)

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
# Read the CSV file produced with Ansys Sound JLT. This file contains descriptive statistics of the
# sound ratings obtained during the listening test conduction. Most notably, it contains the
# rating of each sound averaged over the test participants.

# Initialize lists to store file names and ratings.
filenames = []
ratings = []

# Print the file content for information.
with open(JLT_ratings_path, encoding="utf-8-sig") as f:
    print(f.read())

# %%
# Extract HVAC sound file names and mean ratings from the CSV file.
with open(JLT_ratings_path, encoding="utf-8-sig") as f:
    lines = f.readlines()
    lines = lines[7:]  # Skip the first 7 lines (general info, and table header).

    # Store file names and mean ratings (first and second columns).
    for line in lines:
        row = line.split(";")
        filenames.append(row[0])
        ratings.append(float(row[1]))

# %%
# Calculate the psychoacoustic indicators
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Compute the psychoacoustic indicators for each sound file. The following indicators are computed:
#
# - Loudness (ISO 532-1),
# - Sharpness (DIN 45692),
# - Fluctuation strength (Sontacchi method),
# - Tonality (ECMA 418-2).
#
# .. note::
#    This computation step may be long, as some indicators (fluctuation strength, and tonality) are
#    quite heavy to compute. Note also that, although the sounds of the test are stereo (binaural
#    recordings) and 5 seconds long, we are using the first second of the left channel only. You
#    get similar results if you use the right channel or the average of the two, and the full
#    signal duration.

# Initialize a list to store the indicators for each file. The list will contain sublists, each
# sublist containing the values of the selected indicators for each sound.
indicators = []

# Process each sound file one by one.
for file_name in filenames:
    print(f"Calculating indicators for file: {file_name} ...")
    wav_file_path = os.path.join(model_wav_files_path, file_name + ".wav")

    # Load the sound file.
    wav_loader = LoadWav(wav_file_path)
    wav_loader.process()

    # Keep the first channel only.
    signal = wav_loader.get_output()[0]

    # Keep the first second of signal only.
    cropper = CropSignal(signal=signal, start_time=0.0, end_time=1.0)
    cropper.process()
    signal = cropper.get_output()

    # Compute and append the indicator values for the current sound to the list.
    indicators.append(compute_indicators(signal))

# %%
# Calculate the multiple linear regression
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use package :mod:`sklearn` (https://scikit-learn.org/) to create a multiple linear
# regression model, to predict the ratings based on the computed psychoacoustic indicators.

# Create and compute the model.
regression = linear_model.LinearRegression()
regression.fit(indicators, ratings)

# Compute the predicted ratings using the regression model.
ratings_hat = regression.predict(indicators)

# Display the model coefficients and the correlation coefficient.
print(f"Linear regression model coefficients: {regression.coef_}")
print(f"Correlation coefficient: {sqrt(regression.score(indicators, ratings)):.3f}")

# %%
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
# The correlation coefficient (0.983) is very close to 1, and the points in the plot are
# well aligned. This shows that the rating prediction model is quite accurate for the sounds of
# the listening test.

# %%
# Use the regression coefficients for prediction
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use the model coefficients to estimate the rating of a new sound file. Using the model
# coefficients consists in computing the indicators and applying the formula:
#
# .. math::
#        rating = a_0 + a_1 \cdot LN + a_2 \cdot S + a_3 \cdot FS + a_4 \cdot T
#
# where :math:`a_0` is the intercept and :math:`a_1`, :math:`a_2`, :math:`a_3`, and :math:`a_4` are
# the coefficients of the model, and :math:`LN`, :math:`S`, :math:`FS`, and :math:`T` are the
# loudness level, sharpness, fluctuation strength, and tonality, respectively.
#
# The coefficients of the model are stored in the regression object, and can be accessed using the
# ``coef_`` attribute. The intercept is stored in the ``intercept_`` attribute of the regression
# object.

# Load the sound file for which to predict the rating.
wav_loader = LoadWav(test_wav_file_path)
wav_loader.process()

# Keep the first channel only.
signal = wav_loader.get_output()[0]

# Apply the regression formula to predict the rating of the sound file.
# Note: the intercept (offset) must be added to the coefficients list.
coefficients = [regression.intercept_] + list(regression.coef_)
rating_hat = apply_prediction_formula(signal, coefficients)

print(
    f"\nPredicted rating (0-100) for file {os.path.split(test_wav_file_path)[-1]}: {rating_hat:.2f}"
)

# %%
# This predicted rating (28.52) tells us that the sound is not very pleasant in comparison with the
# other sounds of the listening test, and that it would have probably ranked poorly, had it been
# included during the test conduction.
