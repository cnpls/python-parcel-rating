from fedex.services.rate_service import FedexRateServiceRequest
import pandas as pd
import numpy as np
import logging
import traceback
import sys
import os


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Service(object):
    def __init__(self, config):
        self.rating = FedexRateServiceRequest(config.fedex)
        self.config_data = config.data.set_index('Name')
        self.debug = config.debug
        self.rating.RequestedShipment.DropoffType = self.config_value('DropoffType')
        self.rating.RequestedShipment.ServiceType = self.config_value('ServiceType')
        self.rating.RequestedShipment.PackagingType = self.config_value('PackagingType')
        self.rating.RequestedShipment.ShippingChargesPayment.PaymentType = self.config_value('PaymentType')

    def config_value(self, name):
        return self.config_data.loc[name, 'Value']

    @staticmethod
    def get_rate(response):
        detail = response.RateReplyDetails[0].RatedShipmentDetails[0]
        return ((detail.ShipmentRateDetail.TotalNetFedExCharge.Currency,
            detail.ShipmentRateDetail.TotalNetFedExCharge.Amount))

    def request_rate(self, data):
        logging.info('running %s.' % (data))
        # Shipper's address
        self.rating.RequestedShipment.Shipper.Address.PostalCode = data.origin_zip
        self.rating.RequestedShipment.Shipper.Address.CountryCode = data.origin_country

        # Recipient address
        self.rating.RequestedShipment.Recipient.Address.PostalCode = data.dest_zip
        self.rating.RequestedShipment.Recipient.Address.CountryCode = data.dest_country

        # package details
        package = self.rating.create_wsdl_object_of_type('RequestedPackageLineItem')
        package_weight = self.rating.create_wsdl_object_of_type('Weight')
        package_weight.Value = data.weight
        package_weight.Units = 'LB'
        package.Weight = package_weight
        package.PhysicalPackaging = 'BOX'
        package.GroupPackageCount = 1

        self.rating.add_package(package)
        try:
            self.rating.send_request()
            return self.get_rate(self.rating.response)
        except Exception as e:
            logging.warning('Fedex request failed. Errod: %s.' % (e))
            if self.debug: traceback.print_exc()
            return (np.nan, np.nan)

class App(Service):
    def __init__(self, config, storage_dir):
        # configure service
        Service.__init__(self, config)
        self.partition_size = int(self.config_value('PartitionSize'))

        if os.path.exists(storage_dir):
            self.storage_dir = storage_dir
        else:
            raise 'Storage directory path not found.'

    def run_partition(self, p):
        start_index = p * self.partition_size
        end_index = start_index + self.partition_size
        partition = self.shipments[start_index:end_index].copy()
        currencies = []
        rates = []
        for i in range(len(partition)):
            shipment = partition.iloc[i]
            currencies.append(self.request_rate(shipment)[0])
            rates.append(self.request_rate(shipment)[1])
        partition['parcel_rate'] = rates
        partition['parcel_currency'] = currencies
        filename = 'partition_%s.csv' % p
        filepath = os.path.join(self.storage_dir, filename)
        logging.info('Saving %s to %s.' % (partition.shape, filepath))
        partition.to_csv(filepath, index=False)
        return currencies, rates

    def rate(self, shipments):
        self.shipments = shipments
        n_partitions = int(np.ceil(len(shipments)/self.partition_size))
        currencies = []
        rates = []
        for p in range(n_partitions):
            c, r = self.run_partition(p)
            currencies += c
            rates += r
        self.shipments['parcel_rate'] = rates
        self.shipments['parcel_currency'] = currencies
        filepath = os.path.join(self.storage_dir, 'rating_output.csv')
        logging.info('Saving %s to %s.' % (self.shipments.shape, filepath))
        self.shipments.to_csv(filepath, index=False)
