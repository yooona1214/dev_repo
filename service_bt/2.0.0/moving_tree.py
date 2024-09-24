'''
KT Robot BehaviorTree version 2.0.1

Copyright ⓒ 2023 kt corp. All rights reserved.

This is a proprietary software of kt corp, and you may not use this file except in
compliance with license agreement with kt corp. Any redistribution or use of this
software, with or without modification shall be strictly prohibited without prior written
approval of kt corp, and the copyright notice above does not evidence any actual or
intended publication of such software.
'''

import json

import py_trees
import operator

from ktmw_bt_interfaces.msg import TaskStatus, HaltStatus, AuthRequest, HRI, ItemReturn, SoundControl
from kt_nav_msgs.srv import SetNavGoal
from kt_nav_msgs.msg import NavStatus

from ktmw_srvmgr_lib.common import Idling, SubscribeTopic, TTSPlay, BGMPlay, EnqueueNextService, PublishTopic, SetBlackBoard, GetandSetBlackBoard,compareBBvariableforcorrect, compareBBvariableforincorrect
from ktmw_srvmgr_lib.hardware import (BoxOpen,BoxClose, BoxCtrl,  LEDControl,
                                      )
from ktmw_srvmgr_lib.navigation import NavigationStart, NavigationCancel, NavigationPause
from std_msgs.msg import UInt8

from slam_manager_msgs.srv import NavMapLoad
from ktmw_srvmgr_lib.common import ServiceCall, NoResponseCheck, GetCurrentTime, InitCount
from kt_msgs.msg import BoxStates

from config_manager_msgs.srv import GetPoiRoute

from data_manager_msgs.srv import GetFile

from std_msgs.msg import Empty, Bool
from std_msgs.msg import Int8MultiArray
import sensor_msgs.msg as sensor_msgs
from kt_msgs.msg import BoolCmdArray, LEDState, Location, LEDEffect

from std_srvs.srv import SetBool
from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm


SERVICE_NAME = 'moving-tree'
SERVICE_VERSION = '0.1.0'

class BB_init(py_trees.behaviour.Behaviour):
    """
    BB init
    """

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

        py_trees.blackboard.Blackboard.set('req_id', '')
        py_trees.blackboard.Blackboard.set('nav_status', '')
        py_trees.blackboard.Blackboard.set('mode', '')

        py_trees.blackboard.Blackboard.set('halt_status', '')
        #py_trees.blackboard.Blackboard.set('cancel_return_status', msg.cancel_return_status)
        py_trees.blackboard.Blackboard.set('cancel_return_tray_id', '')
        py_trees.blackboard.Blackboard.set('cancel_return_service_code', 0)
        py_trees.blackboard.Blackboard.set('cancel_return_service_id', '')
        py_trees.blackboard.Blackboard.set('cancel_return_task_id', '')
        py_trees.blackboard.Blackboard.set('cancel_return_return_location', '')
        py_trees.blackboard.Blackboard.set('cancel_return_moving_status', '')        

        py_trees.blackboard.Blackboard.set('dep_current_floor', 0)
        py_trees.blackboard.Blackboard.set('des_des_floor', '')
        py_trees.blackboard.Blackboard.set('des_get_off_point', '')
        py_trees.blackboard.Blackboard.set('des_current_floor', -1)
        py_trees.blackboard.Blackboard.set('abcd', '')        
        py_trees.blackboard.Blackboard.set('previous_tree', 'moving_tree')
        py_trees.blackboard.Blackboard.set('hri_status', '')
        py_trees.blackboard.Blackboard.set('admin_pw_from_ui', '') #
        py_trees.blackboard.Blackboard.set('admin_pw_type', '')
        py_trees.blackboard.Blackboard.set('remote_unlock', False)
        py_trees.blackboard.Blackboard.set('finished_flag', False)
        py_trees.blackboard.Blackboard.set('pre_nav_status', None)
        py_trees.blackboard.Blackboard.set('llm_bgm', '')
        py_trees.blackboard.Blackboard.set('llm_led_color', '')
        py_trees.blackboard.Blackboard.set('llm_led_effect', '')
        py_trees.blackboard.Blackboard.set('Tray_1_open_status', 1)
        py_trees.blackboard.Blackboard.set('Tray_2_open_status', 1)

    def update(self):
        return py_trees.common.Status.SUCCESS

class pause_result_check(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability


        # TODO TBD

    def update(self):
        self.bb1 = py_trees.blackboard.Blackboard.get('halt_type')
        self.bb2 = py_trees.blackboard.Blackboard.get('halt_result')

        if self.bb1 == 1 and self.bb2 == 0:
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING  

class Before_Mapchange_nextPOI(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        self.index = py_trees.blackboard.Blackboard.get('route_index_num') 
        self.next_poi =  py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/waypoint_poi')
        py_trees.blackboard.Blackboard.set('route_index_num_+1_waypoint_poi', self.next_poi)
        

        return py_trees.common.Status.SUCCESS

class Before_EV_Tree(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        self.index = py_trees.blackboard.Blackboard.get('route_index_num') 
        self.next_floor =  py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/floor')
        self.map_name =  py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/map_name')
        py_trees.blackboard.Blackboard.set('route_index_num_+1_floor', self.next_floor)
        py_trees.blackboard.Blackboard.set('route_index_num_+1_map_name', self.map_name)
        

        return py_trees.common.Status.SUCCESS
    




class unset_current(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD



    def update(self):
        a = py_trees.blackboard.Blackboard.get('poi_len')
        py_trees.blackboard.Blackboard.set('poi_success_check',None)
        for i in range(a):
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/waypoint_poi','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_name','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/zone','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/floor','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/is_ev',False)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_change',False)

        for i in range(3):
            py_trees.blackboard.Blackboard.set('current_service_id','')
            py_trees.blackboard.Blackboard.set('current_goal_count',-1)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_service_code','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_task_id','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_tray_id','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_goal_id','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_seq',0)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_lock_option',0)

        return py_trees.common.Status.SUCCESS

class set_current(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        py_trees.blackboard.Blackboard.set('goal_index_num', 1)
        py_trees.blackboard.Blackboard.set('route_index_num', 1)
        py_trees.blackboard.Blackboard.set('cancel_flag', 1)

        py_trees.blackboard.Blackboard.set('current_service_id', py_trees.blackboard.Blackboard.get('cancel_return_service_id'))
        py_trees.blackboard.Blackboard.set('current_goal_count', 1)   ##########
        py_trees.blackboard.Blackboard.set('1/current_service_code', py_trees.blackboard.Blackboard.get('cancel_return_service_code'))
        py_trees.blackboard.Blackboard.set('1/current_task_id', py_trees.blackboard.Blackboard.get('cancel_return_task_id'))
        py_trees.blackboard.Blackboard.set('1/current_tray_id', py_trees.blackboard.Blackboard.get('cancel_return_tray_id'))
        py_trees.blackboard.Blackboard.set('1/current_goal_id', py_trees.blackboard.Blackboard.get('cancel_return_return_location'))
        py_trees.blackboard.Blackboard.set('1/current_seq', 1)
        py_trees.blackboard.Blackboard.set('1/current_lock_option', 1)

        return py_trees.common.Status.SUCCESS


class FleetLineupStatus(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    #def initialise(self):


    def update(self):
        self.bb1 = py_trees.blackboard.Blackboard.get('req_id')
        self.bb2 = py_trees.blackboard.Blackboard.get('nav_status')
        if self.bb1 == 2 and self.bb2 == 'finished':
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING    


class MovingStatus(py_trees.behaviour.Behaviour):
    def __init__(self,  name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    #def initialise(self):


    def update(self):
        self.bb1 = py_trees.blackboard.Blackboard.get('mode')
        self.bb2 = py_trees.blackboard.Blackboard.get('nav_status')

        if self.bb1 == 'normal' and self.bb2 == 'moving':
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING    


class arrivedStatus(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability


        # TODO TBD

    def update(self):
        self.bb1 = py_trees.blackboard.Blackboard.get('mode')
        self.bb2 = py_trees.blackboard.Blackboard.get('nav_status')

        if self.bb1 == 'normal' and self.bb2 == 'finished':
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING    




class SetHaltBlackBoard(py_trees.behaviour.Behaviour):
    """
    BB SetHaltBlackBoard
    """

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    #def initialise(self):

    def update(self):
        py_trees.blackboard.Blackboard.set('cancel_tray_num', len(py_trees.blackboard.Blackboard.get('cancel_return_tray_id')))

                
        return py_trees.common.Status.SUCCESS
    


class SetRouteIndex(py_trees.behaviour.Behaviour):
    """
    BB SetRouteIndex
    """

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    # def initialise(self):


    def update(self):
        self.index = py_trees.blackboard.Blackboard.get('route_index_num')

        py_trees.blackboard.Blackboard.set('route_index_num_+1', self.index+1)

        py_trees.blackboard.Blackboard.set('route_index_num_waypoint_poi', py_trees.blackboard.Blackboard.get("r"+str(self.index)+'/waypoint_poi'))
        py_trees.blackboard.Blackboard.set('route_index_num_map_name', py_trees.blackboard.Blackboard.get("r"+str(self.index)+'/map_name'))
        py_trees.blackboard.Blackboard.set('route_index_num_zone', py_trees.blackboard.Blackboard.get("r"+str(self.index)+'/zone'))
        py_trees.blackboard.Blackboard.set('route_index_num_floor', py_trees.blackboard.Blackboard.get("r"+str(self.index)+'/floor'))
        py_trees.blackboard.Blackboard.set('route_index_num_is_ev', py_trees.blackboard.Blackboard.get("r"+str(self.index)+'/is_ev'))
        py_trees.blackboard.Blackboard.set('route_index_num_map_change', py_trees.blackboard.Blackboard.get("r"+str(self.index)+ '/map_change'))

        return py_trees.common.Status.SUCCESS
    
class SetRouteIndexforNextPOI(py_trees.behaviour.Behaviour):
    """
    BB SetRouteIndex
    """

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    # def initialise(self):


    def update(self):
        self.index = py_trees.blackboard.Blackboard.get('route_index_num')
        self.next_next_index = py_trees.blackboard.Blackboard.get('route_index_num') + 2

        py_trees.blackboard.Blackboard.set('route_index_num_+1_waypoint_poi', py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/waypoint_poi'))
        py_trees.blackboard.Blackboard.set('route_index_num_+1_map_name', py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/map_name'))
        py_trees.blackboard.Blackboard.set('route_index_num_+1_zone', py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/zone'))
        py_trees.blackboard.Blackboard.set('route_index_num_+1_floor', py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/floor'))
        py_trees.blackboard.Blackboard.set('route_index_num_+1_is_ev', py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+'/is_ev'))
        py_trees.blackboard.Blackboard.set('route_index_num_+1_map_change', py_trees.blackboard.Blackboard.get("r"+str(self.index+1)+ '/map_change'))
        py_trees.blackboard.Blackboard.set('route_index_num_+2', self.next_next_index)

        return py_trees.common.Status.SUCCESS


class SetGoalIndex(py_trees.behaviour.Behaviour):
    """
    BB SetGoalIndex
    """

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def initialise(self):
        self.index = py_trees.blackboard.Blackboard.get('goal_index_num')
        py_trees.blackboard.Blackboard.set('goal_index_num_current_service_id', py_trees.blackboard.Blackboard.get('current_service_id'))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_service_code', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_service_code'))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_task_id', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_task_id'))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_tray_id', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_tray_id'))
        py_trees.blackboard.Blackboard.set('tray_num', len(py_trees.blackboard.Blackboard.get('goal_index_num_current_tray_id')))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_goal_id', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_goal_id' ))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_seq', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_seq' ))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_lock_option', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_lock_option' ))



    def update(self):

            
        return py_trees.common.Status.SUCCESS


class GetandSetTrayBlackBoard(py_trees.behaviour.Behaviour):
    """
    BB init
    """

    def __init__(self, BB_variable,  name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable = BB_variable


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        
        py_trees.blackboard.Blackboard.set(self.BB_variable, 'Tray_'+str(py_trees.blackboard.Blackboard.get('hri_tray_id'))+'_stuff_status')
                
        return py_trees.common.Status.SUCCESS        



class GetTrayInfo(py_trees.behaviour.Behaviour):
    """
    BB init
    """

    def __init__(self,  name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        tray_list = py_trees.blackboard.Blackboard.get('goal_index_num_current_tray_id') # array('B', [1, 2])

        for i in range(len(tray_list)):
            py_trees.blackboard.Blackboard.set('tray'+str(i+1), tray_list[i]) # tray1 / tray2
                
        return py_trees.common.Status.SUCCESS   


class Reduce_1(py_trees.behaviour.Behaviour):
    """
    BB init
    """

    def __init__(self, BB_variable, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable = BB_variable

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        self.bb_value=py_trees.blackboard.Blackboard.get(self.BB_variable) -1 
        py_trees.blackboard.Blackboard.set(self.BB_variable, self.bb_value)
                
        return py_trees.common.Status.SUCCESS    

class led_bgm(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

    def update(self):
        self.control_value = py_trees.blackboard.Blackboard.get('current_service_id')
        self.control_values = list(self.control_value)
        
        self.first_bgm = self.control_values[0]
        self.second_led = self.control_values[1]
        self.thirld_led = self.control_values[2]

        py_trees.blackboard.Blackboard.set('llm_bgm', self.first_bgm)
        py_trees.blackboard.Blackboard.set('llm_led_color', self.second_led)
        py_trees.blackboard.Blackboard.set('llm_led_effect', self.thirld_led)
                
        return py_trees.common.Status.SUCCESS     

def halt_reserve():

    seq = py_trees.composites.Sequence()

    reserve_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'reserve_check',
        check=py_trees.common.ComparisonExpression(
            variable="halt_status",
            value='reserve',
            operator= operator.eq
        )
        )

    cancel_goal = NavigationCancel()

    cancel_alarm =  PublishTopic(
            name='cancel_alarm',
            topic_name='ktmw_bt/task_status',
            topic_type = TaskStatus,
            msg_generate_fn=lambda: TaskStatus(
                service_code=0,
                task_id='',
                goal_id='',
                current_goal_id='',
                tray_id=[0],
                task_status='nav_cancel',
                action='nav_cancel',
                action_target='nav_cancel',
                action_result=True
                )
            )     
    multirobot_available_f = PublishTopic(
                                name='multirobot_available_f',
                                topic_name='ktmw_bt/task_status',
                                topic_type = TaskStatus, #TODO
                                msg_generate_fn=lambda: TaskStatus(
                                    service_id='',
                                    service_code=0,
                                    task_id='',
                                    goal_id='',
                                    current_goal_id='',
                                    tray_id=[0],             
                                    task_status = 'moving',
                                    action = 'multi_robot',
                                    action_target = 'multi_robot',
                                    action_result = False
                                    )   
                                ) 


    go_to_BB_clear = EnqueueNextService(service_name='BB_clear', service_version='2.0.0')
        
    seq.add_children([reserve_check,multirobot_available_f, cancel_goal, cancel_alarm, go_to_BB_clear])
    
    return seq

def time_delay_check_seq():

    
    seq = py_trees.composites.Sequence()

    task_fail_alarm = PublishTopic(
                            name='user_input_delayed_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
                                tray_id=[0],             
                                task_status = 'task_fail',
                                action = 'user_input_delayed2',
                                action_target = 'tray_'+str(py_trees.blackboard.Blackboard.get('tray1')),
                                action_result = True
                                )   
                            )
    
    user_input_delay_alarm = PublishTopic(
                            name='time_delay_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'user_input_delayed',
                                action = 'user_input_delayed',
                                action_target = 'user_input_delayed',
                                action_result = True
                                )   
                            )

    tray_closed_1 = BoxClose(position=1, x=1, y=1)
    tray_closed_2 = BoxClose(position=1, x=1, y=2)


    seq.add_children([no_response_check(time11 = 'user_input_duration'), task_fail_alarm, user_input_delay_alarm, tray_closed_1, tray_closed_2]) # 600
    return seq



def battery_under_15():

    battery_seq = py_trees.composites.Sequence()    


    battery_under_15_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'battery_under_15_check',
                check=py_trees.common.ComparisonExpression(
                variable='current_battery_level',
                value=0.15,
                operator= operator.lt
            )
        )

    battery_alarm = PublishTopic(
                            name='battery_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'unavailable_battery',
                                action = 'unavailable_battery',
                                action_target = 'unavailable_battery',
                                action_result = True
                                )   
                            )
    
    cancel_goal = NavigationCancel()

    cancel_alarm =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )     

    BGM_off_cancel = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)


    go_to_low_battery_tree = EnqueueNextService(
        service_name='low_battery_tree', service_version='2.0.0'
    )
    multirobot_available_f6 = PublishTopic(
                            name='multirobot_available_f6',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = False
                                )   
                            ) 
    battery_seq.add_children([battery_under_15_check, multirobot_available_f6, battery_alarm, cancel_goal, cancel_alarm, BGM_off_cancel, go_to_low_battery_tree ])
    
    return battery_seq

