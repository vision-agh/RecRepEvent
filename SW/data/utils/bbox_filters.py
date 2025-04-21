import numpy as np
from typing import Dict


dataset_2_height = {'gen1': 240, 'gen4': 720}
dataset_2_width = {'gen1': 304, 'gen4': 1280}

def prophesee_bbox_filter(labels: np.ndarray, dataset_type: str) -> np.ndarray:
    assert dataset_type in {'gen1', 'gen4'}

    # Default values taken from: https://github.com/prophesee-ai/prophesee-automotive-dataset-toolbox/blob/0393adea2bf22d833893c8cb1d986fcbe4e6f82d/src/psee_evaluator.py#L23-L24
    min_box_diag = 60 if dataset_type == 'gen4' else 30
    # Corrected values from supplementary mat from paper for min_box_side!
    min_box_side = 20 if dataset_type == 'gen4' else 10

    w_lbl = labels['w']
    h_lbl = labels['h']

    diag_ok = w_lbl ** 2 + h_lbl ** 2 >= min_box_diag ** 2
    side_ok = (w_lbl >= min_box_side) & (h_lbl >= min_box_side)
    keep = diag_ok & side_ok
    labels = labels[keep]
    return labels


def conservative_bbox_filter(labels: np.ndarray) -> np.ndarray:
    w_lbl = labels['w']
    h_lbl = labels['h']
    min_box_side = 5
    side_ok = (w_lbl >= min_box_side) & (h_lbl >= min_box_side)
    labels = labels[side_ok]
    return labels


def remove_faulty_huge_bbox_filter(labels: np.ndarray, dataset_type: str) -> np.ndarray:
    """There are some labels which span the frame horizontally without actually covering an object."""
    assert dataset_type in {'gen1', 'gen4'}
    w_lbl = labels['w']
    max_width = (9 * dataset_2_width[dataset_type]) // 10
    side_ok = (w_lbl <= max_width)
    labels = labels[side_ok]
    return labels


def crop_to_fov_filter(labels: np.ndarray, dataset_type: str) -> np.ndarray:
    assert dataset_type in {'gen1', 'gen4'}, f'{dataset_type=}'
    # In the gen1 and gen4 datasets the bounding box can be partially or completely outside the frame.
    # We fix this labeling error by cropping to the FOV.
    frame_height = dataset_2_height[dataset_type]
    frame_width = dataset_2_width[dataset_type]
    x_left = labels['x']
    y_top = labels['y']
    x_right = x_left + labels['w']
    y_bottom = y_top + labels['h']
    x_left_cropped = np.clip(x_left, a_min=0, a_max=frame_width - 1)
    y_top_cropped = np.clip(y_top, a_min=0, a_max=frame_height - 1)
    x_right_cropped = np.clip(x_right, a_min=0, a_max=frame_width - 1)
    y_bottom_cropped = np.clip(y_bottom, a_min=0, a_max=frame_height - 1)

    w_cropped = x_right_cropped - x_left_cropped
    assert np.all(w_cropped >= 0)
    h_cropped = y_bottom_cropped - y_top_cropped
    assert np.all(h_cropped >= 0)

    labels['x'] = x_left_cropped
    labels['y'] = y_top_cropped
    labels['w'] = w_cropped
    labels['h'] = h_cropped

    # Remove bboxes that have 0 height or width
    keep = (labels['w'] > 0) & (labels['h'] > 0)
    labels = labels[keep]
    return labels


def prophesee_remove_labels_filter_gen4(labels: np.ndarray) -> np.ndarray:
    # Original gen4 labels: pedestrian, two wheeler, car, truck, bus, traffic sign, traffic light
    # gen4 labels to keep: pedestrian, two wheeler, car
    # gen4 labels to remove: truck, bus, traffic sign, traffic light
    #
    # class_id in {0, 1, 2, 3, 4, 5, 6} in the order mentioned above
    keep = labels['class_id'] <= 2
    labels = labels[keep]
    return labels


def apply_filters(labels: np.ndarray,
                  split_type: str,
                  filter_cfg: Dict,
                  dataset_type: str = 'gen1') -> np.ndarray:
    assert isinstance(dataset_type, str)
    if dataset_type == 'gen4':
        labels = prophesee_remove_labels_filter_gen4(labels=labels)
    labels = crop_to_fov_filter(labels=labels, dataset_type=dataset_type)
    if filter_cfg["apply_psee_bbox_filter"]:
        labels = prophesee_bbox_filter(labels=labels, dataset_type=dataset_type)
    else:
        labels = conservative_bbox_filter(labels=labels)
    if split_type == 'train' and filter_cfg["apply_faulty_bbox_filter"]:
        labels = remove_faulty_huge_bbox_filter(labels=labels, dataset_type=dataset_type)
    return labels