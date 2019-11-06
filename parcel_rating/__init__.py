from fedex.services.rate_service import FedexRateServiceRequest
from fedex.tools.conversion import sobject_to_dict
import pandas as pd
import numpy as np
import os


class Service(object):
    def __init__(self, config):
        self.rating = FedexRateServiceRequest(config.fedex)
        self.config_data = config.data.set_index('Name')
        self.rating.RequestedShipment.DropoffType = self.config_value('DropoffType')
        self.rating.RequestedShipment.ServiceType = self.config_value('ServiceType')
        self.rating.RequestedShipment.PackagingType = self.config_value('PackagingType')
        self.rating.RequestedShipment.ShippingChargesPayment.PaymentType = self.config_value('PaymentType')
        # TODO:package1.PhysicalPackaging = 'BOX'

    def config_value(self, name):
        return self.config_data.loc[name, 'Value']

class App(Service):
    def __init__(self, config, storage_dir):
        # configure service
        Service.__init__(self, config)
        self.partition_size = int(self.config_value('PartitionSize'))

        if os.path.exists(storage_dir):
            self.storage_dir = storage_dir
        else:
            raise 'Storage directory path not found.'