# 비상정지 체크(무빙, ev, charging 캔슬 적용)
def emergency_button_check():

    seq = py_trees.composites.Sequence()

    cancel_goal = NavigationCancel()

    cancel_alarm =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )   
    

    emergency_button_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'emergency_button_check',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button2",
            value=True,
            operator=operator.eq
        )
    )
    
    def request_generate_fn_qr_node_off():
        request = SetBool.Request()
        request.data = False
        return request
    def response_QR_Node(response):
        print(response.success)

    QR_Node_off = ServiceCall(
        service_name='qr/scan_enable',
        service_type= SetBool,
        request_generate_fn=request_generate_fn_qr_node_off,
        response_fn= response_QR_Node, name='QR_Node_off'

    )

    Driving_mode_off = PublishTopic(
        name='Driving_mode_off',
        topic_name='qr_pose_out_mode',
        topic_type = UInt8,
        msg_generate_fn=lambda: UInt8(
            data=0
            )
        )
    
    go_to_emergency_tree = EnqueueNextService(service_name='emergency_tree', service_version='2.0.0')

    multirobot_available_f6 = PublishTopic(
                            name='multirobot_available_f6',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = False
                                )   
                            ) 

    #moving, ev, charging --> cancel_goal
    seq.add_children([emergency_button_check, multirobot_available_f6, cancel_goal, cancel_alarm, go_to_emergency_tree])

    return seq

def check_manual_charge(): 

    seq = py_trees.composites.Sequence()

    manual_contacted_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_contacted_check',
        check=py_trees.common.ComparisonExpression(
            variable="manual_contacted",
            value=1,
            operator=operator.eq
        )
    )

    cancel_goal = NavigationCancel()

    cancel_alarm =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )    

    multirobot_available_f = PublishTopic(
                                name='multirobot_available_f',
                                topic_name='ktmw_bt/task_status',
                                topic_type = TaskStatus, #TODO
                                msg_generate_fn=lambda: TaskStatus(
                                    service_id='',
                                    service_code=0,
                                    task_id='',
                                    goal_id='',
                                    current_goal_id='',
                                    tray_id=[0],             
                                    task_status = 'moving',
                                    action = 'multi_robot',
                                    action_target = 'multi_robot',
                                    action_result = False
                                    )   
                                ) 
    
    go_to_manualcharging = EnqueueNextService(
        service_name='manual_charging_tree', service_version='2.0.0'
    )

    seq.add_children([manual_contacted_check,multirobot_available_f, cancel_goal, cancel_alarm, go_to_manualcharging ])

    return seq

#수동운전 진입
def check_manual_drive(): 

    seq = py_trees.composites.Sequence()


    manual_drive_button_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_drive_button_check',
        check=py_trees.common.ComparisonExpression(
            variable="button_manual_driving",
            value=True,
            operator=operator.eq
        )
    )

    nav_cancel = NavigationCancel()

    cancel_alarm =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )   

    # manual_LED_dimming_front = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_SEQUENTIAL_LED_OFF, 
    #     period_ms=2000,
    #     on_ms=0,
    #     repeat_count=0)
    
    # manual_LED_dimming_rear = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_SEQUENTIAL_LED_OFF, 
    #     period_ms=2000,
    #     on_ms=0,
    #     repeat_count=0)    

    manual_LED_dimming_front = PublishTopic(
                name='manual_LED_dimming_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  


    manual_LED_dimming_rear = PublishTopic(
                name='manual_LED_dimming_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    
    
    go_to_manual_drive = EnqueueNextService(
        service_name='manualdriving_tree', service_version='2.0.0'
    )

    multirobot_available_f5 = PublishTopic(
                            name='multirobot_available_f5',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = False
                                )   
                            ) 

    seq.add_children([manual_drive_button_check, multirobot_available_f5, nav_cancel, cancel_alarm,  manual_LED_dimming_front, manual_LED_dimming_rear, go_to_manual_drive  ])

    return seq


def admin_password_check_seq():
    
    seq = py_trees.composites.Sequence()

    

    wait_for_pw_req = py_trees.behaviours.WaitForBlackboardVariableValue(
        name='wait_for_pw_req',
        check=py_trees.common.ComparisonExpression(
        variable='admin_pw_type',
        value='admin',
        operator= operator.eq
        )
    )

    wait_for_pw_req2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name='wait_for_pw_req',
        check=py_trees.common.ComparisonExpression(
        variable='admin_pw_type',
        value='admin',
        operator= operator.eq
        )
    )


    unset_pw_req1 = SetBlackBoard(BB_variable='admin_pw_type', BB_value='')

    final_seq = py_trees.composites.Sequence()


    seq6 =py_trees.composites.Sequence()

    par3 = py_trees.composites.Parallel(
        name="par3",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq6],
            synchronise=False
        )
    ) 

    
    seq7 =py_trees.composites.Sequence()    

    pw_correct_check = compareBBvariableforcorrect(BB_variable1 = 'admin_pw',
                                         BB_variable2 = 'admin_pw_from_ui')
    
    pw_incorrect_check = compareBBvariableforincorrect(BB_variable1 = 'admin_pw',
                                         BB_variable2 = 'admin_pw_from_ui')
    

    


    
    failed_count_alarm = PublishTopic(
                            name='failed_count_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
                                tray_id=[0],             
                                task_status = 'admin_auth_check',
                                action = 'admin_auth_fail',
                                action_target = 'tray_',
                                action_result = False
                                )   
                            )
    

    auth_checkced_alarm = PublishTopic(
                            name='auth_checkced_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
                                tray_id=[0],             
                                task_status = 'admin_auth_check',
                                action = 'admin_auth_success',
                                action_target = 'tray_',
                                action_result = True
                                )   
                            )


    unset_admin_pw_from_ui2 = SetBlackBoard(BB_variable='admin_pw_from_ui', BB_value='')

    tts_password_fail1= TTSPlay(tts_name='password_fail', play=True, sequence=True)


    # 비밀번호 틀렸을 때 - 점멸
    # led_start_on_pw_incorrect_f = LEDControl(
    #     color=LEDControl.COLOR_BLUE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)

    # led_start_on_pw_incorrect_r = LEDControl(
    #     color=LEDControl.COLOR_BLUE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)
    
    led_start_on_pw_incorrect_f = PublishTopic(
                name='led_start_on_pw_incorrect_f',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )  


    led_start_on_pw_incorrect_r = PublishTopic(
                name='led_start_on_pw_incorrect_r',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )  
  


    seq.add_children([wait_for_pw_req, par3])
    par3.add_children([seq6, seq7])
    seq6.add_children([pw_correct_check, auth_checkced_alarm])
    seq7.add_children([pw_incorrect_check, tts_password_fail1, led_start_on_pw_incorrect_f, led_start_on_pw_incorrect_r, unset_admin_pw_from_ui2, unset_pw_req1, failed_count_alarm, wait_for_pw_req2])
    return seq

def tray_stuff_change_check(tray_id):

    tray = tray_id

    par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 

    seq1 = py_trees.composites.Sequence()
    seq2 = py_trees.composites.Sequence()
    tray_stuff_full_check_forward = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray_stuff_full_check_forward',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_'+str(tray)+'_stuff_status',
                value=True,
                operator= operator.eq
            )
        )    
    
    tray_stuff_empty_check_forward = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray_stuff_empty_check_forward',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_'+str(tray)+'_stuff_status',
                value=False,
                operator= operator.eq
            )
        )        
    
    tray_stuff_empty_check_backward = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray_stuff_empty_check_backward',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_'+str(tray)+'_stuff_status',
                value=False,
                operator= operator.eq
            )
        )    
    
    tray_stuff_full_check_backward = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray_stuff_full_check_backward',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_'+str(tray)+'_stuff_status',
                value=True,
                operator= operator.eq
            )
        )        
    
    par.add_children([seq1, seq2])
    seq1.add_children([tray_stuff_full_check_forward, tray_stuff_empty_check_forward ])
    seq2.add_children([tray_stuff_empty_check_backward, tray_stuff_full_check_backward ])
    
    return par

def no_response_check(time11):

    seq = py_trees.composites.Sequence()

    time_check = NoResponseCheck(time1=time11)

    #시작 시간 입력
    get_start_time = GetCurrentTime()

    par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[time_check],
            synchronise=False
        )        
    )

    seq1 = py_trees.composites.Sequence()

    wait_for_user_input = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_for_user_input',
                check=py_trees.common.ComparisonExpression(
                variable='hri_user_input',
                value=True,
                operator= operator.eq
            )
        )

    init_count = InitCount()

    unset_user_input = py_trees.behaviours.UnsetBlackboardVariable('hri_user_input')

    par1 = py_trees.composites.Parallel(
        name="par1",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )

    seq.add_children([get_start_time, par])
    par.add_children([time_check, seq1])
    seq1.add_children([par1, init_count, unset_user_input])
    par1.add_children([wait_for_user_input, tray_stuff_change_check(tray_id=1), tray_stuff_change_check(tray_id=2)])

    return seq



def tray_action_seq_manual():

    seq = py_trees.composites.Sequence()

    wait_hri_tray_open_cmd = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_hri_tray_open_cmd',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Tray_open',
                operator= operator.eq
            )
        )
    
        # tray 전체 상태 한번에 받을 수 있다면 교체 예정
    tray1_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=1,
            operator= operator.eq
            )
        )
    
    tray2_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=1,
            operator= operator.eq
            )
        )
    


    par0 = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )


    tray1_open_seq = py_trees.composites.Sequence()
    tray2_open_seq = py_trees.composites.Sequence()

    wait_hri_tray1_id_cmd = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_hri_tray1_id_cmd',
                check=py_trees.common.ComparisonExpression(
                variable='hri_tray_id',
                value=1,
                operator= operator.eq
            )
        )
    
    wait_hri_tray2_id_cmd = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_hri_tray2_id_cmd',
                check=py_trees.common.ComparisonExpression(
                variable='hri_tray_id',
                value=2,
                operator= operator.eq
            )
        )

    tray_close1 = BoxClose(position=1, x=1, y=1)
    tray_close2 = BoxClose(position=1, x=1, y=2)


    tray_open1 = BoxOpen(position=1, x=1, y=1)
    tray_open2 = BoxOpen(position=1, x=1, y=2)


    tray_id_unset1 = py_trees.behaviours.UnsetBlackboardVariable('hri_tray_id')
    tray_id_unset2 = py_trees.behaviours.UnsetBlackboardVariable('hri_tray_id')


    tray1_closed_check_3 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=1,
            operator= operator.eq
            )
        )
    



    tray2_closed_check_3 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=1,
            operator= operator.eq
            )
        )

    seq.add_children([wait_hri_tray_open_cmd, par0])
    par0.add_children([tray1_open_seq, tray2_open_seq])
    
    tray1_open_seq.add_children([wait_hri_tray1_id_cmd, tray_not_ing_check(), tray_close2, tray2_closed_check, tray_open1, tray_id_unset1, tray1_closed_check_3])
  
    tray2_open_seq.add_children([wait_hri_tray2_id_cmd, tray_not_ing_check(), tray_close1, tray1_closed_check, tray_open2, tray_id_unset2, tray2_closed_check_3])

    return seq

def only_check_tray_stuck():
    seq = py_trees.composites.Sequence()

    tray1_stuck_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray1_stuck_check',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_1_exception_status',
                value=1,  
                operator= operator.eq
            )
        )
    
    tray2_stuck_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray2_stuck_check',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_2_exception_status',
                value=1,  
                operator= operator.eq
            )
        )    
    
    par_one = py_trees.composites.Parallel(
        name="par_one",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 

    unset_tray1_exception = SetBlackBoard('Tray_1_exception_status', 0)
    unset_tray2_exception = SetBlackBoard('Tray_2_exception_status', 0)


    stuck_alarm = PublishTopic(
        name='stuck_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='tray_stuck',
            action='tray_stuck',
            action_target='tray',
            action_result=True
            )
        )

    seq.add_children([par_one, unset_tray1_exception, unset_tray2_exception, stuck_alarm])
    par_one.add_children([tray1_stuck_check, tray2_stuck_check])


    return seq


def hri_finished_and_alarm():

    seq = py_trees.composites.Sequence()

    hri_finished_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'hri_finished_check',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Finished_check',
                operator= operator.eq
            )
        )

    task_finished_alarm = PublishTopic(
                            name='task_finished_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
                                tray_id=[0],             
                                task_status = 'task_finished',
                                action = 'task_finished',
                                action_target = 'tray'+str(py_trees.blackboard.Blackboard.get('goal_index_num_current_tray_id')),
                                action_result = True
                                )   
                            )
    
    par_tray_all_closed = py_trees.composites.Parallel(
        name="par_tray_all_closed",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )        
    )

    tray1_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=1,
            operator= operator.eq
            )
        )
    
    tray2_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=1,
            operator= operator.eq
            )
        )

    seq.add_children([hri_finished_check, par_tray_all_closed, task_finished_alarm])
    par_tray_all_closed.add_children([tray1_closed_check, tray2_closed_check])


    return seq


