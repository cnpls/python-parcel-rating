from fedex_config import CONFIG_OBJ
from parcel_rating import App
import logging
import sys
import os
import pandas as pd

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
ROOT = os.path.dirname(os.path.abspath(__name__))
INSTANCE = os.path.join(ROOT, 'instance')


def test_init():
    app = App(CONFIG_OBJ, partition_size=0, storage_dir=INSTANCE)
    assert app
