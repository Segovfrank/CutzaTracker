import numpy as np

from ..utils import json_utils
from .constants import NAMO_MAX_HM3, data_dir
from .labels import load_labels
from .measure import read_measurements

TEST_FROM = "2024-01-01"
MAX_JUMP_KM2 = 0.5

def drop_outliers(scenes: list[dict]) -> list[dict]:
    # Let's measure prev and next so we check that we do not have drastic changes between lake reads.
    # For instance we cant have one date 16.2 km2 and the next one 10 km2. We use MAX_JUMP to measure the max tolerance before dropping
    
    kept = []
    for position, scene in enumerate(scenes):
        window_start = max(0, position - 2) # limit to 0
        window_end = position + 3
        window = scenes[window_start:window_end]
        
        window_areas = []
        for neighbor in window:
            window_areas.append(neighbor["area_km2"])
        
        usual_area = np.median(window_areas)
        distance = abs(scene["area_km2"] - usual_area)
        distance = abs(scene["area_km2"] - usual_area)
        if distance <= MAX_JUMP_KM2:
            kept.append(scene)
    return kept

def build_pairs() -> list[dict]:
    # Read the measured areas, one per datee
    area_by_date = {}
    for row in read_measurements():
        area = row["area_km2"]
        if area != "":
            date = row["date"]
            area_by_date[date] = float(area)
    
    # Put them in date order
    scenes = []
    for date in sorted(area_by_date):
        scenes.append({"date": date, "area_km2": area_by_date[date]})
        # Need to get neighbors so we drop any outstanding difference in the lake area
        scenes = drop_outliers(scenes)
    
    days = []
    for scene in scenes:
        days.append(scene["date"])
    
    storage = load_labels(days)    
    pairs = []
    
    for scene in scenes:
        if scene["date"] in storage:
            scene["storage_hm3"] = storage[scene["date"]]
            pairs.append(scene)
            
    return pairs

def columns(pairs: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    areas = []
    volumes = []
    for pair in pairs:
        area_km2 = pair["area_km2"]
        storage = pair["storage_hm3"]
        areas.append(area_km2)
        volumes.append(storage)
    return np.array(areas), np.array(volumes)

# We need to get the volume of the lake
def fit_area_volume_curve(areas: np.ndarray, volumes: np.ndarray) -> tuple[float, float]:
    # V = a * A^b because it behaves more like a valley opening up. As the surface grows, the space opens more
    b, log_a = np.polyfit(np.log(areas), np.log(volumes), 1)
    return float(np.exp(log_a)), float(b)

def predict(area_km2, a: float, b: float):
    return a * area_km2 ** b

def mean_abs_error(predicted: np.ndarray, actual: np.ndarray) -> float:
    return float(np.abs(predicted - actual).mean())

if __name__ == "__main__":
    pairs = build_pairs()
    train = []
    test = []
    for pair in pairs:
        if pair["date"] < TEST_FROM:
            train.append(pair)
        else:
            test.append(pair)
    print(f"{len(pairs)} pairs: {len(train)} to train (before {TEST_FROM}), {len(test)} to test")
    
    train_areas, train_volumes = columns(train)
    test_areas, test_volumes = columns(test)
    a, b = fit_area_volume_curve(train_areas, train_volumes)
    print(f"fitted on train:  V = {a:.5f} * A^{b:.2f}")
    
    error = mean_abs_error(predict(test_areas, a, b), test_volumes)
    guess = np.full(len(test), train_volumes.mean())
    baseline = mean_abs_error(guess, test_volumes)
    print(f"test error     {error:5.1f} hm3  {error / NAMO_MAX_HM3:5.1%} of NAMO")
    print(f"baseline error {baseline:5.1f} hm3  {baseline / NAMO_MAX_HM3:5.1%} of NAMO  (always guess the training mean)")
    
    a, b = fit_area_volume_curve(*columns(pairs))
    json_utils.save_json_to_local({"a": a, "b": b, "pairs": len(pairs)}, "model", data_dir)
    print(f"refitted on all {len(pairs)} pairs:  V = {a:.5f} * A^{b:.2f}")