def opened_tray_check_and_close():
        
    par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )  
    
    seq_tray1_opened = py_trees.composites.Sequence()
    seq_tray2_opened = py_trees.composites.Sequence()

    check_tray1_opened = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_tray1_opened',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=2,
            operator= operator.eq
            )
        )
    
    set_tray_opened_1 = SetBlackBoard('tray_opened', 1)


    check_tray2_opened = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_tray2_opened',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=2,
            operator= operator.eq
            )
        )
    
    set_tray_opened_2 = SetBlackBoard('tray_opened',2)
    
    def request_generate_fn_close_opened_tray():
        request = BoxCtrl.Request()
        request.data.box_command = 2
        request.data.location.position = 1
        request.data.location.x = 1
        request.data.location.y = py_trees.blackboard.Blackboard.get('tray_opened')
        return request
    def response_fn_close_opened_tray(response):
        print(response.success)

    close_opened_tray = ServiceCall(
        service_name='hardware_manager/box/box_control',
        service_type= BoxCtrl,
        request_generate_fn=request_generate_fn_close_opened_tray,
        response_fn= response_fn_close_opened_tray, name='close_opened_tray'

    )

    seq = py_trees.composites.Sequence()

    par_tray_all_closed = py_trees.composites.Parallel(
        name="par_tray_all_closed",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )        
    )

    tray1_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=1,
            operator= operator.eq
            )
        )
    
    tray2_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=1,
            operator= operator.eq
            )
        )
    
    par_tray = py_trees.composites.Parallel(
        name="par_tray",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )  

    par_tray.add_children([par_tray_all_closed, seq])
    par_tray_all_closed.add_children([tray1_closed_check, tray2_closed_check])
    seq.add_children([par, close_opened_tray])
    par.add_children([seq_tray1_opened, seq_tray2_opened])
    seq_tray1_opened.add_children([check_tray1_opened, set_tray_opened_1])
    seq_tray2_opened.add_children([check_tray2_opened, set_tray_opened_2])

    return par_tray


def parallel_get_msg_toBB():

    par =  py_trees.composites.Parallel(
        name="parallel_get_msg_toBB",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )        
    )



    def on_msg_fn_error_status(msg):

        alarm_code = msg.alarm_code
        alarm_code_list = list(alarm_code)
        py_trees.blackboard.Blackboard.set('alarm_code', alarm_code)

        #[error level] 0: CLEARED, 1: NOTICE, 2. WARN, 3. MINOR, 4. MAJOR, 5. CRITICAL, 6. FATAL, 7. EMERGENCY
        py_trees.blackboard.Blackboard.set('alarm_code_error_level', int(alarm_code_list[1]))

        #[error source1] 0: CRITICAL, 1: MC, 2: Robot Core Component
        py_trees.blackboard.Blackboard.set('alarm_code_error_source1', int(alarm_code_list[2]))

        #[error source2] error source1 --> 2: Robot Core Component 
        # 0: BT, 1: RM_AGENT, 2: FOTA_AGENT, 3: DRIVING_CORE, 4: AOSP, 5: HW
        py_trees.blackboard.Blackboard.set('alarm_code_error_source2', int(alarm_code_list[3]))        

        py_trees.blackboard.Blackboard.set('alarm_error_code_1', int(alarm_code_list[5]))        
        py_trees.blackboard.Blackboard.set('alarm_error_code_2', int(alarm_code_list[6]))        
        py_trees.blackboard.Blackboard.set('alarm_error_code_3', int(alarm_code_list[7]))        
        py_trees.blackboard.Blackboard.set('alarm_error_code_4', int(alarm_code_list[8]))     

        py_trees.blackboard.Blackboard.set('alarm_message', msg.message)                     

    error_set_to_BB =  SubscribeTopic(
        topic_name='popup/notify_alarm',
        topic_type=NotifyAlarm,
        on_msg_fn=on_msg_fn_error_status,
        name='error_set_to_BB')

    #이벤트성 버튼 불리안

    def on_msg_fn_button_status(msg):
        # 0: power off, 1: power_reboot, 2: manual_driving, 3: emergency, 4: power_on
        py_trees.blackboard.Blackboard.set('button_power_off', msg.data[0].data)
        py_trees.blackboard.Blackboard.set('button_power_reboot', msg.data[1].data)            
        py_trees.blackboard.Blackboard.set('button_manual_driving', msg.data[2].data)            
        py_trees.blackboard.Blackboard.set('emergency_button', msg.data[3].data)  #button_emergency           
        py_trees.blackboard.Blackboard.set('button_power_on', msg.data[4].data)            

    button_status_to_BB =  SubscribeTopic(
        topic_name='button/button_action_cmd',
        topic_type=BoolCmdArray,
        on_msg_fn=on_msg_fn_button_status,
        name='button_status_to_BB')       

    def on_msg_fn_emergency_button(msg):
            py_trees.blackboard.Blackboard.set('emergency_button2', msg.data[0].data) #True: 버튼 눌림 # False: 버튼 해제

    emergency_button_info_to_BB =  SubscribeTopic(
            topic_name='button/button_status',
            topic_type=BoolCmdArray,
            on_msg_fn=on_msg_fn_emergency_button,
            name='emergency_button_info_to_BB')    
    
    # 배터리 
    def on_msg_batt(msg):
        py_trees.blackboard.Blackboard.set('current_battery_level', msg.percentage) #0.0 ~ 1.0

    battery_state_to_BB = SubscribeTopic(
        topic_name="bms/battery_state",
        topic_type=sensor_msgs.BatteryState,
        on_msg_fn=on_msg_batt,
        name='Battery_state_to_BB'
    )           


    # 충전 여부 data[0]: 충전 여부, data[1]: 오토컨택 여부, data[2]: 수동컨택 여부
    def on_msg_charg(msg):
        py_trees.blackboard.Blackboard.set('is_charging', msg.data[0])
        py_trees.blackboard.Blackboard.set('auto_contacted', msg.data[1])
        py_trees.blackboard.Blackboard.set('manual_contacted', msg.data[2]) 


    charging_state_to_BB = SubscribeTopic(
        topic_name="bms/charging_state",
        topic_type= Int8MultiArray,
        on_msg_fn=on_msg_charg,
        name='charging_state_to_BB'
    )   

    #NAV Status
    def on_msg_fn_nav_status_to_BB(msg):
        py_trees.blackboard.Blackboard.set('req_id', msg.req_id.command)
        py_trees.blackboard.Blackboard.set('mode', msg.mode)
        py_trees.blackboard.Blackboard.set('nav_status', msg.state)
        py_trees.blackboard.Blackboard.set('current_label', msg.current_label)
        py_trees.blackboard.Blackboard.set('goal_label', msg.goal_label)

    nav_status_to_BB = SubscribeTopic(
        topic_name="nav/status",
        topic_type=NavStatus,
        on_msg_fn=on_msg_fn_nav_status_to_BB,
        name='Nav_status_to_BB'
    )
    
    #정지/취소 정보 to BB
    def on_msg_fn_halt_Status(msg):
        py_trees.blackboard.Blackboard.set('halt_status', msg.halt_status)
        #py_trees.blackboard.Blackboard.set('cancel_return_status', msg.cancel_return_status)
        py_trees.blackboard.Blackboard.set('cancel_return_tray_id', msg.tray_id)
        py_trees.blackboard.Blackboard.set('cancel_return_service_code', msg.service_code)
        py_trees.blackboard.Blackboard.set('cancel_return_service_id', msg.service_id)
        py_trees.blackboard.Blackboard.set('cancel_return_task_id', msg.task_id)
        py_trees.blackboard.Blackboard.set('cancel_return_return_location', msg.return_location)
        py_trees.blackboard.Blackboard.set('cancel_return_moving_status', msg.return_result)
        py_trees.blackboard.Blackboard.set('cancel_return_is_tray', msg.is_tray)
    
    halt_Status_to_BB = SubscribeTopic(
        topic_name='ktmw_bt/halt_status',
        topic_type=HaltStatus,
        on_msg_fn=on_msg_fn_halt_Status,
        name='halt_status_to_BB'
    )


    #item_return
    def on_msg_fn_item_return(msg):
        py_trees.blackboard.Blackboard.set('item_return_tray_id', msg.tray_id) #uint8
        py_trees.blackboard.Blackboard.set('item_return_check', msg.check) #bool

    item_return_msgs_to_BB =  SubscribeTopic(
        topic_name='ktmw_bt/item_return',
        topic_type=ItemReturn,
        on_msg_fn=on_msg_fn_item_return,
        name='item_return_msgs_to_BB')
    
    
    def on_msg_fn_pw_req(msg):
        py_trees.blackboard.Blackboard.set('admin_pw_type', msg.type) #user/admin 
        py_trees.blackboard.Blackboard.set('admin_pw_tray_id', msg.tray_id) #string
        py_trees.blackboard.Blackboard.set('admin_pw_from_ui', msg.pw) #uint8

    admin_pw_req_msgs_to_BB =  SubscribeTopic(
        topic_name='ktmw_bt/auth_request',
        topic_type=AuthRequest,
        on_msg_fn=on_msg_fn_pw_req,
        name='admin_pw_req_msgs_to_BB')        
    


    def on_msg_fn_tray_open(msg):
        py_trees.blackboard.Blackboard.set('remote_unlock', True)

    remote_unlock_status_to_BB = SubscribeTopic(
        topic_name='rm_agent/service_unlock_request',
        topic_type=Empty,
        on_msg_fn=on_msg_fn_tray_open,
        name='remote_unlock_status_to_BB') 

    def on_msg_fn_user_input(msg):
        py_trees.blackboard.Blackboard.set('hri_id', msg.hri_id) #uint8
        py_trees.blackboard.Blackboard.set('hri_status', msg.hri_status) #string
        py_trees.blackboard.Blackboard.set('hri_tray_id', msg.tray_id) #uint8
        py_trees.blackboard.Blackboard.set('hri_user_input', msg.user_input) #bool        

    user_input_msgs_to_BB =  SubscribeTopic(
        topic_name='ktmw_bt/HRI',
        topic_type=HRI,
        on_msg_fn=on_msg_fn_user_input,
        name='user_input_msgs_to_BB')

    def on_msg_fn_tray_open(msg):
        for i in range(2):
            py_trees.blackboard.Blackboard.set('Tray_'+str(i+1)+'_open_status', msg.door_states[i].door_state)
            py_trees.blackboard.Blackboard.set('Tray_'+str(i+1)+'_stuff_status', msg.door_states[i].has_stuff)


    tray_open_status_to_BB = SubscribeTopic(
        topic_name='box/box_state',
        topic_type=BoxStates,
        on_msg_fn=on_msg_fn_tray_open,
        name='tray_open_status_to_BB')       

    #tray exception status to BB
    def on_msg_fn_box_exception(msg):
        py_trees.blackboard.Blackboard.set('Tray_'+str(msg.door_states[0].location.y)+'_exception_status', msg.door_states[0].door_state) # 1: 물건 끼임 / 2: 고장 동작 이상


    box_exception_to_BB = SubscribeTopic(
        topic_name='box/box_exception',
        topic_type=BoxStates,
        on_msg_fn=on_msg_fn_box_exception,
        name='box_exception_to_BB')

    def on_msg_fn_stop_cancel_result(msg):
         # index[0] : 0-cancel, 1-stop, 2-release / index[1] : 0-성공, 1-실패
        py_trees.blackboard.Blackboard.set('halt_type', msg.data[0])
        py_trees.blackboard.Blackboard.set('halt_result', msg.data[1])        

    halt_result_to_BB = SubscribeTopic(
        topic_name='nav/event_result',
        topic_type=Int8MultiArray,
        on_msg_fn=on_msg_fn_stop_cancel_result,
        name='halt_result_to_BB')
    
    def on_msg_fn_beep_trigger(msg):
         # Treu: 충격감지, False: 기존 상태
        py_trees.blackboard.Blackboard.set('beep_trigger', msg.data)        

    beep_trigger_to_BB = SubscribeTopic(
        topic_name='shock/beep_trigger',
        topic_type=Bool,
        on_msg_fn=on_msg_fn_beep_trigger,
        name='beep_trigger_to_BB')
        
    par.add_children([box_exception_to_BB, emergency_button_info_to_BB, error_set_to_BB, admin_pw_req_msgs_to_BB, button_status_to_BB, battery_state_to_BB, charging_state_to_BB, nav_status_to_BB, halt_Status_to_BB, item_return_msgs_to_BB, remote_unlock_status_to_BB, user_input_msgs_to_BB, tray_open_status_to_BB, halt_result_to_BB, beep_trigger_to_BB])


    return par


