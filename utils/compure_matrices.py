import os
import json
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from configs.constants import OUTPUT_FOLDER_JSON_IMAGES,LABELS_FOLDER,INPUT_FOLDER_IMAGES

# -------------------------
# Configuration
# -------------------------

json_dir = OUTPUT_FOLDER_JSON_IMAGES
label_dir = LABELS_FOLDER
image_dir = INPUT_FOLDER_IMAGES
IOU_THRESHOLD = 0.5

# -------------------------
# IOU Calculation
# -------------------------
def compute_iou(boxA,boxB):
    """
    Compute Intersection over Union (IoU) between two bounding boxes.
    """
    xA = max(boxA["x_min"],boxB["x_min"])
    yA = max(boxA["y_min"], boxB["y_min"])
    xB = min(boxA["x_max"], boxB["x_max"])
    yB = min(boxA["y_max"], boxB["y_max"])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA["x_max"] - boxA["x_min"]) * (boxA["y_max"] - boxA["y_min"])
    boxBArea = (boxB["x_max"] - boxB["x_min"]) * (boxB["y_max"] - boxB["y_min"])
    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou


# -------------------------
# Ground Truth Loader (YOLO Format)
# -------------------------
def load_ground_truth_boxes(label_path, image_size):
    """
    Load YOLO format labels and convert to absolute pixel bounding boxes.
    """
    gt_boxes = []
    if not os.path.exists(label_path):
        return gt_boxes

    width, height = image_size
    with open(label_path, "r") as f:
        for line in f:
            class_id, x_center, y_center, w, h = map(float, line.strip().split())
            x_center *= width
            y_center *= height
            w *= width
            h *= height
            x_min = x_center - w / 2
            y_min = y_center - h / 2
            x_max = x_center + w / 2
            y_max = y_center + h / 2
            gt_boxes.append({"x_min": x_min, "y_min": y_min, "x_max": x_max, "y_max": y_max})
    return gt_boxes

# -------------------------
# Evaluate One Image
# -------------------------
def evaluate_image(json_data, label_path, image_path):
    """
    Evaluate a single image by comparing predicted boxes (from JSON) to ground truth.
    Returns: true positives (TP), false positives (FP), false negatives (FN)
    """
    with Image.open(image_path) as img:
        image_size = img.size

    gt_boxes = load_ground_truth_boxes(label_path, image_size)
    detections = json_data["detections"]
    predictions_info = []

    true_positives = 0
    false_positives = 0
    matched_gt = set()

    for det in detections:
        pred_box = det["bounding_box"]
        conf = det["confidence"]
        matched = False
        for i, gt_box in enumerate(gt_boxes):
            if i in matched_gt:
                continue
            iou = compute_iou(pred_box, gt_box)
            if iou >= IOU_THRESHOLD:
                true_positives += 1
                matched_gt.add(i)
                matched = True
                predictions_info.append((conf, True))  # <--- TP
                break
        if not matched:
            false_positives += 1
            predictions_info.append((conf, False))  # <--- FP

    false_negatives = len(gt_boxes) - len(matched_gt)
    return true_positives, false_positives, false_negatives, predictions_info, len(gt_boxes)


# -------------------------
# Average Precision Calculation
# -------------------------
def compute_average_precision(sorted_predictions, num_gt):
    """
    sorted_predictions: list of (confidence, is_tp)
    num_gt: total number of ground truth boxes
    """
    if num_gt == 0:
        return 0.0

    sorted_predictions.sort(key=lambda x: x[0], reverse=True)  # sort by confidence descending

    tp_cumsum = 0
    fp_cumsum = 0
    precisions = []
    recalls = []

    for conf, is_tp in sorted_predictions:
        if is_tp:
            tp_cumsum += 1
        else:
            fp_cumsum += 1
        precision = tp_cumsum / (tp_cumsum + fp_cumsum + 1e-6)
        recall = tp_cumsum / (num_gt + 1e-6)
        precisions.append(precision)
        recalls.append(recall)

    # Interpolate to get precision at each recall level from 0.0 to 1.0
    ap = 0.0
    for r in np.linspace(0, 1, 11):
        p = max([prec for prec, rec in zip(precisions, recalls) if rec >= r] + [0.0])
        ap += p / 11
    return ap,precisions,recalls

