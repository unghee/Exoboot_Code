import threading
from typing import Type

from concurrent import futures
import grpc
import Message_pb2
import Message_pb2_grpc

import config_util
import exoboot
import time

import asyncio

class ControllerCommunication(threading.Thread):
    def __init__(self,config: Type[config_util.ConfigurableConstants], exo_list,
                 new_params_event=Type[threading.Event], name = 'communication-thread'):
        super().__init__(name=name)
        self.daemon=True
        self.config=config
        self.new_params_event = new_params_event
        self.exo_list = exo_list
        self.stride_counter = 0
        self.temp_ankle_angle = []
        self.temp_ankle_angular_velocity = []
        #self.temp_counter = 0
        self.action_received = False
        self.start()

    #def storing_the_stride_values(self):


    def sending_data(self, ankle_a, ankle_v):
        for exo in self.exo_list:
            #print(exo.data.did_heel_strike, self.temp_ankle_angle, self.temp_ankle_angular_velocity)
            """if (exo.data.did_heel_strike == True):
                print("Here.............", self.stride_counter)
                self.stride_counter += 1
            #if(self.stride_counter == 1 and self.stride_counter == 2):
            self.temp_ankle_angle.append(exo.data.ankle_angle)
            self.temp_ankle_angular_velocity.append(exo.data.ankle_velocity)
            if(self.stride_counter == 2):
                print("Sending values")
                #print(exo.data.ankle_angle)"""
        print("Sending values")
        with grpc.insecure_channel(
                self.config.CONTROLLER_ALGORITHM_COMMUNICATION, options=(('grpc.enable_http_proxy',0), )) as channel:
            try:
                print("Sending.............")
                stub = Message_pb2_grpc.ControllerAlgorithmStub(channel)
                response = stub.ControllerMessage(
                    Message_pb2.ControllerPing(ankle_angle = ankle_a, ankle_angular_velocity = ankle_v))
                print('Response', response) 
                #Message_pb2.ControllerPing(ankle_angle = exo.data.ankle_angle, ankle_angular_velocity = exo.data.ankle_velocity))
            except grpc.RpcError as e:
                print("ERROR!!!!: ", e, "Check if the Computer IP is correct or if the computer side server is running")
            
            self.action_received = False
            self.stride_counter = 0
            self.temp_ankle_angle = []
            self.temp_ankle_angular_velocity = []

    class ActionState(Message_pb2_grpc.ActionStateServicer):
        def __init__(self, ControllerCommunication):
            self.ControllerCommunication = ControllerCommunication
        
        def ActionMessage(self,request,context):
            print("Action received", request.action_torque_profile)
            config_util.torque_profile = request.action_torque_profile
            self.ControllerCommunication.action_received = True
            return Message_pb2.Null()

    def server_to_receive_actions_for_the_controller(self):
        print(".... Starting the server on the controller.....")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        Message_pb2_grpc.add_ActionStateServicer_to_server(self.ActionState(self),server)
        server.add_insecure_port(self.config.ALGORITHM_CONTROLLER_COMMUNICATION)
        server.start()
        server.wait_for_termination()    

    def run(self):
        #while True:
        self.server_to_receive_actions_for_the_controller()