def tray_stuck_seq_new():


    par_stuck_close = py_trees.composites.Parallel(
        name="par_stuck_close",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
        )

    seq_stuck1 = py_trees.composites.Sequence()
    seq_stuck2 = py_trees.composites.Sequence()

    tray1_stuck_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray1_stuck_check',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_1_exception_status',
                value=1,  
                operator= operator.eq
            )
        )
    
    tray2_stuck_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray2_stuck_check',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_2_exception_status',
                value=1,  
                operator= operator.eq
            )
        )   
    

    stuck_alarm1 = PublishTopic(
        name='stuck_alarm1',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[1],
            task_status='tray_stuck',
            action='tray_stuck',
            action_target='tray',
            action_result=True
            )
        )
    
    stuck_alarm2 = PublishTopic(
        name='stuck_alarm2',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[2],
            task_status='tray_stuck',
            action='tray_stuck',
            action_target='tray',
            action_result=True
            )
        )
    
    par_close_cmd1 = py_trees.composites.Parallel(
        name="par_close_cmd1",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
        )
    
    par_close_cmd2 = py_trees.composites.Parallel(
        name="par_close_cmd2",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
        )
    
    wait_hri_tray1_id_cmd = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_hri_tray1_id_cmd',
                check=py_trees.common.ComparisonExpression(
                variable='hri_tray_id',
                value=1,
                operator= operator.eq
            )
        )
    
    wait_hri_tray2_id_cmd = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_hri_tray2_id_cmd',
                check=py_trees.common.ComparisonExpression(
                variable='hri_tray_id',
                value=2,
                operator= operator.eq
            )
        )
    
    hri_finished_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'hri_finished_check1',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Finished_check',
                operator= operator.eq
            )
        )

    hri_finished_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'hri_finished_check2',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Finished_check',
                operator= operator.eq
            )
        )
    
    unset_stuck1 = SetBlackBoard('Tray_1_exception_status', 0)
    unset_stuck2 = SetBlackBoard('Tray_2_exception_status', 0)

    unset_hri1 = SetBlackBoard('hri_tray_id', '')
    unset_hri2 = SetBlackBoard('hri_tray_id', '')

    unset_hri_status1 = SetBlackBoard('hri_status', '')
    unset_hri_status2 = SetBlackBoard('hri_status', '')    

    # tray_close1 = BoxClose(position=1, x=1, y=1)
    # tray_close2 = BoxClose(position=1, x=1, y=2)

    def request_generate_fn_close_opened_tray():
        request = BoxCtrl.Request()
        request.data.box_command = 2
        request.data.location.position = 1
        request.data.location.x = 1
        request.data.location.y = 1
        return request
    def response_fn_close_opened_tray(response):
        print(response.success)

    tray_close1 = ServiceCall(
        service_name='hardware_manager/box/box_control',
        service_type= BoxCtrl,
        request_generate_fn=request_generate_fn_close_opened_tray,
        response_fn= response_fn_close_opened_tray, name='tray_close1'

    )

    def request_generate_fn_close_opened_tray():
        request = BoxCtrl.Request()
        request.data.box_command = 2
        request.data.location.position = 1
        request.data.location.x = 1
        request.data.location.y = 2
        return request
    def response_fn_close_opened_tray(response):
        print(response.success)

    tray_close2 = ServiceCall(
        service_name='hardware_manager/box/box_control',
        service_type= BoxCtrl,
        request_generate_fn=request_generate_fn_close_opened_tray,
        response_fn= response_fn_close_opened_tray, name='tray_close2'

    )


    tts_tray_error= TTSPlay(tts_name='tray_error', play=True, sequence=True)
    
    
    tts_tray_error2= TTSPlay(tts_name='tray_error', play=True, sequence=True)
    tts_tray_error3= TTSPlay(tts_name='tray_error', play=True, sequence=True)

    seq_stuck_for_delay1 = py_trees.composites.Sequence()
    seq_stuck_for_delay2 = py_trees.composites.Sequence()


    par_selected1 = py_trees.composites.Parallel(
        name="par_selected1",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[par_close_cmd1],
            synchronise=False
        )        
    )

    tray1_stuck_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray1_stuck_check2',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_1_exception_status',
                value=1,  
                operator= operator.eq
            )
        )
    
    stuck_alarm1_2 = PublishTopic(
        name='stuck_alarm1_2',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[1],
            task_status='tray_stuck',
            action='tray_stuck',
            action_target='tray',
            action_result=True
            )
        )
    
    unset_stuck1_2 = SetBlackBoard('Tray_1_exception_status', 0)

    par_selected2 = py_trees.composites.Parallel(
        name="par_selected2",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[par_close_cmd2],
            synchronise=False
        )        
    )

    tray2_stuck_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray2_stuck_check2',
                check=py_trees.common.ComparisonExpression(
                variable='Tray_2_exception_status',
                value=1,  
                operator= operator.eq
            )
        )
    
    stuck_alarm2_2 = PublishTopic(
        name='stuck_alarm2_2',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[2],
            task_status='tray_stuck',
            action='tray_stuck',
            action_target='tray',
            action_result=True
            )
        )
    
    unset_stuck2_2 = SetBlackBoard('Tray_2_exception_status', 0)



    
    tts_tray_error1 = TTSPlay(tts_name='tray_error', play=True, sequence=True)

    par_stuck_close.add_children([seq_stuck1, seq_stuck2])

    seq_stuck1.add_children([tray1_stuck_check, unset_hri1, unset_hri_status1, stuck_alarm1, unset_stuck1, tts_tray_error, par_selected1, tray_not_ing_check(), tray_close1])
    
    par_selected1.add_children([par_close_cmd1, seq_stuck_for_delay1])
    par_close_cmd1.add_children([wait_hri_tray2_id_cmd, hri_finished_check1])
    seq_stuck_for_delay1.add_children([tray1_stuck_check2, stuck_alarm1_2, tts_tray_error1, unset_stuck1_2])

    seq_stuck2.add_children([tray2_stuck_check,  unset_hri2, unset_hri_status2, stuck_alarm2, unset_stuck2, tts_tray_error2, par_selected2, tray_not_ing_check(), tray_close2])
    
    par_selected2.add_children([par_close_cmd2, seq_stuck_for_delay2])
    par_close_cmd2.add_children([wait_hri_tray1_id_cmd, hri_finished_check2])
    seq_stuck_for_delay2.add_children([tray2_stuck_check2, stuck_alarm2_2, tts_tray_error3, unset_stuck2_2])
    
    

    return par_stuck_close


def tray_not_ing_check():

    par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    tray1_opening_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=3,
            operator= operator.ne
            )
        )
    
    tray2_opening_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=3,
            operator= operator.ne
            )
        )
    
    tray1_closing_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=4,
            operator= operator.ne
            )
        )    
    
    tray2_closing_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=4,
            operator= operator.ne
            )
        )       


    par.add_children([tray1_opening_check, tray1_closing_check, tray2_opening_check, tray2_closing_check])

    return par

def halt_cancel_seq():


    seq_halt_cancel = py_trees.composites.Sequence()
    
    admin_auth_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'admin_auth_check',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='Admin_auth',
            operator= operator.eq
        )
    )

    cancel_nav_true1 = NavigationCancel()
    cancel_nav_true2 = NavigationCancel()
    cancel_nav_true3 = NavigationCancel()
    cancel_nav_true4 = NavigationCancel()

    cancel_alarm1 =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )   
    
    cancel_alarm2 =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )   

    cancel_alarm3 =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )   

    cancel_alarm4 =  PublishTopic(
        name='cancel_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_cancel',
            action='nav_cancel',
            action_target='nav_cancel',
            action_result=True
            )
        )               
    
    cancel_return_alarm1 =  PublishTopic(
        name='cancel_return_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('cancel_return_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('cancel_return_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('cancel_return_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=py_trees.blackboard.Blackboard.get('cancel_return_tray_id'),
            task_status='cancel_return',
            action='cancel_return',
            action_target='cancel_return',
            action_result=True
            )
        )     

    seq_resume_check = py_trees.composites.Sequence()



    par_cancel_type_check = py_trees.composites.Parallel(
        name="par_cancel_type_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )



    seq_item_change_check = py_trees.composites.Sequence()
    seq_item_cancel_check = py_trees.composites.Sequence()

    par_item_change = py_trees.composites.Parallel(
        name="par_item_change",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    item_change_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'item_change_check',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='Item_change',
            operator= operator.eq
        )
    )


    item_cancel_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'item_cancel_check',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='Item_cancel',
            operator= operator.eq
        )
    )

    par_service_id_check = py_trees.composites.Parallel(
        name="par_service_id_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_halt_returrn_check = py_trees.composites.Sequence()

    cancel_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'cancel_check1',
        check=py_trees.common.ComparisonExpression(
            variable="halt_status",
            value='cancel',
            operator= operator.eq
        )
    )

    cancel_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'cancel_check1',
        check=py_trees.common.ComparisonExpression(
            variable="halt_status",
            value='cancel',
            operator= operator.eq
        )
    )

    halt_return_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'halt_return_check',
        check=py_trees.common.ComparisonExpression(
            variable="cancel_return_is_tray",
            value=True,
            operator= operator.eq
        )
    )
    
    cancel_tray_num_check = SetHaltBlackBoard()
    
    par_cancel_unload_loc_check = py_trees.composites.Parallel(
        name="par_unload_loc_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_cancel_unload_here = py_trees.composites.Sequence()

    cancel_unload_moving_check_1 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'cancel_unload_moving_check_1',
        check=py_trees.common.ComparisonExpression(
            variable="cancel_return_moving_status",
            value=False,
            operator= operator.eq
        )
    )

    par_unload_cancel_tray_check_1 = py_trees.composites.Parallel(
        name="par_unload_cancel_tray_check_1",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_one_cancel_tray_unload_1 = py_trees.composites.Sequence()

    one_cancel_tray_unload_check_1 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'one_cancel_tray_unload_check_1',
        check=py_trees.common.ComparisonExpression(
            variable="cancel_tray_num",
            value=1,
            operator=operator.eq
        )
    )
    
    go_to_tray_cancel1_1 = EnqueueNextService(
        service_name='tray_cancel1', service_version=''
    )

    seq_multi_cancel_tray_unload_1 = py_trees.composites.Sequence()

    multi_cancel_tray_unload_check_1 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'multi_cancel_tray_unload_check_1',
        check=py_trees.common.ComparisonExpression(
            variable="cancel_tray_num",
            value=2,
            operator=operator.eq
        )
    )

    go_to_tray_cancel2_1 = EnqueueNextService(
        service_name='tray_cancel2', service_version=''
    )

    seq_cancel_unload_there = py_trees.composites.Sequence()

    cancel_unload_moving_check_2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'cancel_unload_moving_check_2',
        check=py_trees.common.ComparisonExpression(
            variable="cancel_return_moving_status",
            value=True,
            operator= operator.eq
        )
    )

    unset_current_service = unset_current()


    set_current_service = set_current()

    
    cancel_set_goal_index = SetGoalIndex()
    cancel_set_route_index = SetRouteIndex()

    def request_generate_fn_poi2bb():
        req = GetPoiRoute.Request()
        req.goal_label = py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id')
        return req
    
    def response_fn_poi2bb(response):
        py_trees.blackboard.Blackboard.set('poi_len', len(response.poi_info_list))
        py_trees.blackboard.Blackboard.set('poi_success_check', response.success)
        for i in range(len(response.poi_info_list)):
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/waypoint_poi', response.poi_info_list[i].poi)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_name', response.poi_info_list[i].map_name)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/zone', response.poi_info_list[i].zone)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/floor', response.poi_info_list[i].floor)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/is_ev', response.poi_info_list[i].is_elevator)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_change', response.poi_info_list[i].map_change)

    route_to_BB_for_cancel = ServiceCall(
        service_name='configuration_manager/get_poi_route',
        service_type=GetPoiRoute,
        request_generate_fn=request_generate_fn_poi2bb,
        response_fn=response_fn_poi2bb,
        name='route_to_BB_for_cancel'
    )

    go_to_moving_tree_for_cancel = EnqueueNextService(
        service_name='moving_tree', service_version=''
    )


    seq_just_halt_check = py_trees.composites.Sequence()

    just_halt_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'just_halt_check',
        check=py_trees.common.ComparisonExpression(
            variable="cancel_return_is_tray",
            value=False,
            operator= operator.eq
        )
    )

    go_to_idle_tree = EnqueueNextService(
        service_name='BB_clear', service_version=''
    )

    resume_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'resume_check',
            check=py_trees.common.ComparisonExpression(
            variable="halt_status",
            value='resume',
            operator= operator.eq
        )
    )    

    unset_hri_status = py_trees.behaviours.UnsetBlackboardVariable('hri_status')

    tts_item_change = TTSPlay(tts_name='item_change', play=True, sequence=True)

    unset_admin_pw = SetBlackBoard('admin_pw_type', '')
    unset_halt_status2 = py_trees.behaviours.UnsetBlackboardVariable('halt_status')

    # led_start_on_auth_checked_f = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    # led_start_on_auth_checked_r = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)    
    

    led_start_on_auth_checked_f = PublishTopic(
                name='led_start_on_auth_checked_f',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    led_start_on_auth_checked_r = PublishTopic(
                name='led_start_on_auth_checked_r',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    BGM_off_cancel = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)

    cancel_return_alarm = PublishTopic(
        name='cancel_return_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('cancel_return_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('cancel_return_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('cancel_return_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=py_trees.blackboard.Blackboard.get('cancel_return_tray_id'),
            task_status='cancel_return',
            action='cancel_return',
            action_target='cancel_return',
            action_result=True
            )
        )
      

    par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq_resume_check],
            synchronise=False
        )
    )

    route_ready_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'route_ready_check',
            check=py_trees.common.ComparisonExpression(
            variable="poi_success_check",
            value=True,
            operator= operator.eq
        )
    )

    par_route_ready_check = py_trees.composites.Parallel(
            name="par_route_ready_check",
            policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[route_ready_check],
            synchronise=False
            )
        )
    
    seq_route_fail_check = py_trees.composites.Sequence()

    route_fail_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'route_fail_check',
            check=py_trees.common.ComparisonExpression(
            variable="poi_success_check",
            value=False,
            operator= operator.eq
        )
    )

    route_fail_alarm = PublishTopic(
        name='route_fail_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='route_fail',
            action='route_fail',
            action_target='route',
            action_result=False
            )
        )
    
    unset_current_service2 = unset_current()
    unset_route_fail = SetBlackBoard(BB_variable='poi_success_check', BB_value='')

    Service_requested_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'Service_requested_check',
            check=py_trees.common.ComparisonExpression(
            variable="current_goal_count",
            value=0,
            operator= operator.ge
        )
    )

    #경로 to BB -> TBD
    def request_generate_fn_poi2bb2():
        req = GetPoiRoute.Request()
        req.goal_label = py_trees.blackboard.Blackboard.get('1/current_goal_id')
        return req
    
    def response_fn_poi2bb2(response):
        py_trees.blackboard.Blackboard.set('poi_len', len(response.poi_info_list))
        py_trees.blackboard.Blackboard.set('poi_success_check', response.success)
        for i in range(len(response.poi_info_list)):
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/waypoint_poi', response.poi_info_list[i].poi)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_name', response.poi_info_list[i].map_name)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/zone', response.poi_info_list[i].zone)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/floor', response.poi_info_list[i].floor)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/is_ev', response.poi_info_list[i].is_elevator)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_change', response.poi_info_list[i].map_change)

    route_to_BB2 = ServiceCall(
        service_name='configuration_manager/get_poi_route',
        service_type=GetPoiRoute,
        request_generate_fn=request_generate_fn_poi2bb2,
        response_fn=response_fn_poi2bb2,
        name='route_to_BB2'
    )

    unset_hri_status3 = SetBlackBoard('hri_status', '')
    unset_hri_status4 = SetBlackBoard('hri_status', '')

    tts_play = TTSPlay(tts_name='returning_start', play=True, sequence=True)






    #주행중 취소(취소, 변경)
    par.add_children([seq_resume_check, seq_halt_cancel])
    seq_halt_cancel.add_children([admin_auth_check, admin_password_check_seq(), unset_admin_pw, led_start_on_auth_checked_f, led_start_on_auth_checked_r, par_cancel_type_check])
    par_cancel_type_check.add_children([seq_item_change_check, seq_item_cancel_check])
    seq_item_change_check.add_children([item_change_check, unset_hri_status3, tts_item_change, par_item_change])
    par_item_change.add_children([tray_action_seq_manual(), hri_finished_and_alarm()])
    seq_item_cancel_check.add_children([item_cancel_check, unset_hri_status4, par_service_id_check])
    seq_resume_check.add_children([resume_check2, unset_hri_status, unset_halt_status2])

    par_service_id_check.add_children([seq_halt_returrn_check, seq_just_halt_check])
    seq_halt_returrn_check.add_children([cancel_check1, halt_return_check, cancel_tray_num_check, par_cancel_unload_loc_check])
    
    par_cancel_unload_loc_check.add_children([seq_cancel_unload_here, seq_cancel_unload_there])
    
    seq_cancel_unload_here.add_children([cancel_unload_moving_check_1, par_unload_cancel_tray_check_1])
    par_unload_cancel_tray_check_1.add_children([seq_one_cancel_tray_unload_1, seq_multi_cancel_tray_unload_1])
    seq_one_cancel_tray_unload_1.add_children([one_cancel_tray_unload_check_1, cancel_nav_true1, cancel_alarm1, go_to_tray_cancel1_1])
    seq_multi_cancel_tray_unload_1.add_children([multi_cancel_tray_unload_check_1, cancel_nav_true2, cancel_alarm2, go_to_tray_cancel2_1])

    seq_cancel_unload_there.add_children([cancel_unload_moving_check_2, cancel_nav_true3, unset_current_service,set_current_service,cancel_set_goal_index, route_to_BB_for_cancel, cancel_set_route_index,par_route_ready_check, cancel_alarm3, cancel_return_alarm, tts_play, go_to_moving_tree_for_cancel]) # 얘 잘감
    par_route_ready_check.add_children([route_ready_check, seq_route_fail_check])
    seq_route_fail_check.add_children([route_fail_check, route_fail_alarm, unset_current_service2, unset_route_fail, Service_requested_check2, route_to_BB2])

    seq_just_halt_check.add_children([cancel_check2, just_halt_check, cancel_nav_true4, cancel_alarm4, cancel_return_alarm1, BGM_off_cancel, go_to_idle_tree])


    return par

