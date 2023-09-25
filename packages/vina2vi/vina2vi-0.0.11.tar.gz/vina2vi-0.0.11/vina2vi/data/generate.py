import json
from importlib.resources import files

from vina2vi.util import uncased_vina_normalizer

def generate_test_data():
    data_dir = files("vina2vi.data")
    json_path = data_dir/"test_data_skeleton.json"
    with open(json_path, "r") as f:
        flesh = json.load(f)

    for author, works in flesh.items():
        for title in works:
            stem = uncased_vina_normalizer.normalize_str(
                title).replace(" ", "_")
            filename = f'{stem}.txt'
            text = (data_dir/filename).read_text().strip().replace("\n", " ")
            flesh[author][title] = text

    return flesh
