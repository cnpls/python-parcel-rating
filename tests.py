from fedex_config import FEDEX_OBJ
from parcel_rating import App
import logging
import sys
import os
import pandas as pd

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
ROOT = os.path.dirname(os.path.abspath(__name__))
INSTANCE = os.path.join(ROOT, 'instance')

class Config:
    fedex = FEDEX_OBJ
    data = pd.read_csv(os.path.join(ROOT, 'example_service_config.csv'))

def test_init():
    app = App(Config, storage_dir=INSTANCE)
    assert app