def llm_led_whole1():
    
    par_llm_led = py_trees.composites.Parallel(
        name="par_llm_led",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_llm_led_colorful = py_trees.composites.Sequence()
    seq_llm_led_calm = py_trees.composites.Sequence()
    
    llm_led_colorful_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_colorful_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_calm_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_calm_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    par_llm_led_colorful = py_trees.composites.Parallel(
        name="par_llm_led_colorful",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    par_llm_led_calm = py_trees.composites.Parallel(
        name="par_llm_led_colorful",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_llm_led_yellow1 = py_trees.composites.Sequence()
    seq_llm_led_blue1 = py_trees.composites.Sequence()
    seq_llm_led_green1 = py_trees.composites.Sequence()
    seq_llm_led_general1 = py_trees.composites.Sequence()
    seq_llm_led_orange1 = py_trees.composites.Sequence()
    seq_llm_led_red1 = py_trees.composites.Sequence()
    
    seq_llm_led_yellow2 = py_trees.composites.Sequence()
    seq_llm_led_blue2 = py_trees.composites.Sequence()
    seq_llm_led_green2 = py_trees.composites.Sequence()
    seq_llm_led_general2 = py_trees.composites.Sequence()
    seq_llm_led_orange2 = py_trees.composites.Sequence()
    seq_llm_led_red2 = py_trees.composites.Sequence()
    
    llm_led_yellow_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_yellow_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_blue_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_blue_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    llm_led_green_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_green_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='3',
            operator= operator.eq
        )
    )
    
    llm_led_general_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_general_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='4',
            operator= operator.eq
        )
    )
    
    llm_led_orange_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_orange_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='5',
            operator= operator.eq
        )
    )
    
    llm_led_red_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_red_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='6',
            operator= operator.eq
        )
    )
    
    llm_led_yellow_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_yellow_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_blue_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_blue_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    llm_led_green_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_green_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='3',
            operator= operator.eq
        )
    )
    
    llm_led_general_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_general_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='4',
            operator= operator.eq
        )
    )
    
    llm_led_orange_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_orange_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='5',
            operator= operator.eq
        )
    )
    
    llm_led_red_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_red_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='6',
            operator= operator.eq
        )
    )
    
    led_start_on_moving1_yellow1 = PublishTopic(
                name='led_start_on_moving1_yellow1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_yellow1 = PublishTopic(
                name='led_start_on_moving2_yellow1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_yellow2 = PublishTopic(
                name='led_start_on_moving1_yellow2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_yellow2 = PublishTopic(
                name='led_start_on_moving2_yellow2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_blue1 = PublishTopic(
                name='led_start_on_moving1_blue1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_blue1 = PublishTopic(
                name='led_start_on_moving2_blue1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_blue2 = PublishTopic(
                name='led_start_on_moving1_blue2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_blue2 = PublishTopic(
                name='led_start_on_moving2_blue2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_green1 = PublishTopic(
                name='led_start_on_moving1_green1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_green1 = PublishTopic(
                name='led_start_on_moving2_green1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_green2 = PublishTopic(
                name='led_start_on_moving1_green2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_green2 = PublishTopic(
                name='led_start_on_moving2_green2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_general1 = PublishTopic(
                name='led_start_on_moving1_general1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_general1 = PublishTopic(
                name='led_start_on_moving2_general1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_general2 = PublishTopic(
                name='led_start_on_moving1_general2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_general2 = PublishTopic(
                name='led_start_on_moving2_general2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_orange1 = PublishTopic(
                name='led_start_on_moving1_orange1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_orange1 = PublishTopic(
                name='led_start_on_moving2_orange1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_orange2 = PublishTopic(
                name='led_start_on_moving1_orange2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_orange2 = PublishTopic(
                name='led_start_on_moving2_orange2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_red1 = PublishTopic(
                name='led_start_on_moving1_red1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_red1 = PublishTopic(
                name='led_start_on_moving2_red1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_red2 = PublishTopic(
                name='led_start_on_moving1_red2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_red2 = PublishTopic(
                name='led_start_on_moving2_red2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    par_llm_led.add_children([seq_llm_led_colorful, seq_llm_led_calm])
    seq_llm_led_colorful.add_children([llm_led_colorful_check, par_llm_led_colorful])
    seq_llm_led_calm.add_children([llm_led_calm_check, par_llm_led_calm])
    
    par_llm_led_colorful.add_children([seq_llm_led_yellow1, seq_llm_led_blue1, seq_llm_led_green1, seq_llm_led_general1, seq_llm_led_orange1, seq_llm_led_red1])
    par_llm_led_calm.add_children([seq_llm_led_yellow2, seq_llm_led_blue2, seq_llm_led_green2, seq_llm_led_general2, seq_llm_led_orange2, seq_llm_led_red2])
    
    seq_llm_led_yellow1.add_children([llm_led_yellow_check1, led_start_on_moving1_yellow1, led_start_on_moving2_yellow1])
    seq_llm_led_blue1.add_children([llm_led_blue_check1, led_start_on_moving1_blue1, led_start_on_moving2_blue1])
    seq_llm_led_green1.add_children([llm_led_green_check1, led_start_on_moving1_green1, led_start_on_moving2_green1])
    seq_llm_led_general1.add_children([llm_led_general_check1, led_start_on_moving1_general1, led_start_on_moving2_general1])
    seq_llm_led_orange1.add_children([llm_led_orange_check1, led_start_on_moving1_orange1, led_start_on_moving2_orange1])
    seq_llm_led_red1.add_children([llm_led_red_check1, led_start_on_moving1_red1, led_start_on_moving2_red1])
    
    seq_llm_led_yellow2.add_children([llm_led_yellow_check2, led_start_on_moving1_yellow2, led_start_on_moving2_yellow2])
    seq_llm_led_blue2.add_children([llm_led_blue_check2, led_start_on_moving1_blue2, led_start_on_moving2_blue2])
    seq_llm_led_green2.add_children([llm_led_green_check2, led_start_on_moving1_green2, led_start_on_moving2_green2])
    seq_llm_led_general2.add_children([llm_led_general_check2, led_start_on_moving1_general2, led_start_on_moving2_general2])
    seq_llm_led_orange2.add_children([llm_led_orange_check2, led_start_on_moving1_orange2, led_start_on_moving2_orange2])
    seq_llm_led_red2.add_children([llm_led_red_check2, led_start_on_moving1_red2, led_start_on_moving2_red2])
    
    return par_llm_led

def llm_led_whole2():
    
    par_llm_led = py_trees.composites.Parallel(
        name="par_llm_led",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_llm_led_colorful = py_trees.composites.Sequence()
    seq_llm_led_calm = py_trees.composites.Sequence()
    
    llm_led_colorful_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_colorful_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_calm_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_calm_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    par_llm_led_colorful = py_trees.composites.Parallel(
        name="par_llm_led_colorful",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    par_llm_led_calm = py_trees.composites.Parallel(
        name="par_llm_led_colorful",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_llm_led_yellow1 = py_trees.composites.Sequence()
    seq_llm_led_blue1 = py_trees.composites.Sequence()
    seq_llm_led_green1 = py_trees.composites.Sequence()
    seq_llm_led_general1 = py_trees.composites.Sequence()
    seq_llm_led_orange1 = py_trees.composites.Sequence()
    seq_llm_led_red1 = py_trees.composites.Sequence()
    
    seq_llm_led_yellow2 = py_trees.composites.Sequence()
    seq_llm_led_blue2 = py_trees.composites.Sequence()
    seq_llm_led_green2 = py_trees.composites.Sequence()
    seq_llm_led_general2 = py_trees.composites.Sequence()
    seq_llm_led_orange2 = py_trees.composites.Sequence()
    seq_llm_led_red2 = py_trees.composites.Sequence()
    
    llm_led_yellow_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_yellow_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_blue_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_blue_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    llm_led_green_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_green_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='3',
            operator= operator.eq
        )
    )
    
    llm_led_general_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_general_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='4',
            operator= operator.eq
        )
    )
    
    llm_led_orange_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_orange_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='5',
            operator= operator.eq
        )
    )
    
    llm_led_red_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_red_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='6',
            operator= operator.eq
        )
    )
    
    llm_led_yellow_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_yellow_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_blue_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_blue_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    llm_led_green_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_green_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='3',
            operator= operator.eq
        )
    )
    
    llm_led_general_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_general_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='4',
            operator= operator.eq
        )
    )
    
    llm_led_orange_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_orange_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='5',
            operator= operator.eq
        )
    )
    
    llm_led_red_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_red_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='6',
            operator= operator.eq
        )
    )
    
    led_start_on_moving1_yellow1 = PublishTopic(
                name='led_start_on_moving1_yellow1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_yellow1 = PublishTopic(
                name='led_start_on_moving2_yellow1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_yellow2 = PublishTopic(
                name='led_start_on_moving1_yellow2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_yellow2 = PublishTopic(
                name='led_start_on_moving2_yellow2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_blue1 = PublishTopic(
                name='led_start_on_moving1_blue1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_blue1 = PublishTopic(
                name='led_start_on_moving2_blue1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_blue2 = PublishTopic(
                name='led_start_on_moving1_blue2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_blue2 = PublishTopic(
                name='led_start_on_moving2_blue2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_green1 = PublishTopic(
                name='led_start_on_moving1_green1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_green1 = PublishTopic(
                name='led_start_on_moving2_green1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_green2 = PublishTopic(
                name='led_start_on_moving1_green2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_green2 = PublishTopic(
                name='led_start_on_moving2_green2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_general1 = PublishTopic(
                name='led_start_on_moving1_general1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_general1 = PublishTopic(
                name='led_start_on_moving2_general1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_general2 = PublishTopic(
                name='led_start_on_moving1_general2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_general2 = PublishTopic(
                name='led_start_on_moving2_general2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_orange1 = PublishTopic(
                name='led_start_on_moving1_orange1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_orange1 = PublishTopic(
                name='led_start_on_moving2_orange1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_orange2 = PublishTopic(
                name='led_start_on_moving1_orange2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_orange2 = PublishTopic(
                name='led_start_on_moving2_orange2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_red1 = PublishTopic(
                name='led_start_on_moving1_red1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_red1 = PublishTopic(
                name='led_start_on_moving2_red1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_red2 = PublishTopic(
                name='led_start_on_moving1_red2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_red2 = PublishTopic(
                name='led_start_on_moving2_red2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    par_llm_led.add_children([seq_llm_led_colorful, seq_llm_led_calm])
    seq_llm_led_colorful.add_children([llm_led_colorful_check, par_llm_led_colorful])
    seq_llm_led_calm.add_children([llm_led_calm_check, par_llm_led_calm])
    
    par_llm_led_colorful.add_children([seq_llm_led_yellow1, seq_llm_led_blue1, seq_llm_led_green1, seq_llm_led_general1, seq_llm_led_orange1, seq_llm_led_red1])
    par_llm_led_calm.add_children([seq_llm_led_yellow2, seq_llm_led_blue2, seq_llm_led_green2, seq_llm_led_general2, seq_llm_led_orange2, seq_llm_led_red2])
    
    seq_llm_led_yellow1.add_children([llm_led_yellow_check1, led_start_on_moving1_yellow1, led_start_on_moving2_yellow1])
    seq_llm_led_blue1.add_children([llm_led_blue_check1, led_start_on_moving1_blue1, led_start_on_moving2_blue1])
    seq_llm_led_green1.add_children([llm_led_green_check1, led_start_on_moving1_green1, led_start_on_moving2_green1])
    seq_llm_led_general1.add_children([llm_led_general_check1, led_start_on_moving1_general1, led_start_on_moving2_general1])
    seq_llm_led_orange1.add_children([llm_led_orange_check1, led_start_on_moving1_orange1, led_start_on_moving2_orange1])
    seq_llm_led_red1.add_children([llm_led_red_check1, led_start_on_moving1_red1, led_start_on_moving2_red1])
    
    seq_llm_led_yellow2.add_children([llm_led_yellow_check2, led_start_on_moving1_yellow2, led_start_on_moving2_yellow2])
    seq_llm_led_blue2.add_children([llm_led_blue_check2, led_start_on_moving1_blue2, led_start_on_moving2_blue2])
    seq_llm_led_green2.add_children([llm_led_green_check2, led_start_on_moving1_green2, led_start_on_moving2_green2])
    seq_llm_led_general2.add_children([llm_led_general_check2, led_start_on_moving1_general2, led_start_on_moving2_general2])
    seq_llm_led_orange2.add_children([llm_led_orange_check2, led_start_on_moving1_orange2, led_start_on_moving2_orange2])
    seq_llm_led_red2.add_children([llm_led_red_check2, led_start_on_moving1_red2, led_start_on_moving2_red2])
    
    return par_llm_led

def while_moving_par():



    par_moving_event = py_trees.composites.Parallel(
        name="par_moving_event",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )


    seq_failed = py_trees.composites.Sequence()


    fail_par = py_trees.composites.Parallel(
        name="fail_par",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )
    
    failed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'failed_check',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='failed',
            operator=operator.eq
        )
    )

    req_id_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'req_id_check',
        check=py_trees.common.ComparisonExpression(
            variable="req_id",
            value=1,
            operator=operator.le
        )
    )

    failed_alarm = PublishTopic(
        name='failed_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='moving',
            action='failed',
            action_target='failed',
            action_result=True
            )
        )

    go_to_error = EnqueueNextService(
        service_name='critical_error_tree', service_version='2.0.0'
    )

    seq_blocked = py_trees.composites.Sequence()

    blocked_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'blocked_check',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='blocked',
            operator=operator.eq
        )
    )

    blocked_alarm = PublishTopic(
        name='blocked_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='moving',
            action='blocked',
            action_target='obstacle',
            action_result=True
            )
        )
    

    blocked_pause_15 = py_trees.timers.Timer("blocked_pause_15", duration=15.0)

    seq_fleet_lineup = py_trees.composites.Sequence()   

    fleet_lineup_alarm = PublishTopic(
        name='fleet_lineup_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='moving',
            action='fleet_lineup',
            action_target='fleet_lineup',
            action_result=True
            )
        )
    
    fleet_lineup_alarm2 = PublishTopic(
        name='fleet_lineup_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='moving',
            action='fleet_lineup',
            action_target='fleet_lineup',
            action_result=False
            )
        )



    seq_recovery = py_trees.composites.Sequence()

    recovery_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'recovery_check',
        check=py_trees.common.ComparisonExpression(
            variable="req_id",
            value=3,
            operator=operator.eq
        )
    )

    recovery_alarm = PublishTopic(
        name='recovery_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='moving',
            action='recovery',
            action_target='recovery',
            action_result=True
            )
        )
    
    recovery_alarm2 = PublishTopic(
        name='recovery_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='moving',
            action='recovery',
            action_target='recovery',
            action_result=False
            )
        )


    seq_arrived = py_trees.composites.Sequence()
    tts_obstacle = TTSPlay(tts_name='obstacle', play=True, sequence=True)

    par_fleet_lineup_check = py_trees.composites.Parallel(
        name="par_fleet_lineup_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    tts_obstacle_robot = TTSPlay(tts_name='obstacle_robot', play=True, sequence=True)
    tts_lineup_wating = TTSPlay(tts_name='lineup_wating', play=True, sequence=True)    


    par_fleet_finished_check = py_trees.composites.Parallel(
        name="par_fleet_finished_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    fleet_lineup_check_state = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'fleet_lineup_check_state',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    fleet_lineup_check_req_id = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'fleet_lineup_check_req_id',
        check=py_trees.common.ComparisonExpression(
            variable="req_id",
            value=2,
            operator=operator.eq
        )
    )

    fleet_finished_check_state = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'fleet_finished_check_state',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='moving',
            operator=operator.eq
        )
    )

    fleet_finished_check_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'fleet_finished_check_mode',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='normal',
            operator=operator.eq
        )
    )

    par_recovery_finished_check = py_trees.composites.Parallel(
        name="par_recovery_finished_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    recovery_finished_check_state = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'recovery_finished_check_state',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='moving',
            operator=operator.eq
        )
    )

    recovery_finished_check_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'recovery_finished_check_mode',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='normal',
            operator=operator.eq
        )
    )

    # for fail idling
    # led_qr_rec_fail_f = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)

    # led_qr_rec_fail_r = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)
    
    led_qr_rec_fail_f = PublishTopic(
                name='led_qr_rec_fail_f',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )  

    led_qr_rec_fail_r = PublishTopic(
                name='led_qr_rec_fail_r',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )  


    fail_idling = Idling()
    
    go_to_minor_error_tree = EnqueueNextService(service_name='minor_error_tree', service_version='2.0.0')

    seq_collission = py_trees.composites.Sequence()

    collission_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'collission_check',
        check=py_trees.common.ComparisonExpression(
            variable="beep_trigger",
            value=True,
            operator=operator.eq
        )
    )

    collision_alarm = PublishTopic(
        name='collision_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='moving',
            action='collision',
            action_target='collision',
            action_result=True
            )
        )

    alarmplay_collision = PublishTopic(
        name='alarmplay_collision',
        topic_name='ktmw_bt/alarm_param/service',
        topic_type = SoundControl,
        msg_generate_fn=lambda: SoundControl(
            name='seld_alarm',
            play=True,
            repeat=False,
            sequence=False,
            )
        )

    collision_key_reset = SetBlackBoard(BB_variable='beep_trigger', BB_value=False)


    led_start_on_lineup_front = PublishTopic(
                name='led_start_on_lineup_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )     

    led_start_on_lineup_rear = PublishTopic(
                name='led_start_on_lineup_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )

    led_start_on_moving_again1 = PublishTopic(
                name='led_start_on_moving_again1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving_again2 = PublishTopic(
                name='led_start_on_moving_again2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )

    led_start_on_moving_again3 = PublishTopic(
                name='led_start_on_moving_again3',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving_again4 = PublishTopic(
                name='led_start_on_moving_again4',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )

    led_start_on_recovery_front = PublishTopic(
                name='led_start_on_recovery_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )     

    led_start_on_recovery_rear = PublishTopic(
                name='led_start_on_recovery_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )

    set_pre_fleet = SetBlackBoard(BB_variable='pre_nav_status', BB_value='fleet')
    set_pre_recovery = SetBlackBoard(BB_variable='pre_nav_status', BB_value='recovery')

    reset_pre_nav_status1 = SetBlackBoard(BB_variable='pre_nav_status', BB_value=None)
    reset_pre_nav_status2 = SetBlackBoard(BB_variable='pre_nav_status', BB_value=None)

    par_llm_bgm = py_trees.composites.Parallel(
        name="par_llm_bgm",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_bgm_moving = py_trees.composites.Sequence()
    seq_bgm_new = py_trees.composites.Sequence()
    seq_bgm_classic = py_trees.composites.Sequence()
    
    bgm_moving_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'bgm_moving_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_bgm",
            value='1',
            operator= operator.eq
        )
    )
    
    bgm_new_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'bgm_new_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_bgm",
            value='2',
            operator= operator.eq
        )
    )
    
    bgm_classic_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'bgm_classic_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_bgm",
            value='3',
            operator= operator.eq
        )
    )
    
    bgm_moving = BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=True, repeat=True)
    bgm_new = BGMPlay(bgm_name= "serious_alarm", play=True, repeat=True) # aespa
    bgm_classic = BGMPlay(bgm_name= "serious_alarm", play=True, repeat=True) # classic
    
    
    BGM_off_fleet = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)


    par_moving_event.add_children([seq_collission, seq_blocked, seq_fleet_lineup, seq_recovery, seq_failed])
    seq_collission.add_children([collission_check, alarmplay_collision, collision_alarm, collision_key_reset])
    seq_blocked.add_children([blocked_check, tts_obstacle, blocked_alarm, blocked_pause_15])
    seq_fleet_lineup.add_children([par_fleet_lineup_check, set_pre_fleet, tts_lineup_wating, BGM_off_fleet, led_start_on_lineup_front, led_start_on_lineup_rear, fleet_lineup_alarm,par_fleet_finished_check, par_llm_bgm, reset_pre_nav_status1, llm_led_whole1(), fleet_lineup_alarm2])
    par_fleet_lineup_check.add_children([fleet_lineup_check_state, fleet_lineup_check_req_id])
    par_fleet_finished_check.add_children([fleet_finished_check_state, fleet_finished_check_mode])
    
    par_llm_bgm.add_children([seq_bgm_moving, seq_bgm_new, seq_bgm_classic])
    seq_bgm_moving.add_children([bgm_moving_check, bgm_moving])
    seq_bgm_new.add_children([bgm_new_check, bgm_new])
    seq_bgm_classic.add_children([bgm_classic_check, bgm_classic])

    seq_recovery.add_children([recovery_check, set_pre_recovery, tts_obstacle_robot, led_start_on_recovery_front, led_start_on_recovery_rear, recovery_alarm, par_recovery_finished_check,reset_pre_nav_status2, llm_led_whole2(), recovery_alarm2])
    par_recovery_finished_check.add_children([recovery_finished_check_state, recovery_finished_check_mode])

    seq_failed.add_children([fail_par, failed_alarm, NavigationCancel(), go_to_minor_error_tree])
    fail_par.add_children([failed_check, req_id_check])
    

    return par_moving_event


