"""
Script to generate reports.
"""

import os
import sys

from functools import reduce
import collections
import logging

# Initializing constants.
LOG_LEVEL = logging.INFO
PREDICTIONS_PATH = os.path.join("predictions")
OUTPUT_PATH = os.path.join("madrid.txt")

# Initializing logger.
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initializing reports.
scores_by_label = collections.defaultdict(list)
avg_scores = []

# Collect data from all individual reports.
for prediction_filename in os.listdir(PREDICTIONS_PATH):

    # Collecting predictions.
    prediction_path = os.path.join(PREDICTIONS_PATH, prediction_filename)
    logger.debug("Reading prediction. | sf_path=%s", prediction_path)

    # Reading file.
    with open(prediction_path, "r") as file_buffer:
        predictions = file_buffer.read().split("\n")
    logger.debug("Prediction loaded. | sf_predictions=%s", len(predictions))
    
    # Obtaining URL.
    url = predictions[0].replace("[", "").replace("]", "")
    logger.debug("URL detected. | sf_url=%s", url)

    # Obtaining score.
    score = 0
    if predictions[-2].startswith("["):
        score = float(predictions[-2].replace("[Score: ", "").replace("]", ""))
    if score:
        avg_scores.append(score)
    logger.debug("Score detected. | sf_score=%s", score)

    # Reading predictions.
    for line in predictions[1:]:

        # Evaluating each line.
        logger.debug("Reading prediction line. | sf_line=%s", line)
        if line and line.startswith("- "):

            # Obtaining label and score.
            label, score = line.split(":")
            score = float(score)
            label = label[2:]
            logger.debug("Label detected. | sf_label=%s | sf_score=%s", label, score)

            # Adding results to report.
            scores_by_label[label].append(score)

# Calculate scores.
reducer = lambda x, y: x + y
labels_score = {
    label: reduce(reducer, scores_by_label[label])
    for label in scores_by_label
}
logger.debug("Global score calculated. | sf_scores=%s", len(labels_score))

# Sorting labels.
sorted_labels = sorted(scores_by_label, key=lambda x: labels_score[x], reverse=True)
logger.debug("Labels sorted. | sf_labels=%s", sorted_labels)

# Collecting all results.
with open(OUTPUT_PATH, "w") as file_buffer:
    for label in sorted_labels:
        score = labels_score[label]
        print("{:30} {}".format(label, score), file=file_buffer)
logger.info("Report generated. | sf_path=%s", OUTPUT_PATH)

# Get average scores.
avg = sum(avg_scores) / len(avg_scores)
logger.info("Average score detected. | sf_avg=%s", avg)
