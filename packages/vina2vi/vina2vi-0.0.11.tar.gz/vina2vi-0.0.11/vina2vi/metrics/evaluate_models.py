from collections import OrderedDict, namedtuple

import numpy as np
import pandas as pd

from vina2vi.data.generate import generate_test_data
from vina2vi.metrics.indel import quick_eval
from vina2vi.models.baseline import DoNothingModel
from vina2vi.models.crf import CrfTrungTV
from vina2vi.models.char_based.bigram import Bigram
from vina2vi.models.word_based import tf_tuto_transformer


def main():
    # TODO
    # - [x] Better visualize the performances of diff models
    #       (e.g. DataFrame, pretty print, etc.)
    flesh = generate_test_data()
    gt = []
    for author, works in flesh.items():
        for title, text in works.items():
            gt.append(text)

    models = OrderedDict()
    ModelSpec = namedtuple("ModelSpec", ["name", "cased"])
    models[ModelSpec(name="baseline", cased=True)] = DoNothingModel()
    models[ModelSpec(name="bigram", cased=True)] = Bigram.from_pretrained()
    models[ModelSpec(name="crf_trungtv", cased=True)] = CrfTrungTV()
    models[ModelSpec(name="tf_tuto_transformer", cased=False)] = tf_tuto_transformer.Translator.from_pretrained()

    performance_df = pd.DataFrame(columns=["mean", "median"], dtype=np.float32)
    for spec, model in models.items():
        print(f'Evaluating {spec.name}...')
        performance = quick_eval(
            gt=gt,
            translate=model.translate,
            cased=spec.cased,
            verbose=True,
        )
        performance_df.loc[spec.name] = [performance["mean"], performance["median"]]

    default_display_precision = pd.options.display.precision
    pd.set_option("display.precision", 4)
    print(performance_df)
    pd.set_option("display.precision", default_display_precision)

if __name__ == "__main__":
    main()