def open_check():
    par_on_one =  py_trees.composites.Parallel(
        name="par_one",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 
    # tray 전체 상태 한번에 받을 수 있다면 교체 예정
    tray1_open_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=2,
            operator= operator.eq
            )
        )
    
    tray2_open_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=2,
            operator= operator.eq
            )
        )    
    
    par_on_one.add_children([tray1_open_check, tray2_open_check])

    return par_on_one

def close_check():
    par_on_all =  py_trees.composites.Parallel(
        name="par_all",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    ) 
    # tray 전체 상태 한번에 받을 수 있다면 교체 예정
    tray1_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=1,
            operator= operator.eq
            )
        )
    
    tray2_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=1,
            operator= operator.eq
            )
        )    
    
    par_on_all.add_children([tray1_closed_check, tray2_closed_check])

    return par_on_all



def minor_error_alarm():
    #알람만 보내고, BT계속 진행
    seq_error_mgmt = py_trees.composites.Sequence()

    par_error_check = py_trees.composites.Parallel(
            name="par_error_check",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )

    error_on_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'error_on_check',
                check=py_trees.common.ComparisonExpression(
                variable='error_status',
                value=True,  ##
                operator= operator.eq
            )
        )
    
    error_level_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'error_level_check',
                check=py_trees.common.ComparisonExpression(
                variable='error_level',
                value='Major',  ##
                operator= operator.eq
            )
        )
    
    led_error_alarm = PublishTopic(
        name='led_error_alarm',
        topic_name='alarm_manager/set_alarm',
        topic_type = SetAlarm,
        msg_generate_fn=lambda: SetAlarm(
            level=3,
            source1=2,
            source2=0,
            destination=0,
            error_code='0004',
            message='CANNOT CONTROL LED - '+str(py_trees.blackboard.Blackboard.get('error_cause'))
            )
        )
    
    tts_error_alarm = PublishTopic(
        name='tts_error_alarm',
        topic_name='alarm_manager/set_alarm',
        topic_type = SetAlarm,
        msg_generate_fn=lambda: SetAlarm(
            level=3,
            source1=2,
            source2=0,
            destination=0,
            error_code='0005',
            message='CANNOT CONTROL TTS - '+str(py_trees.blackboard.Blackboard.get('error_cause'))
            )
        )
    
    bgm_error_alarm = PublishTopic(
        name='bgm_error_alarm',
        topic_name='alarm_manager/set_alarm',
        topic_type = SetAlarm,
        msg_generate_fn=lambda: SetAlarm(
            level=3,
            source1=2,
            source2=0,
            destination=0,
            error_code='0006',
            message='CANNOT CONTROL BGM - '+str(py_trees.blackboard.Blackboard.get('error_cause'))
            )
        )

    error_unset = SetBlackBoard(BB_variable='error_status', BB_value=False)

    par_error_alarm = py_trees.composites.Parallel(
            name="par_error_check",
            policy=py_trees.common.ParallelPolicy.SuccessOnOne(
            )
        )
    
    seq_led_error = py_trees.composites.Sequence()
    seq_bgm_error = py_trees.composites.Sequence()
    seq_tts_error = py_trees.composites.Sequence()

    led_error_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'led_error_check',
                check=py_trees.common.ComparisonExpression(
                variable='error_cause',
                value='hardware_manager/led/effect_type_control',  ##
                operator= operator.eq
            )
        )
    
    tts_error_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tts_error_check',
                check=py_trees.common.ComparisonExpression(
                variable='error_cause',
                value='ktmw_bt/tts_control/service',  ##
                operator= operator.eq
            )
        )
    
    bgm_error_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'bgm_error_check',
                check=py_trees.common.ComparisonExpression(
                variable='error_cause',
                value='ktmw_bt/bgm_param/service',  ##
                operator= operator.eq
            )
        )

    seq_error_mgmt.add_children([par_error_check, par_error_alarm, error_unset])
    par_error_check.add_children([error_on_check, error_level_check])
    par_error_alarm.add_children([seq_led_error, seq_tts_error, seq_bgm_error])
    seq_led_error.add_children([led_error_check, led_error_alarm])
    seq_tts_error.add_children([tts_error_check, tts_error_alarm])
    seq_bgm_error.add_children([bgm_error_check, bgm_error_alarm])

    return seq_error_mgmt


def check_critical_error():
    
    seq_critical_error = py_trees.composites.Sequence()

    critical_error_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'critical_error_check',
                check=py_trees.common.ComparisonExpression(
                variable='alarm_code_error_level',
                value=4,
                operator= operator.ge
            )
        )
    
    go_to_critical_error_tree = EnqueueNextService(
        service_name='critical_error_tree', service_version='2.0.0'
    )
    multirobot_available_f3 = PublishTopic(
                            name='multirobot_available_f3',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = False
                                )   
                            ) 
    seq_critical_error.add_children([critical_error_check, multirobot_available_f3, NavigationCancel(), go_to_critical_error_tree])
    
    return seq_critical_error

def go_to_minor_error_tree():
    
    seq_go_to_minor_error_tree = py_trees.composites.Sequence()

    # error_level = 3 and error_code = 맨 앞자리가 1 모두 만족하여야 minor_error_tree로 이동
    par_major_error_check_all = py_trees.composites.Parallel(
            name="par_major_error_check_all",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )
    major_error_level_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'major_error_level_check',
                check=py_trees.common.ComparisonExpression(
                variable='alarm_code_error_level',
                value=3,
                operator= operator.eq
            )
        )
    major_error_code_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'major_error_code_check',
                check=py_trees.common.ComparisonExpression(
                variable='alarm_error_code_1',
                value=1,
                operator= operator.eq
            )
        )

    
    go_to_minor_error_tree = EnqueueNextService(
        service_name='minor_error_tree', service_version='2.0.0'
    )
    
    multirobot_available_f4 = PublishTopic(
                            name='multirobot_available_f4',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = False
                                )   
                            ) 

    seq_go_to_minor_error_tree.add_children([par_major_error_check_all, multirobot_available_f4, NavigationCancel(), go_to_minor_error_tree])
    par_major_error_check_all.add_children([major_error_level_check, major_error_code_check])
    
    return seq_go_to_minor_error_tree



