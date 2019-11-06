import pandas as pd
import numpy as np

class App:
    def __init__(self, config, partition_size, storage_dir):
        self.df = pd.DataFrame()
        self.config = config
        self.partition_size = partition_size
        self.storage_dir = storage_dir
