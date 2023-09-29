import os
from flask import Response
import requests

from tim_mod_gen_dep.src.models.sourceTypeEnum import SourceTypeEnum
from tim_mod_gen_dep.src.factories.timDataModelFactory import TimDataModelFactory

def addOne(x):
    return x + 1

# This class will serve as the interface between the Approval Web App Backend API and the TIM Model Generator/Depositor
class ApprovalWebAppBackendApiConnector:

    def __init__(self):
        if "APPROVAL_WEB_APP_ENDPOINT" not in os.environ:
            print("APPROVAL_WEB_APP_ENDPOINT not defined")
            exit(1)
        self.approvalWebAppEndpoint = os.environ["APPROVAL_WEB_APP_ENDPOINT"]

    def createUrgentTim(self, 
                        description, 
                        start_date, 
                        end_date, 
                        point, 
                        incident_code, 
                        sourceType:SourceTypeEnum, 
                        sourceDescription) -> Response:
        tim_data_model = TimDataModelFactory.generateUrgentPointModel(
            description,
            start_date,
            end_date,
            point,
            incident_code,
            sourceType,
            sourceDescription
        )
        return self.createGeneratedTim(self, tim_data_model)
    
    def createGeneratedTim(self, timDataModel) -> Response:
        json = timDataModel.toJson()

        # prepare post request
        url = self.approvalWebAppEndpoint + "/createGeneratedTim"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json, headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to create TIM")
        return response

    def createGeneratedTims(self, timDataModels):
        json = []
        for timDataModel in timDataModels:
            json.append(timDataModel.toJson())

        # prepare post request
        url = self.approvalWebAppEndpoint + "/createGeneratedTims"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json, headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to create TIMs")
        return response

    def getAll(self):
        # prepare get request
        url = self.approvalWebAppEndpoint + "/getAll"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to get TIMs")
        return response
    
    def delete(self, id):
        # prepare delete request
        url = self.approvalWebAppEndpoint + "/delete/" + id
        response = requests.delete(url)
        if response.status_code != 200:
            raise Exception("Failed to delete TIM")
        return response