def create_root():
    

    seq_init = py_trees.composites.Sequence()

    BB_start = BB_init()

    Set_Route = SetRouteIndex()

    Set_Goals = SetGoalIndex()


    # root 선언 - parallel
    root = py_trees.composites.Parallel(
        name="Moving_Tree",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    
    
    halt_seq_stop = py_trees.composites.Sequence()

    stop_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'stop_check',
            check=py_trees.common.ComparisonExpression(
            variable="halt_status",
            value='stop',
            operator= operator.eq
        )
    )

    pause_nav_true = NavigationPause(pause=True)

    pause_check = pause_result_check()

    pause_alarm =  PublishTopic(
        name='pause_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_pause',
            action='nav_pause',
            action_target='nav_pause',
            action_result=True
            )
        )     

    resume_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'resume_check',
            check=py_trees.common.ComparisonExpression(
            variable="halt_status",
            value='resume',
            operator= operator.eq
        )
    )



    def request_generate_fn_pause():
        req = SetBool.Request()
        req.data = False
        return req
    
    def response_fn_pause(response):
        print(response.success)

    start_nav_again = ServiceCall(
        service_name='nav/pause',
        service_type=SetBool,
        request_generate_fn=request_generate_fn_pause,
        response_fn=response_fn_pause,
        name='start_nav_again'
    )

    pause_off_alarm =  PublishTopic(
        name='pause_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='nav_pause',
            action='nav_pause',
            action_target='nav_pause',
            action_result=False
            )
        )     




    seq_main = py_trees.composites.Sequence()

    start_alarm = PublishTopic(
        name='start_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),  
            tray_id=[0],
            task_status='task_start',
            action='task_start',
            action_target='task_start',
            action_result=True
            )
        )

    par_llm_bgm = py_trees.composites.Parallel(
        name="par_llm_bgm",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_bgm_moving = py_trees.composites.Sequence()
    seq_bgm_new = py_trees.composites.Sequence()
    seq_bgm_classic = py_trees.composites.Sequence()
    
    bgm_moving_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'bgm_moving_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_bgm",
            value='1',
            operator= operator.eq
        )
    )
    
    bgm_new_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'bgm_new_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_bgm",
            value='2',
            operator= operator.eq
        )
    )
    
    bgm_classic_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'bgm_classic_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_bgm",
            value='3',
            operator= operator.eq
        )
    )
    
    bgm_moving = BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=True, repeat=True)
    bgm_new = BGMPlay(bgm_name= "serious_alarm", play=True, repeat=True) # aespa
    bgm_classic = BGMPlay(bgm_name= "serious_alarm", play=True, repeat=True) # classic

    def request_generate_fn_start_nav():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("route_index_num_waypoint_poi")
        req.goal_label = ''
        req.mode = 'normal'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_start_nav(response):
        print(response.result)

    start_nav = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_start_nav,
        response_fn=response_fn_start_nav,
        name='start_nav'
    )





    par_arrived_check = py_trees.composites.Parallel(
        name="par_arrived_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    arrived_check_state = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'arrived_check_state',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    arrived_check_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'arrived_check_mode',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='normal',
            operator=operator.eq
        )
    )

    # led_arrived = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_REVERSE_SEQUENTIAL_LED_OFF, # 로테이션
    #     period_ms=2500,
    #     on_ms=0,
    #     repeat_count=1)
    
    led_arrived = PublishTopic(
                name='led_arrived',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2500,
                    on_ms=0,
                    repeat_count=1
                    )   
                )  

    wait_led= py_trees.timers.Timer("led_show", duration=0.75)


    par_last_goal_check = py_trees.composites.Parallel(
        name="par_last_goal_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_not_last_goal = py_trees.composites.Sequence()

    wait_for_last_flag1 = py_trees.behaviours.WaitForBlackboardVariable('not_last_goal_check_variable')
    wait_for_last_flag2 = py_trees.behaviours.WaitForBlackboardVariable('not_last_goal_check_value')

    not_last_goal_check_variable = GetandSetBlackBoard(BB_variable='not_last_goal_check_variable',BB_value='goal_index_num_current_goal_id')
    not_last_goal_check_value = GetandSetBlackBoard(BB_variable='not_last_goal_check_value',BB_value='route_index_num_waypoint_poi')
    
    
    not_last_goal_check = compareBBvariableforincorrect(BB_variable1='not_last_goal_check_variable', BB_variable2='not_last_goal_check_value')

    par_next_moving = py_trees.composites.Parallel(
        name="par_next_moving",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_ev = py_trees.composites.Sequence()

    ev_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'ev_check',
        check=py_trees.common.ComparisonExpression(
            variable='route_index_num_is_ev',
            value=True,
            operator=operator.eq
        )
        )
    

    go_to_ev = EnqueueNextService(
        service_name='ev_tree', service_version='')

    seq_not_ev = py_trees.composites.Sequence()

    not_ev_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'not_ev_check',
        check=py_trees.common.ComparisonExpression(
            variable='route_index_num_is_ev',
            value=False,
            operator=operator.eq
        )
    )
    
    route_index_num_add_1 = GetandSetBlackBoard(BB_variable='route_index_num',BB_value='route_index_num_+1')
    route_index_num_add_2 = GetandSetBlackBoard(BB_variable='route_index_num',BB_value='route_index_num_+2')

    mapchange_set_route_index = SetRouteIndexforNextPOI()

    par_map_change = py_trees.composites.Parallel(
        name="par_map_change",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )

    seq_map_not_change = py_trees.composites.Sequence()

    map_not_change_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'map_not_change_check',
        check=py_trees.common.ComparisonExpression(
            variable='route_index_num_+1_map_change',
            value=False,
            operator=operator.eq
        )
    )

    seq_map_change = py_trees.composites.Sequence()

    map_change_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'map_change_check',
        check=py_trees.common.ComparisonExpression(
            variable='route_index_num_+1_map_change',
            value=True,
            operator=operator.eq
        )
    )

    before_Mapchange_nextPOI = Before_Mapchange_nextPOI()
    
    def request_generate_fn_load_des_map():
        req                   = NavMapLoad.Request()
        req.map_name          = py_trees.blackboard.Blackboard.get('route_index_num_+1_map_name')
        req.reset             = False 
        req.localization_only = True 
        req.resolution        = 0.0 
        req.label             = py_trees.blackboard.Blackboard.get('route_index_num_+1_waypoint_poi') # changed mw
        return req

    def response_fn_load_des_map(response):
        py_trees.blackboard.Blackboard.set('load_map_check', response.result) 

    map_change = ServiceCall(service_type=NavMapLoad, 
                          service_name='nav/map_load', 
                          request_generate_fn= request_generate_fn_load_des_map,
                          response_fn= response_fn_load_des_map, 
                          name='map_change')
    
    
    go_to_moving = EnqueueNextService(
        service_name='moving_tree', service_version='')


    seq_last_goal = py_trees.composites.Sequence()

    wait_for_last_flag3 = py_trees.behaviours.WaitForBlackboardVariable('last_goal_check_variable')
    wait_for_last_flag4 = py_trees.behaviours.WaitForBlackboardVariable('last_goal_check_value')

    last_goal_check_variable = GetandSetBlackBoard(BB_variable='last_goal_check_variable',BB_value='goal_index_num_current_goal_id')
    last_goal_check_value = GetandSetBlackBoard(BB_variable='last_goal_check_value',BB_value='route_index_num_waypoint_poi')
    
    
    last_goal_check = compareBBvariableforcorrect(BB_variable1='last_goal_check_variable', BB_variable2='last_goal_check_value')


    
    BGM_off_arrived = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)

    arrived_alarm = PublishTopic(
        name='arrived_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='task_arrived',
            action='task_arrived',
            action_target='task_arrived',
            action_result=True
            )
        )
    
    par_next_step = py_trees.composites.Parallel(
        name="par_next_moving",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_unload_check = py_trees.composites.Sequence()

    unload_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'unload_check',
        check=py_trees.common.ComparisonExpression(
            variable='goal_index_num_current_service_code',
            value=101,
            operator=operator.eq
        )
    )

    seq_load_check = py_trees.composites.Sequence()

    load_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'load_check',
        check=py_trees.common.ComparisonExpression(
            variable='goal_index_num_current_service_code',
            value=102,
            operator=operator.eq
        )
    )

    seq_902_check = py_trees.composites.Sequence()

    unload_check_902 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'unload_check_902',
        check=py_trees.common.ComparisonExpression(
            variable='goal_index_num_current_service_code',
            value=902,
            operator=operator.eq
        )
    )

    par_unload_tray_check_902 = py_trees.composites.Parallel(
        name="par_unload_tray_check_902",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    par_unload_tray_check = py_trees.composites.Parallel(
        name="par_next_moving",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_one_tray_unload = py_trees.composites.Sequence()

    one_tray_unload_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'one_tray_unload_check',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=1,
            operator=operator.eq
        )
    )

    go_to_tray_unload1 = EnqueueNextService(
        service_name='tray_unload1', service_version='')
    
    seq_multi_tray_unload = py_trees.composites.Sequence()

    multi_tray_unload_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'multi_tray_unload_check',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=2,
            operator=operator.eq
        )
    )

    go_to_tray_unload2 = EnqueueNextService(
        service_name='tray_unload2', service_version='')


    seq_one_tray_unload_902 = py_trees.composites.Sequence()

    one_tray_unload_check_902 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'one_tray_unload_check_902',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=1,
            operator=operator.eq
        )
    )

    go_to_tray_unload1_902 = EnqueueNextService(
        service_name='tray_fail1', service_version='')
    
    seq_multi_tray_unload_902 = py_trees.composites.Sequence()

    multi_tray_unload_check_902 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'multi_tray_unload_check_902',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=2,
            operator=operator.eq
        )
    )

    go_to_tray_unload2_902 = EnqueueNextService(
        service_name='tray_fail2', service_version='')
    

    par_load_tray_check = py_trees.composites.Parallel(
        name="par_load_tray_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_one_tray_load = py_trees.composites.Sequence()

    one_tray_load_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'one_tray_load_check',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=1,
            operator=operator.eq
        )
    )

    go_to_tray_load1 = EnqueueNextService(
        service_name='tray_load1', service_version='')

    seq_multi_tray_load = py_trees.composites.Sequence()

    multi_tray_load_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'multi_tray_load_check',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=2,
            operator=operator.eq
        )
    )

    go_to_tray_load2 = EnqueueNextService(
        service_name='tray_load2', service_version='')
    
    
    seq_not_tray = py_trees.composites.Sequence()

    not_tray_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'not_tray_check',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num", ############ 여기서 trigger 된듯
            value=0,
            operator=operator.eq
        )
    )

    just_moving_finished_alarm = PublishTopic(
        name='just_moving_finished_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
            tray_id=[0],
            task_status='task_finished',
            action='task_finished',
            action_target='task_finished',
            action_result=True
            )
        )
    
    go_to_idle = EnqueueNextService(
        service_name='BB_clear', service_version='')
    
    seq_charging = py_trees.composites.Sequence()

    charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="goal_index_num_current_service_code", ############ 여기서 trigger 된듯
            value=903,
            operator=operator.eq
        )
    )

    not_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'not_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="goal_index_num_current_service_code", ############ 여기서 trigger 된듯
            value=903,
            operator=operator.ne
        )
    )
    
    go_to_charging = EnqueueNextService(
        service_name='charging_tree', service_version='')


    seq_cancel_tray = py_trees.composites.Sequence()

    cancel_flag_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'cancel_flag_check',
        check=py_trees.common.ComparisonExpression(
            variable="cancel_flag", ############ 이게 걸려야 하는것 같은데?
            value=1,
            operator=operator.eq
        )
    )

    par_cancel_tray_check = py_trees.composites.Parallel(
        name="par_cancel_tray_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_one_cancel_tray = py_trees.composites.Sequence()

    one_cancel_tray_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'one_cancel_tray_check',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=1,
            operator=operator.eq
        )
    )

    cancel_flag_unset1 = py_trees.behaviours.UnsetBlackboardVariable('cancel_flag')

    go_to_cancel_tray1 = EnqueueNextService(
        service_name='tray_fail1', service_version='')
    
    seq_multi_cancel_tray = py_trees.composites.Sequence()

    multi_cancel_tray_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'multi_cancel_tray_check',
        check=py_trees.common.ComparisonExpression(
            variable="tray_num",
            value=2,
            operator=operator.eq
        )
    )

    cancel_flag_unset2 = py_trees.behaviours.UnsetBlackboardVariable('cancel_flag')

    go_to_cancel_tray2 = EnqueueNextService(
        service_name='tray_fail2', service_version='')


    test2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'test2',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='test2',
            operator= operator.eq
        )
    )
    test3 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'test3',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='test3',
            operator= operator.eq
        )
    )
    test4 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'test4',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='test4',
            operator= operator.eq
        )
    )
    test5 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'test5',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='test5',
            operator= operator.eq
        )
    )
    test6 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'test6',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='test6',
            operator= operator.eq
        )
    )

    tts_password = TTSPlay(tts_name='password', play=True, sequence=True)
    tts_delivering_resume = TTSPlay(tts_name='delivering_resume', play=True, sequence=True)



    Before_EV_Tree1 = Before_EV_Tree()

    #일시정지
    # led_start_on_halt1 = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, # 점등
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    # led_start_on_halt2 = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, #점등
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    led_start_on_halt1 = PublishTopic(
                name='led_start_on_halt1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_halt2 = PublishTopic(
                name='led_start_on_halt2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  


    #비밀번호 맞고 다시 일시정지

    


    
    # led_start_on_moving1 = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_SEQUENTIAL_LED_OFF, #dimming
    #     period_ms=2000,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_start_on_moving2 = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_SEQUENTIAL_LED_OFF, #dimming
    #     period_ms=2000,
    #     on_ms=0,
    #     repeat_count=0)
    
    par_llm_led = py_trees.composites.Parallel(
        name="par_llm_led",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_llm_led_colorful = py_trees.composites.Sequence()
    seq_llm_led_calm = py_trees.composites.Sequence()
    
    llm_led_colorful_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_colorful_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_calm_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_calm_check',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    par_llm_led_colorful = py_trees.composites.Parallel(
        name="par_llm_led_colorful",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    par_llm_led_calm = py_trees.composites.Parallel(
        name="par_llm_led_colorful",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    
    seq_llm_led_yellow1 = py_trees.composites.Sequence()
    seq_llm_led_blue1 = py_trees.composites.Sequence()
    seq_llm_led_green1 = py_trees.composites.Sequence()
    seq_llm_led_general1 = py_trees.composites.Sequence()
    seq_llm_led_orange1 = py_trees.composites.Sequence()
    seq_llm_led_red1 = py_trees.composites.Sequence()
    
    seq_llm_led_yellow2 = py_trees.composites.Sequence()
    seq_llm_led_blue2 = py_trees.composites.Sequence()
    seq_llm_led_green2 = py_trees.composites.Sequence()
    seq_llm_led_general2 = py_trees.composites.Sequence()
    seq_llm_led_orange2 = py_trees.composites.Sequence()
    seq_llm_led_red2 = py_trees.composites.Sequence()
    
    llm_led_yellow_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_yellow_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_blue_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_blue_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    llm_led_green_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_green_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='3',
            operator= operator.eq
        )
    )
    
    llm_led_general_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_general_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='4',
            operator= operator.eq
        )
    )
    
    llm_led_orange_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_orange_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='5',
            operator= operator.eq
        )
    )
    
    llm_led_red_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_red_check1',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='6',
            operator= operator.eq
        )
    )
    
    llm_led_yellow_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_yellow_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='1',
            operator= operator.eq
        )
    )
    
    llm_led_blue_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_blue_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='2',
            operator= operator.eq
        )
    )
    
    llm_led_green_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_green_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='3',
            operator= operator.eq
        )
    )
    
    llm_led_general_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_general_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='4',
            operator= operator.eq
        )
    )
    
    llm_led_orange_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_orange_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='5',
            operator= operator.eq
        )
    )
    
    llm_led_red_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'llm_led_red_check2',
            check=py_trees.common.ComparisonExpression(
            variable="llm_led_effect",
            value='6',
            operator= operator.eq
        )
    )
    
    led_start_on_moving1_yellow1 = PublishTopic(
                name='led_start_on_moving1_yellow1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_yellow1 = PublishTopic(
                name='led_start_on_moving2_yellow1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_yellow2 = PublishTopic(
                name='led_start_on_moving1_yellow2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_yellow2 = PublishTopic(
                name='led_start_on_moving2_yellow2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_blue1 = PublishTopic(
                name='led_start_on_moving1_blue1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_blue1 = PublishTopic(
                name='led_start_on_moving2_blue1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_blue2 = PublishTopic(
                name='led_start_on_moving1_blue2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_blue2 = PublishTopic(
                name='led_start_on_moving2_blue2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_green1 = PublishTopic(
                name='led_start_on_moving1_green1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_green1 = PublishTopic(
                name='led_start_on_moving2_green1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_green2 = PublishTopic(
                name='led_start_on_moving1_green2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_green2 = PublishTopic(
                name='led_start_on_moving2_green2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_general1 = PublishTopic(
                name='led_start_on_moving1_general1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_general1 = PublishTopic(
                name='led_start_on_moving2_general1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_general2 = PublishTopic(
                name='led_start_on_moving1_general2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_general2 = PublishTopic(
                name='led_start_on_moving2_general2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_orange1 = PublishTopic(
                name='led_start_on_moving1_orange1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_orange1 = PublishTopic(
                name='led_start_on_moving2_orange1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_orange2 = PublishTopic(
                name='led_start_on_moving1_orange2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_orange2 = PublishTopic(
                name='led_start_on_moving2_orange2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=128, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_red1 = PublishTopic(
                name='led_start_on_moving1_red1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_red1 = PublishTopic(
                name='led_start_on_moving2_red1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=4,
                    period=1000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )
    
    led_start_on_moving1_red2 = PublishTopic(
                name='led_start_on_moving1_red2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    led_start_on_moving2_red2 = PublishTopic(
                name='led_start_on_moving2_red2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )

    # 일시정지 후 Resume 했을 때 다시 무빙
    # led_start_on_restart_f = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_SEQUENTIAL_LED_OFF, # dimming
    #     period_ms=2000,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_start_on_restart_r = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_SEQUENTIAL_LED_OFF, #dimming
    #    period_ms=2000,
    #     on_ms=0,
    #     repeat_count=0)

    led_start_on_restart_f = PublishTopic(
                name='led_start_on_restart_f',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    led_start_on_restart_r = PublishTopic(
                name='led_start_on_restart_r',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    

    wait_led3= py_trees.timers.Timer("led_show", duration=2.5)    


    # led_off_arrived_rear = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_on_arrived_front = LEDControl(#???
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)    


    led_off_arrived_rear = PublishTopic(
                name='led_off_arrived_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    led_on_arrived_front = PublishTopic(
                name='led_on_arrived_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    
    no_touch_par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[resume_check1],
            synchronise=False
        )
    ) 


    par_moving = py_trees.composites.Parallel(
        name="par_moving",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )
    seq_arrived = py_trees.composites.Sequence()
    seq_tray_closed = py_trees.composites.Sequence()

    par_tray_check = py_trees.composites.Parallel(
        name="par_tray_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq_tray_closed],
            synchronise=False
        )        
    )

    seq_tray_open = py_trees.composites.Sequence()


    root_sel = py_trees.composites.Selector('moving_tree')
    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
    )

    wait_for_next1 = py_trees.timers.Timer("wait_for_next", duration=0.0)
    wait_for_next2 = py_trees.timers.Timer("wait_for_next", duration=0.0)

    set_finished_flag = SetBlackBoard(BB_variable='finished_flag', BB_value=True)

    finished_flag_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'finished_flag_check',
                check=py_trees.common.ComparisonExpression(
                variable='finished_flag',
                value=True,  
                operator= operator.eq
            )
        )
    
    halt_seq = py_trees.composites.Sequence()

    halt_par = py_trees.composites.Parallel(
        name="halt_par",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[finished_flag_check],
            synchronise=False
        )
        )
    
    map_change_alarm = PublishTopic(
                            name='map_change_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id=py_trees.blackboard.Blackboard.get('route_index_num_waypoint_poi'),
                                tray_id=[0],             
                                task_status = 'map_change',
                                action = 'map_change',
                                action_target = 'map_change',
                                action_result = True
                                )   
                            )
    
    halt_idling = Idling()

    closed_check_seq = py_trees.composites.Sequence()


    par_tray_all_closed = py_trees.composites.Parallel(
        name="par_tray_all_closed",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )        
    )

    tray1_closed_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_1_open_status",
            value=1,
            operator= operator.eq
            )
        )
    
    tray2_closed_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=1,
            operator= operator.eq
            )
        )
    
    multirobot_available_t = PublishTopic(
                            name='multirobot_available_t',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = True
                                )   
                            ) 
    multirobot_available_f = PublishTopic(
                            name='multirobot_available_f',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = False
                                )   
                            ) 
    
    multirobot_available_t2 = PublishTopic(
                            name='multirobot_available_t2',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = True
                                )   
                            ) 
    multirobot_available_f2 = PublishTopic(
                            name='multirobot_available_f2',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id='',
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'moving',
                                action = 'multi_robot',
                                action_target = 'multi_robot',
                                action_result = False
                                )   
                            ) 
    led_start_on_recovery_front = PublishTopic(
                name='led_start_on_recovery_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )     

    led_start_on_recovery_rear = PublishTopic(
                name='led_start_on_recovery_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=255),
                    effect=3,
                    period=2000,
                    on_ms=0,
                    repeat_count=0
                    )   
                )

    led_start_on_lineup_front = PublishTopic(
                name='led_start_on_lineup_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )     

    led_start_on_lineup_rear = PublishTopic(
                name='led_start_on_lineup_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=2,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )

    check_pre_moving = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'check_pre_moving',
        check=py_trees.common.ComparisonExpression(
            variable="pre_nav_status",
            value='moving',
            operator=operator.eq
        )
    )
    check_pre_fleet = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'check_pre_fleet',
        check=py_trees.common.ComparisonExpression(
            variable="pre_nav_status",
            value='fleet',
            operator=operator.eq
        )
    )
    check_pre_recovery = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'check_pre_recovery',
        check=py_trees.common.ComparisonExpression(
            variable="pre_nav_status",
            value='recovery',
            operator=operator.eq
        )
    )

    par_check_not_fleet_recov = py_trees.composites.Parallel(
        name="par_check_not_fleet_recov",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    ) 

    check_not_pre_fleet = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'check_not_pre_fleet',
        check=py_trees.common.ComparisonExpression(
            variable="pre_nav_status",
            value='fleet',
            operator=operator.ne
        )
    )
    check_not_pre_recovery = py_trees.behaviours.WaitForBlackboardVariableValue(
        name = 'check_not_pre_recovery',
        check=py_trees.common.ComparisonExpression(
            variable="pre_nav_status",
            value='recovery',
            operator=operator.ne
        )
    )
    par_before_halt = py_trees.composites.Parallel(
        name="par_before_halt",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 
    seq_pre_moving =  py_trees.composites.Sequence()
    seq_pre_fleet =  py_trees.composites.Sequence()
    seq_pre_recovery = py_trees.composites.Sequence()

    # 이동 서비스
    root_sel.add_children([seq_init, go_to_ciritcal_error2])

    seq_init.add_children([BB_start,Set_Route,Set_Goals, root])
    root.add_children([tray_stuck_seq_new(), check_critical_error(), go_to_minor_error_tree(), parallel_get_msg_toBB(), minor_error_alarm(), halt_reserve(), check_manual_drive(), check_manual_charge(), emergency_button_check(), battery_under_15(), halt_seq, halt_cancel_seq(), seq_main])

    #주행중 일시정지(stop)
    halt_seq.add_children([halt_par, halt_idling]) 
    halt_par.add_children([halt_seq_stop, finished_flag_check])
    halt_seq_stop.add_children([stop_check, tts_password, multirobot_available_f2, pause_nav_true, pause_check, pause_alarm, led_start_on_halt1, led_start_on_halt2, no_touch_par, par_tray_check, par_before_halt])
   
    ####### editing
    par_before_halt.add_children([seq_pre_moving, seq_pre_fleet, seq_pre_recovery])
    seq_pre_moving.add_children([par_check_not_fleet_recov,led_start_on_restart_f, led_start_on_restart_r, tts_delivering_resume ])
    par_check_not_fleet_recov.add_children([check_not_pre_fleet,check_not_pre_recovery])
    seq_pre_fleet.add_children([check_pre_fleet, led_start_on_lineup_front, led_start_on_lineup_rear])
    seq_pre_recovery.add_children([check_pre_recovery,led_start_on_recovery_front, led_start_on_recovery_rear ])
    ######

    par_tray_check.add_children([seq_tray_open, seq_tray_closed])
    seq_tray_open.add_children([open_check(), opened_tray_check_and_close(), par_tray_all_closed])
    seq_tray_closed.add_children([close_check(), multirobot_available_t2, start_nav_again, pause_off_alarm])

    par_tray_all_closed.add_children([tray1_closed_check1, tray2_closed_check1])

    no_touch_par.add_children([resume_check1, time_delay_check_seq()])
    

    #주행 시작
    seq_main.add_children([start_alarm, par_llm_bgm, par_llm_led, multirobot_available_t, start_nav, par_moving])
    
    par_llm_bgm.add_children([seq_bgm_moving, seq_bgm_new, seq_bgm_classic])
    seq_bgm_moving.add_children([bgm_moving_check, bgm_moving])
    seq_bgm_new.add_children([bgm_new_check, bgm_new])
    seq_bgm_classic.add_children([bgm_classic_check, bgm_classic])
    
    par_llm_led.add_children([seq_llm_led_colorful, seq_llm_led_calm])
    seq_llm_led_colorful.add_children([llm_led_colorful_check, par_llm_led_colorful])
    seq_llm_led_calm.add_children([llm_led_calm_check, par_llm_led_calm])
    
    par_llm_led_colorful.add_children([seq_llm_led_yellow1, seq_llm_led_blue1, seq_llm_led_green1, seq_llm_led_general1, seq_llm_led_orange1, seq_llm_led_red1])
    par_llm_led_calm.add_children([seq_llm_led_yellow2, seq_llm_led_blue2, seq_llm_led_green2, seq_llm_led_general2, seq_llm_led_orange2, seq_llm_led_red2])
    
    seq_llm_led_yellow1.add_children([llm_led_yellow_check1, led_start_on_moving1_yellow1, led_start_on_moving2_yellow1])
    seq_llm_led_blue1.add_children([llm_led_blue_check1, led_start_on_moving1_blue1, led_start_on_moving2_blue1])
    seq_llm_led_green1.add_children([llm_led_green_check1, led_start_on_moving1_green1, led_start_on_moving2_green1])
    seq_llm_led_general1.add_children([llm_led_general_check1, led_start_on_moving1_general1, led_start_on_moving2_general1])
    seq_llm_led_orange1.add_children([llm_led_orange_check1, led_start_on_moving1_orange1, led_start_on_moving2_orange1])
    seq_llm_led_red1.add_children([llm_led_red_check1, led_start_on_moving1_red1, led_start_on_moving2_red1])
    
    seq_llm_led_yellow2.add_children([llm_led_yellow_check2, led_start_on_moving1_yellow2, led_start_on_moving2_yellow2])
    seq_llm_led_blue2.add_children([llm_led_blue_check2, led_start_on_moving1_blue2, led_start_on_moving2_blue2])
    seq_llm_led_green2.add_children([llm_led_green_check2, led_start_on_moving1_green2, led_start_on_moving2_green2])
    seq_llm_led_general2.add_children([llm_led_general_check2, led_start_on_moving1_general2, led_start_on_moving2_general2])
    seq_llm_led_orange2.add_children([llm_led_orange_check2, led_start_on_moving1_orange2, led_start_on_moving2_orange2])
    seq_llm_led_red2.add_children([llm_led_red_check2, led_start_on_moving1_red2, led_start_on_moving2_red2])
    
    par_moving.add_children([while_moving_par(), seq_arrived])

    #도착 이후(이후 트레이 상태와 서비스를 고려하여 다음 서비스 결정)
    seq_arrived.add_children([par_arrived_check, multirobot_available_f, set_finished_flag, led_off_arrived_rear, wait_led3, led_on_arrived_front, wait_for_next1 ,wait_for_next2, par_last_goal_check])
    par_arrived_check.add_children([arrived_check_state, arrived_check_mode])
    par_last_goal_check.add_children([seq_not_last_goal, seq_last_goal])

    seq_not_last_goal.add_children([not_last_goal_check_variable,not_last_goal_check_value, wait_for_last_flag1, wait_for_last_flag2 ,not_last_goal_check, par_next_moving])
    par_next_moving.add_children([seq_ev, seq_not_ev])
    seq_ev.add_children([ev_check, Before_EV_Tree1, go_to_ev])
    seq_not_ev.add_children([not_ev_check, mapchange_set_route_index, par_map_change, go_to_moving])
    par_map_change.add_children([seq_map_not_change, seq_map_change])
    seq_map_not_change.add_children([map_not_change_check, route_index_num_add_1])
    seq_map_change.add_children([map_change_check, map_change_alarm ,map_change, route_index_num_add_2])

    seq_last_goal.add_children([last_goal_check_variable, last_goal_check_value, wait_for_last_flag3, wait_for_last_flag4, last_goal_check, led_arrived, BGM_off_arrived, arrived_alarm, wait_led, par_next_step])
    par_next_step.add_children([seq_unload_check, seq_load_check, seq_902_check, seq_not_tray, seq_charging, seq_cancel_tray])
    seq_unload_check.add_children([unload_check, par_unload_tray_check])
    seq_load_check.add_children([load_check, par_load_tray_check])
    seq_902_check.add_children([unload_check_902, par_unload_tray_check_902])
    seq_not_tray.add_children([not_charging_check, not_tray_check, just_moving_finished_alarm, go_to_idle])
    seq_charging.add_children([charging_check, go_to_charging])
    seq_cancel_tray.add_children([cancel_flag_check, par_cancel_tray_check])

    par_cancel_tray_check.add_children([seq_one_cancel_tray, seq_multi_cancel_tray])
    seq_one_cancel_tray.add_children([one_cancel_tray_check, cancel_flag_unset1, go_to_cancel_tray1])
    seq_multi_cancel_tray.add_children([multi_cancel_tray_check, cancel_flag_unset2, go_to_cancel_tray2])

    par_unload_tray_check.add_children([seq_one_tray_unload, seq_multi_tray_unload])
    par_load_tray_check.add_children([seq_one_tray_load, seq_multi_tray_load])
    par_unload_tray_check_902.add_children([seq_one_tray_unload_902, seq_multi_tray_unload_902])

    seq_one_tray_load.add_children([one_tray_load_check, go_to_tray_load1])
    seq_multi_tray_load.add_children([multi_tray_load_check, go_to_tray_load2])
    seq_one_tray_unload.add_children([one_tray_unload_check, go_to_tray_unload1])
    seq_multi_tray_unload.add_children([multi_tray_unload_check, go_to_tray_unload2])
    seq_one_tray_unload_902.add_children([one_tray_unload_check_902, go_to_tray_unload1_902])
    seq_multi_tray_unload_902.add_children([multi_tray_unload_check_902, go_to_tray_unload2_902])



    return root_sel