# -------------------------
# Evaluate Entire Dataset
# -------------------------
def evaluate_dataset(json_dir, label_dir, image_dir):
    """Evaluate all predictions against ground truth labels."""
    tp_total = 0
    fp_total = 0
    fn_total = 0
    all_predictions = []
    total_gt_boxes = 0

    for filename in os.listdir(json_dir):
        if not filename.endswith(".json"):
            continue

        json_path = os.path.join(json_dir, filename)
        with open(json_path, "r") as f:
            json_data = json.load(f)

        image_name = json_data["image_name"]
        image_path = os.path.join(image_dir, image_name)
        label_path = os.path.join(label_dir, os.path.splitext(image_name)[0] + ".txt")

        if not os.path.exists(image_path) or not os.path.exists(label_path):
            continue

        tp, fp, fn,preds,gt_count = evaluate_image(json_data, label_path, image_path)
        tp_total += tp
        fp_total += fp
        fn_total += fn
        all_predictions.extend(preds)
        total_gt_boxes += gt_count

    return tp_total, fp_total, fn_total,all_predictions,total_gt_boxes

# -------------------------
# Metric Calculation
# -------------------------
def calculate_metrics(tp, fp, fn):
    """Calculate precision, recall, and F1 score."""
    precision = tp / (tp + fp + 1e-6)
    recall = tp / (tp + fn + 1e-6)
    f1 = 2 * precision * recall / (precision + recall + 1e-6)
    return precision, recall, f1

# -------------------------
# Display Results
# -------------------------
def display_results(tp, fp, fn, precision, recall, f1,ap,precisions_list,recalls_list):
    """
    Create a metrics DataFrame and a confusion matrix, and display them.
    """
    # Create a DataFrame for the metrics
    metrics_df = pd.DataFrame([{
        "True Positives": tp,
        "False Positives": fp,
        "False Negatives": fn,
        "Precision": round(precision, 3),
        "Recall": round(recall, 3),
        "F1 Score": round(f1, 3),
        "Average Precision (AP)": round(ap, 3)
    }])
    print("\nDetection Metrics:")
    print(metrics_df)
    
    # Plot a bar chart for the metrics
    metrics = ["Precision", "Recall", "F1 Score","AP"]
    values = [precision, recall, f1, ap]
    plt.figure(figsize=(6,4))
    sns.barplot(x=metrics, y=values, palette="viridis")
    plt.ylim(0, 1)
    plt.yticks(np.arange(0,1.05,0.1))
    plt.title("Detection Metrics")
    plt.ylabel("Score")
    plt.savefig("/workspace/deepstream/deepstream_project/output/metrics/metrics_barplot.png")
    plt.close()
    
    # Build a simple confusion matrix:
    # Since we have one class, we consider: 
    #   - Actual Positives: TP + FN
    #   - Predicted Positives: TP + FP
    # We build a 2x2 matrix for visualization:
    cm = np.array([[tp, fn], [fp, 0]])
    cm_df = pd.DataFrame(cm, index=["Actual Positive", "Actual Negative"],
                         columns=["Predicted Positive", "Predicted Negative"])
    plt.figure(figsize=(5,4))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.savefig("/workspace/deepstream/deepstream_project/output/metrics/confusion_matrix.png")
    plt.close()

    # Build a normalized confusion matrix:
    cm_normalized = cm.astype('float') / cm.sum(axis=1, keepdims=True)
    cm_df = pd.DataFrame(cm_normalized, index=["Actual Positive", "Actual Negative"],
                         columns=["Predicted Positive", "Predicted Negative"])
    plt.figure(figsize=(5,4))
    sns.heatmap(cm_df, annot=True, fmt=".2f", cmap="Blues", cbar=True)
    plt.title("Normalized Confusion Matrix")
    plt.savefig("/workspace/deepstream/deepstream_project/output/metrics/confusion_matrix_normalized.png")
    plt.close()

    # Build a Recall Precisions Curve
    plt.figure(figsize=(6, 5))
    plt.plot(recalls_list, precisions_list, marker='.')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'Precision-Recall Curve (AP = {ap:.3f})')
    plt.grid(True)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.savefig("/workspace/deepstream/deepstream_project/output/metrics/precision_recall_curve.png")
    plt.close()


# -------------------------
# Main Runner
# -------------------------
def run_evaluation():
    tp, fp, fn,predictions,num_gt = evaluate_dataset(json_dir, label_dir, image_dir)
    precision, recall, f1 = calculate_metrics(tp, fp, fn)
    ap,precisions,recalls = compute_average_precision(predictions, num_gt)
    display_results(tp, fp, fn, precision, recall, f1,ap,precisions,recalls)
    print(f"Average Precision (AP): {ap:.3f}")

# -------------------------
# Run the Evaluation
# -------------------------
if __name__ == "__main__":
    run_evaluation()