'''
KT Robot BehaviorTree version 2.0.1

Copyright ⓒ 2023 kt corp. All rights reserved.

This is a proprietary software of kt corp, and you may not use this file except in
compliance with license agreement with kt corp. Any redistribution or use of this
software, with or without modification shall be strictly prohibited without prior written
approval of kt corp, and the copyright notice above does not evidence any actual or
intended publication of such software.
'''

import py_trees
import operator

#from params_manager import ParamsManager
from ktmw_srvmgr_lib.common import *
from ktmw_bt_interfaces.msg import *
from slam_manager_msgs.srv import *
from kt_msgs.msg import EVControl, EVBoardStatus,EVControlResponse, EVControlNoti, LEDState, Location, LEDEffect

from ktmw_srvmgr_lib.navigation import NavigationStart, NavigationCancel, NavigationPause
from kt_nav_msgs.msg import NavStatus
from ktmw_bt_interfaces.msg import HaltStatus

from kt_nav_msgs.srv import SetNavGoal


from std_msgs.msg import Int8MultiArray, Bool
import sensor_msgs.msg as sensor_msgs
from kt_msgs.msg import BoolCmdArray

from std_srvs.srv import SetBool


from ktmw_bt_interfaces.msg import TaskStatus, HaltStatus, HRI, SoundControl
from kt_nav_msgs.msg import NavStatus

from ktmw_srvmgr_lib.common import  SubscribeTopic, TTSPlay, BGMPlay, EnqueueNextService, PublishTopic, SetBlackBoard, compareBBvariableforcorrect, compareBBvariableforincorrect
from ktmw_srvmgr_lib.hardware import (BoxOpen,BoxClose,LEDControl)

from slam_manager_msgs.srv import NavMapLoad
from ktmw_srvmgr_lib.common import ServiceCall, NoResponseCheck, GetCurrentTime, InitCount

from config_manager_msgs.srv import GetPoiRoute

from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm

import logging

logging.basicConfig(filename="/home/kt/ev_tree.log",level=logging.DEBUG)

       
'''
Elevator service
'''
SERVICE_NAME = 'ev-tree'
SERVICE_VERSION = '0.1.0'

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
        
class Add_1(py_trees.behaviour.Behaviour):
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
        self.bb_value=py_trees.blackboard.Blackboard.get(self.BB_variable) +1 
        py_trees.blackboard.Blackboard.set(self.BB_variable, self.bb_value)
                
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

        py_trees.blackboard.Blackboard.set('previous_tree', 'ev_tree')
        py_trees.blackboard.Blackboard.set('fail_count', 5)
        py_trees.blackboard.Blackboard.set('evi_success', None)
        py_trees.blackboard.Blackboard.set('hallcall_count', 1)
        py_trees.blackboard.Blackboard.set('error_flag', None)

        py_trees.blackboard.Blackboard.set('call_board_point', 'no')
        py_trees.blackboard.Blackboard.set('des_get_off_point', 'no')



    def update(self):
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
        py_trees.blackboard.Blackboard.set('goal_index_num_current_service_code', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_service_code'))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_task_id', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_task_id'))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_tray_id', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_tray_id'))
        py_trees.blackboard.Blackboard.set('tray_num', len(py_trees.blackboard.Blackboard.get('goal_index_num_current_tray_id')))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_goal_id', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_goal_id' ))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_seq', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_seq' ))
        py_trees.blackboard.Blackboard.set('goal_index_num_current_lock_option', py_trees.blackboard.Blackboard.get(str(self.index)+'/current_lock_option' ))



    def update(self):

            
        return py_trees.common.Status.SUCCESS



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

class EVF_check(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def initialise(self):
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)

    def update(self):
        
        if self.bb1 == 'normal' and self.bb2 == 'finished':
            return py_trees.common.Status.SUCCESS    

        else: 
            return py_trees.common.Status.RUNNING 

class set_goal_abcd(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        abc = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        py_trees.blackboard.Blackboard.set('abcd', abc)
        return py_trees.common.Status.SUCCESS


class NavStatus_check1(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):

        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)

        if self.bb1 == 'normal' and self.bb2 == 'finished':
            return py_trees.common.Status.SUCCESS    

        else: 
            return py_trees.common.Status.RUNNING 
        
class NavStatus_check2(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD


    def update(self):
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)

        
            
        if self.bb1 == 'ev_in' and self.bb2 == 'moving':
            return py_trees.common.Status.SUCCESS    

        else: 
            return py_trees.common.Status.RUNNING 

class NavStatus_check3(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD



    def update(self):
        
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)

        if self.bb1 == 'ev_in' and self.bb2 == 'failed':
            return py_trees.common.Status.SUCCESS    

        else: 
            return py_trees.common.Status.RUNNING 

class NavStatus_check4(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD



    def update(self):
        
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)


        if self.bb1 == 'ev_in' and self.bb2 == 'finished':
            logging.debug("ev in")
            return py_trees.common.Status.SUCCESS          
            
        else: 
            return py_trees.common.Status.RUNNING 

class NavStatus_check5(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD



    def update(self):
                 
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)
            
        if self.bb1 == 'ev_out' and self.bb2 == 'moving':
            return py_trees.common.Status.SUCCESS     

        else: 
            return py_trees.common.Status.RUNNING 

class NavStatus_check6(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD



    def update(self):
        
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)

        if self.bb1 == 'ev_out' and self.bb2 == 'failed':
            return py_trees.common.Status.SUCCESS     
        

        else: 
            return py_trees.common.Status.RUNNING 

class NavStatus_check7(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD



    def update(self):
        
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)
        
        if self.bb1 == 'ev_out' and self.bb2 == 'finished':
            return py_trees.common.Status.SUCCESS     

        else: 
            return py_trees.common.Status.RUNNING 
                                           

class Flag_Count_Set(py_trees.behaviour.Behaviour):

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
        
        py_trees.blackboard.Blackboard.set("EVCFI_count", 5)
        py_trees.blackboard.Blackboard.set("EVR_count", 5)
        py_trees.blackboard.Blackboard.set("Flag1", True)
        py_trees.blackboard.Blackboard.set("Flag2", True)
        py_trees.blackboard.Blackboard.set("Flag3", True)
        
        return py_trees.common.Status.SUCCESS    

class EV_floor_check(py_trees.behaviour.Behaviour):
    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1 # mode
        self.BB_variable2 = BB_variable2 # state


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        

        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)

        if self.bb1 ==  self.bb2 :
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING    

class EVI_set(py_trees.behaviour.Behaviour):
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
        
        EVF_name = py_trees.blackboard.Blackboard.get("call_board_point")
        EVI_name = EVF_name.replace("EVF", "EFI")

        py_trees.blackboard.Blackboard.set("EVI_board_point", EVI_name)

        return py_trees.common.Status.SUCCESS 

class next_EVI_set(py_trees.behaviour.Behaviour):
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
    
        EVI_bp_name = py_trees.blackboard.Blackboard.get("EVI_board_point")
        next_EVI_bp = py_trees.blackboard.Blackboard.get("route_index_num_+1_map_name") + "_" +EVI_bp_name.split("_")[1]

        py_trees.blackboard.Blackboard.set("next_EVI_board_point", next_EVI_bp)

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

class Route_Index_Add_2(py_trees.behaviour.Behaviour):
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

    def update(self):
        self.next_num =py_trees.blackboard.Blackboard.get("route_index_num") + 2  
        py_trees.blackboard.Blackboard.set("route_index_num", self.next_num)

        return py_trees.common.Status.SUCCESS 

def idling_for_fail():

    seq = py_trees.trees.composites.Sequence()
    # for fail idling
    go_to_minor_error_tree = EnqueueNextService(service_name='minor_error_tree', service_version='2.0.0')

    seq.add_children([NavigationCancel(), go_to_minor_error_tree])

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

    go_to_low_battery_tree = EnqueueNextService(
        service_name='low_battery_tree', service_version='2.0.0'
    )

    battery_seq.add_children([battery_under_15_check, battery_alarm, cancel_goal, cancel_alarm, go_to_low_battery_tree ])
    
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
    
    go_to_emergency_tree = EnqueueNextService(service_name='emergency_tree', service_version='2.0.0')

    #moving, ev, charging --> cancel_goal
    seq.add_children([emergency_button_check,cancel_goal, cancel_alarm, go_to_emergency_tree])

    return seq


# 수동충전 체크
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


    go_to_manualcharging = EnqueueNextService(
        service_name='manual_charging_tree', service_version='2.0.0'
    )

    seq.add_children([manual_contacted_check, cancel_goal, cancel_alarm, go_to_manualcharging ])

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

    cancel_alarm = PublishTopic(
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

    def request_generate_fn_ev_zone_checker_on():
        request = SetBool.Request()
        request.data = True
        return request
    def response_fn_ev_zone_checker_on(response):
        print(response.success)

    ev_zone_checker_on = ServiceCall(
        service_name='set_keepout_filter',
        service_type= SetBool,
        request_generate_fn=request_generate_fn_ev_zone_checker_on,
        response_fn= response_fn_ev_zone_checker_on, name='ev_zone_checker_on'

    )

    seq.add_children([manual_drive_button_check, nav_cancel, cancel_alarm, manual_LED_dimming_front, manual_LED_dimming_rear, ev_zone_checker_on, go_to_manual_drive  ])

    return seq


def admin_password_check_seq():
    
    seq = py_trees.composites.Sequence()

    pwcount_reset = SetBlackBoard(BB_variable = 'pw_count',
                                  BB_value = 3)        
    
    final_check_pw_correct = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_pw_correct',
                check=py_trees.common.ComparisonExpression(
                variable='pw_check',
                value=True,
                operator= operator.eq
            )
        )       

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

    wait_for_pw_req3 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name='wait_for_pw_req',
        check=py_trees.common.ComparisonExpression(
        variable='admin_pw_type',
        value='admin',
        operator= operator.eq
        )
    )        

    unset_pw_req1 = SetBlackBoard(BB_variable='admin_pw_type', BB_value='')
    unset_pw_req2 = SetBlackBoard(BB_variable='admin_pw_type', BB_value='')

    final_seq = py_trees.composites.Sequence()

    par2 = py_trees.composites.Parallel(
        name="par2",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[final_seq],
            synchronise=False
        )
    )

    seq4 =py_trees.composites.Sequence()
    seq5 =py_trees.composites.Sequence()

    pw_count_over_zero = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'pw_count_over_zero',
                check=py_trees.common.ComparisonExpression(
                variable='pw_count',
                value=0,
                operator= operator.gt
            )
        )       

    pw_count_is_zero = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'pw_count_is_zero',
                check=py_trees.common.ComparisonExpression(
                variable='pw_count',
                value=0,
                operator= operator.eq
            )
        )       
    
    par3 = py_trees.composites.Parallel(
        name="par3",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 

    seq6 =py_trees.composites.Sequence()
    seq7 =py_trees.composites.Sequence()    

    pw_correct_check = compareBBvariableforcorrect(BB_variable1 = 'admin_pw',
                                         BB_variable2 = 'admin_pw_from_ui')
    
    pw_incorrect_check = compareBBvariableforincorrect(BB_variable1 = 'admin_pw',
                                         BB_variable2 = 'admin_pw_from_ui')
    
    pw_correct_set1 = SetBlackBoard(BB_variable = 'pw_check',
                                  BB_value = True)  
    
    reduce_one_count = Reduce_1(BB_variable = 'pw_count')    
    


    
    failed_count_alarm = PublishTopic(
                            name='failed_count_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'admin_auth_check',
                                action = 'admin_auth_'+str(3-py_trees.blackboard.Blackboard.get('pw_count')),
                                action_target = '',
                                action_result = False
                                )   
                            )
    
    final_failed_alarm = PublishTopic(
                            name='final_failed_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),        
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'admin_auth_failed',
                                action = 'admin_auth_'+str(3-py_trees.blackboard.Blackboard.get('pw_count')),
                                action_target = '',
                                action_result = False
                                )   
                            )
    
    service_locked_alarm = PublishTopic(
                            name='service_locked_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),        
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'service_locked_alarm',
                                action = 'service_locked',
                                action_target = '',
                                action_result = True
                                )   
                            )
    
    #TODO have to interfaces
    admin_remote_auth = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'admin_remote_auth',
                check=py_trees.common.ComparisonExpression(
                variable='remote_unlock',
                value=True,
                operator= operator.eq
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
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'admin_auth_chekced',
                                action = 'admin_auth_'+str(3-py_trees.blackboard.Blackboard.get('pw_count')),
                                action_target = '',
                                action_result = True
                                )   
                            )

    pw_correct_set2 = SetBlackBoard(BB_variable = 'pw_check',
                                  BB_value = True)  

    unset_admin_pw1 = SetBlackBoard(BB_variable='admin_pw_from_ui', BB_value='')
    unset_admin_pw2 = SetBlackBoard(BB_variable='admin_pw_from_ui', BB_value='')

    tts_password_fail = TTSPlay(tts_name='password_fail', play=True, sequence=True)
    tts_password_lock = TTSPlay(tts_name='password_lock', play=True, sequence=True)

    # 비밀번호 틀렸을 때 - 점멸
    # led_start_on5 = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    # led_start_on6 = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    led_start_on5 = PublishTopic(
                name='led_start_on5',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
       
    led_start_on6 = PublishTopic(
                name='led_start_on6',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )     

    seq.add_children([pwcount_reset, wait_for_pw_req, par2])
    par2.add_children([seq4, seq5, final_seq])
    final_seq.add_children([final_check_pw_correct, auth_checkced_alarm, unset_admin_pw1])
    seq4.add_children([wait_for_pw_req2, pw_count_over_zero, par3])
    seq5.add_children([wait_for_pw_req3, pw_count_is_zero, final_failed_alarm, tts_password_lock, service_locked_alarm, admin_remote_auth, pw_correct_set2])
    par3.add_children([seq6, seq7])
    seq6.add_children([pw_correct_check, unset_pw_req1, pw_correct_set1])
    seq7.add_children([pw_incorrect_check,unset_admin_pw2, unset_pw_req2, reduce_one_count, failed_count_alarm,led_start_on5, led_start_on6, tts_password_fail ])

    return seq

def no_response_check(time11):

    seq = py_trees.composites.Sequence()

    time_check = NoResponseCheck(time1=time11)

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

    seq.add_children([get_start_time, par])
    par.add_children([time_check, seq1])
    seq1.add_children([wait_for_user_input, init_count, unset_user_input])

    return seq

def hall_call_progress():
        par_check_done = py_trees.composites.Parallel(
            name="par_check_done",
            policy=py_trees.common.ParallelPolicy.SuccessOnOne(
            ))

        par_hallcall = py_trees.composites.Parallel(
            name="par_hallcall",
            policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
                children=[par_check_done],
                synchronise=False
            ))
        
        seq_hallcall = py_trees.composites.Sequence()
        add_hallcall_count = Add_1(BB_variable= 'hallcall_count')
        
        req_hallcall = PublishTopic(
            name='req_hallcall',
            topic_name='rm_agent/ev_control_request',
            topic_type = EVControl,
            msg_generate_fn=lambda: EVControl(
                api_code= '',
                create_date='',
                board_zone= py_trees.blackboard.Blackboard.get("route_index_num_waypoint_poi"),
                robot_id= '',
                current_floor=py_trees.blackboard.Blackboard.get("route_index_num_floor"),
                des_floor=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor")
                )
        )

        seq_hallcall_success = py_trees.composites.Sequence()

        hallcall_alarm = PublishTopic(
            name='hallcall_alarm',
            topic_name='ktmw_bt/task_status',
            topic_type = TaskStatus,
            msg_generate_fn=lambda: TaskStatus(
                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                current_goal_id='',
                tray_id=[0],
                task_status='EV_IN',
                action='EV_call',
                action_target=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
                action_result=True
                )
        )

        check_hallcall_success = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_hallcall_success', 
                check=py_trees.common.ComparisonExpression(
                variable="call_ev_status",
                value=1,
                operator=operator.eq
            )
        )

        check_hallcall_fail = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_hallcall_fail', 
                check=py_trees.common.ComparisonExpression(
                variable="call_ev_status",
                value=1,
                operator=operator.gt ####nes
            )
        )        

        hallcall_result_unset = SetBlackBoard(BB_variable = 'call_ev_status',
                                    BB_value = 0)   
        hallcall_result_unset2 = SetBlackBoard(BB_variable = 'call_ev_status',
                                    BB_value = 0)   

        seq_hallcall_5 = py_trees.composites.Sequence()

        check_hallcall_5 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_hallcall_5', 
                check=py_trees.common.ComparisonExpression(
                variable="hallcall_count",
                value=5,
                operator=operator.eq
            )
        )

        set_critical_status = SetBlackBoard(BB_variable = 'error_status',
                                    BB_value = True)   
        set_critical_level = SetBlackBoard(BB_variable = 'error_level',
                                    BB_value = 'Critical')   
        set_critical_cause = SetBlackBoard(BB_variable = 'error_cause',
                                    BB_value = 'Hall_Call')   
            
        go_to_ciritcal_error = EnqueueNextService(
            service_name='critical_error_tree', service_version='2.0.0'
        )

        hallcall_fail_alarm = PublishTopic(
            name='hallcall_alarm',
            topic_name='ktmw_bt/task_status',
            topic_type = TaskStatus,
            msg_generate_fn=lambda: TaskStatus(
                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                current_goal_id='',
                tray_id=[0],
                task_status='EV_IN',
                action='EV_call_fail',
                action_target='EV_call_fail',
                action_result=False
                )
        )



        par_hallcall.add_children([seq_hallcall ,par_check_done])
        seq_hallcall.add_children([req_hallcall, check_hallcall_fail,hallcall_result_unset2, add_hallcall_count])
        par_check_done.add_children([seq_hallcall_5, seq_hallcall_success])
        seq_hallcall_success.add_children([check_hallcall_success, hallcall_alarm, hallcall_result_unset])
        seq_hallcall_5.add_children([check_hallcall_5, hallcall_fail_alarm, go_to_ciritcal_error])

        return par_hallcall


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

    tray_open = BoxOpen(position=1, x=1, y= py_trees.blackboard.Blackboard.get('hri_tray_id')) #if hri tray open cmd is in, open tray as requested.

    par1 = py_trees.composites.Parallel(
        name="par1",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )

    seq1 = py_trees.composites.Sequence()
    seq2 = py_trees.composites.Sequence()

    item_return_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'item_return_check',
                check=py_trees.common.ComparisonExpression(
                variable='item_return_check',
                value=True,
                operator= operator.eq
            )
        )
    
    send_back_alarm1 =  PublishTopic(
                            name='send_back_alarm1',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'task_sendback',
                                action = 'sendback',
                                action_target = 'tray'+str(py_trees.blackboard.Blackboard.get('goal_index_num_current_tray_id')),
                                action_result = True
                                )   
                            )
    
    item_return_unset1 = py_trees.behaviours.UnsetBlackboardVariable('item_return_check')

    tray_close1 = BoxClose(position=1, x=1, y= py_trees.blackboard.Blackboard.get('hri_tray_id'))

    hri_tray_num_unset1 = py_trees.behaviours.UnsetBlackboardVariable('hri_tray_id')

    tray_manual_set = GetandSetTrayBlackBoard(BB_variable='Tray_manual_stuff_status')

    tray_object_sensing_empty_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'tray_object_sensing_empty_check',
        check=py_trees.common.ComparisonExpression(
        variable= "Tray_manual_stuff_status",
        value=False,
        operator= operator.eq
        )
    )    

    par2 = py_trees.composites.Parallel(
        name="par2",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )

    tray_close2 = BoxClose(position=1, x=1, y= py_trees.blackboard.Blackboard.get('hri_tray_id'))

    hri_tray_num_unset2 = py_trees.behaviours.UnsetBlackboardVariable('hri_tray_id')

    seq3 = py_trees.composites.Sequence()

    hri_finished_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'hri_finished_check',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Tray_open',
                operator= operator.eq
            )
        )
    
    
    item_return_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'item_return_check',
                check=py_trees.common.ComparisonExpression(
                variable='item_return_check',
                value=True,
                operator= operator.eq
            )
        )

    send_back_alarm2 =  PublishTopic(
                            name='send_back_alarm1',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'task_sendback',
                                action = 'sendback',
                                action_target = 'tray'+str(py_trees.blackboard.Blackboard.get('goal_index_num_current_tray_id')),
                                action_result = True
                                )   
                            )
    
    item_return_unset2 = py_trees.behaviours.UnsetBlackboardVariable('item_return_check')


    seq.add_children([wait_hri_tray_open_cmd, tray_open, par1])
    par1.add_children([seq1, seq2])
    seq1.add_children([item_return_check1, send_back_alarm1, item_return_unset1, tray_close1, hri_tray_num_unset1])
    seq2.add_children([tray_manual_set, tray_object_sensing_empty_check, par2, tray_close2, hri_tray_num_unset2 ])
    par2.add_children([seq3, hri_finished_check, no_response_check(time11=10)]) #TODO
    seq3.add_children([item_return_check2, send_back_alarm2, item_return_unset2])

    return seq

def finish_and_go_to_idle_seq():

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
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'task_finished',
                                action = 'task_finished',
                                action_target = 'tray'+str(py_trees.blackboard.Blackboard.get('goal_index_num_current_tray_id')),
                                action_result = True
                                )   
                            )
    
    seq.add_children([hri_finished_check, task_finished_alarm])

    return seq

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
    
    cancel_goal = NavigationCancel()
    seq_go_to_minor_error_tree.add_children([ par_major_error_check_all, cancel_goal,go_to_minor_error_tree])
    par_major_error_check_all.add_children([major_error_level_check, major_error_code_check])
    
    return seq_go_to_minor_error_tree

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
    cancel_goal = NavigationCancel()
    seq_critical_error.add_children([critical_error_check,cancel_goal, go_to_critical_error_tree])
    
    return seq_critical_error


# main tree
def create_root():

    #1. (tree-PAR) main root
    root_ele = py_trees.composites.Parallel(
        name="Elevator_Tree",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    ##1-1. (tree-PAR) Something 2 BB

    parallel_get_msg = py_trees.composites.Parallel(
        name="parallel_get_msg",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

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
        name='button_info_to_BB')       

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

    #EV 호출 noti
    def on_msg_fn_ev_call(msg):
        logging.debug("ev call")
        logging.debug(msg)
        py_trees.blackboard.Blackboard.set('call_create_date', msg.create_date)
        py_trees.blackboard.Blackboard.set('call_board_zone', msg.board_zone)
        py_trees.blackboard.Blackboard.set('call_board_point', msg.board_point)
        py_trees.blackboard.Blackboard.set('call_current_floor', msg.current_floor)
        py_trees.blackboard.Blackboard.set('call_des_floor', msg.des_floor)  #string
        py_trees.blackboard.Blackboard.set('call_result', msg.result)
        py_trees.blackboard.Blackboard.set('call_ev_status', msg.ev_status)

    EVcall_to_BB = SubscribeTopic(
        topic_name='rm_agent/ev_call_result',
        topic_type=EVControlResponse,
        on_msg_fn=on_msg_fn_ev_call,
        name='EVF_nav_status_to_BB'
    )

    #EV 도착 noti
    def on_msg_fn_ev_arrival_noti(msg):
        logging.debug("ev arrival noti")
        logging.debug(msg)
        #py_trees.blackboard.Blackboard.set('dep_create_date', msg.create_date)
        py_trees.blackboard.Blackboard.set('dep_board_zone', msg.board_zone)
        py_trees.blackboard.Blackboard.set('dep_board_point', msg.board_point)
        py_trees.blackboard.Blackboard.set('dep_current_floor', msg.current_floor)
        # py_trees.blackboard.Blackboard.set('dep_des_floor', msg.des_floor)
        #py_trees.blackboard.Blackboard.set('dep_get_off_zone', msg.get_off_zone)
        #py_trees.blackboard.Blackboard.set('dep_get_off_point', msg.get_off_point)

    dep_arv_noti_to_BB = SubscribeTopic(
        topic_name='rm_agent/ev_dep_arv',
        topic_type=EVControlNoti,
        on_msg_fn=on_msg_fn_ev_arrival_noti,
        name='dep_arv_noti_to_BB'
    )

    #EV 목적층 destination 도착 noti
    def on_msg_fn_ev_des_noti(msg):
        logging.debug("ev des noti")
        logging.debug(msg)
        #py_trees.blackboard.Blackboard.set('des_create_date', msg.create_date)
        #py_trees.blackboard.Blackboard.set('des_board_zone', msg.board_zone)
        #py_trees.blackboard.Blackboard.set('des_board_point', msg.board_point)
        py_trees.blackboard.Blackboard.set('des_current_floor', msg.current_floor)
        #py_trees.blackboard.Blackboard.set('des_des_floor', msg.des_floor)
        py_trees.blackboard.Blackboard.set('des_get_off_zone', msg.get_off_zone)
        temp_get_off_point = msg.get_off_point
        temp_get_off_point = temp_get_off_point.replace("EVR","EVF")
        py_trees.blackboard.Blackboard.set('des_get_off_point', msg.get_off_point)
        py_trees.blackboard.Blackboard.set('des_temp_get_off', temp_get_off_point)

    des_arv_noti_to_BB = SubscribeTopic(
        topic_name='rm_agent/ev_des_arv',
        topic_type=EVControlNoti,
        on_msg_fn=on_msg_fn_ev_des_noti,
        name='des_arv_noti_to_BB'
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

    ##1-2 Stop 정지
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

    resume_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'resume_check',
            check=py_trees.common.ComparisonExpression(
            variable="halt_status",
            value='resume',
            operator= operator.eq
        )
    )

    #pause_nav_false = NavigationPause(pause=False)
    
    def request_generate_fn_pause():
        req = SetBool.Request()
        req.data = False
        return req
    
    def response_fn_pause(response):
        print(response.success)

    pause_nav_false = ServiceCall(
        service_name='nav/pause',
        service_type=SetBool,
        request_generate_fn=request_generate_fn_pause,
        response_fn=response_fn_pause,
        name='pause_nav_false'
    )

    unset_halt_status1 = py_trees.behaviours.UnsetBlackboardVariable('halt_status')
    unset_halt_status2 = py_trees.behaviours.UnsetBlackboardVariable('halt_status')

    ##1-3 Halt 취소
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

    seq_resume_check = py_trees.composites.Sequence()

    admin_reset_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'admin_reset_check',
            check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value='Admin_reset',
            operator= operator.eq
        )
    )

    #pause_nav_false2 = NavigationPause(pause=False)

    pause_nav_false2 = NavigationStart(req_generate_fn=lambda:
        {'target_label': py_trees.blackboard.Blackboard.get("abcd"),
         'goal_label': '',
         'mode': 'ev_in',
         'req_id': '',
         'speed_scale': py_trees.blackboard.Blackboard.get('moving_speed')
         })

    par_cancel_type_check = py_trees.composites.Parallel(
        name="par_cancel_type_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq_resume_check],
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

    go_to_item_change_tree = EnqueueNextService(
        service_name='', service_version=''
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

    # blocked seq
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
            current_goal_id='',
            tray_id=[0],
            task_status='moving',
            action='blocked',
            action_target='obstacle',
            action_result=True
            )
        )


    blocked_pause_15 = py_trees.timers.Timer("blocked_pause_15", duration=15.0)

    
    ##1-4 Main
    main_seq = py_trees.composites.Sequence(
        name='main_seq'
    )

    Flag_Count_set = Flag_Count_Set()


    
    # EV 앞 이동 완료 알림 전송
    evf_alarm = PublishTopic(
        name='evf_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_IN',
            action='EVF_arv',
            action_target=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
            action_result=True
            )
    )

    # EV 도착 체크
    ev_dep_arv_check = EV_floor_check(BB_variable1="dep_current_floor",BB_variable2= "call_current_floor")



    evi_set = EVI_set()
    
    #EV 탑승 시작 알림
    EVI_boarding_req = PublishTopic(
        name='EVI_boarding_req',
        topic_name='rm_agent/ev_boarding_status_request',
        topic_type = EVBoardStatus,
        msg_generate_fn=lambda: EVBoardStatus(
            api_code="BOARD_STATUS",
            create_date="", # TODO
            request_id="",
            board_zone=py_trees.blackboard.Blackboard.get('call_board_zone'),
            board_point=py_trees.blackboard.Blackboard.get('call_board_point'),
            robot_id="",
            current_floor=py_trees.blackboard.Blackboard.get('call_current_floor'),
            board_type=0, # 0: board 1: getoff
            board_status="START"
            )
    )

    BGM_moving_EVI_on= BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=True, repeat = True)
    BGM_moving_evi_off= BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=False, repeat = False)

    # EV Boarding success/fail check parallel
    seq_EVI_moving_success_check = py_trees.composites.Sequence()


    EVI_boarding_alarm = PublishTopic(
        name='EVI_boarding_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),  
            current_goal_id='',
            tray_id=[0],
            task_status='EV_IN',
            action='Boarding',
            action_target=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
            action_result=True
            )
    )

    evi_boarding_success_alarm = PublishTopic(
        name='evi_boarding_success_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),  
            current_goal_id='',
            tray_id=[0],
            task_status='EV_IN',
            action='Boarding_Success',
            action_target=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
            action_result=True
            )
    )
    
    # 탑승 완료
    EVI_boarding_complete = PublishTopic(
        name='EVI_boarding_complete',
        topic_name='rm_agent/ev_boarding_status_request',
        topic_type = EVBoardStatus,
        msg_generate_fn=lambda: EVBoardStatus(
            api_code="BOARD_STATUS",
            create_date="", ### TODO
            request_id="",
            board_zone=py_trees.blackboard.Blackboard.get('call_board_zone'),
            board_point=py_trees.blackboard.Blackboard.get('call_board_point'),
            robot_id="",
            current_floor=py_trees.blackboard.Blackboard.get('call_current_floor'),
            board_type=0, # 0: board 1: getoff
            board_status="complete"
            )
    )


    # 목적층 map 선택 --> EVR

    next_evi_set = next_EVI_set()

    def request_generate_fn_load_des_map():
        # Init Point "1층-융기원5cm-20230531102836_EFI-ev6" -> "2층-융기원5cm-20230531130807_EFI-ev6"
        #temp = py_trees.blackboard.Blackboard.get("EVI_board_point").split("_")[1]   ->   EFI-ev6
        req                   = NavMapLoad.Request()
        req.map_name          = py_trees.blackboard.Blackboard.get("route_index_num_+1_map_name")
        req.reset             = False #py_trees.blackboard.Blackboard.get("reset") #TODO
        req.localization_only = True #py_trees.blackboard.Blackboard.get("localization_only") #TODO
        req.resolution        = 0.0 #py_trees.blackboard.Blackboard.get("resolution") #TODO
        req.label             = py_trees.blackboard.Blackboard.get("next_EVI_board_point") 
        return req

    def response_fn_load_des_map(response):
        py_trees.blackboard.Blackboard.set('load_map_check', response.result) 

    load_des_map_set = ServiceCall(service_type=NavMapLoad, 
                          service_name='nav/map_load', 
                          request_generate_fn= request_generate_fn_load_des_map,
                          response_fn= response_fn_load_des_map , 
                          name='load_des_map_set')



    # 도착층 도착? ev_des_arv
    move_evr_seq = py_trees.composites.Sequence(
        name='move_evr_seq'
    )
    
    BGM_moving_evi_On2 =  BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=True, repeat = True)
    BGM_moving_evi_On3 = BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=True, repeat = True)
    BGM_moving_evi_off2= BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=False, repeat = False)
    BGM_moving_evi_off3= BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=False, repeat = False)

    EVI_alarm3 = PublishTopic(
        name='EVW_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_Fail',
            action='EVI_arv',
            action_target='EVI',
            action_result=True
            )
    )

    EVI_alarm3_fail = PublishTopic(
        name='EVI_alarm3_fail',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_Fail',
            action='EVI_arv',
            action_target='EVI',
            action_result=False
            )
    )

    admin_waiting2 = Idling(name='Idling')

    go_to_minor_error_tree1 = EnqueueNextService(service_name='minor_error_tree', service_version='2.0.0')
    
    ev_des_arv_check = EV_floor_check(BB_variable1="des_current_floor",BB_variable2= "call_des_floor")

    # 도착층 EVR 앞 이동 (하차 명령)
    

    BGM_moving_evr = BGMPlay(bgm_name= BGMPlay.BGM_MOVING, play=True, repeat = True)
    
    
    seq_EVR_moving_success_check = py_trees.composites.Sequence()

    # EV Getoff success/fail check parallel
    

    evr_boarding_alarm = PublishTopic(
        name='evr_boarding_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_OUT',
            action='EVR_Success',
            action_target=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
            action_result=True
            )
    )

   

    route_index_num_add_2 = Route_Index_Add_2()

    go_to_moving = EnqueueNextService(
        service_name='moving_tree', service_version=''
    )

    tts_obstacle = TTSPlay(tts_name='obstacle', play=True, sequence=True)
    tts_obstacle_robot = TTSPlay(tts_name='obstacle_robot', play=True, sequence=True)
    tts_lineup_wating = TTSPlay(tts_name='lineup_wating', play=True, sequence=True)

    TTS_ev_in = TTSPlay(tts_name="elevator_in", play=True, sequence=True)
    TTS_ev_in_fail = TTSPlay(tts_name="elevator_in_fail", play=True, sequence=True)
    TTS_ev_out = TTSPlay(tts_name="elevator_out", play=True, sequence=True)
    TTS_ev_out_fail = TTSPlay(tts_name="elevator_out_fail", play=True, sequence=True)


    

    seq_fleet_lineup = py_trees.composites.Sequence()

    fleet_lineup_check = FleetLineupStatus()    

    fleet_lineup_alarm = PublishTopic(
        name='fleet_lineup_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
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
            current_goal_id='',
            tray_id=[0],
            task_status='moving',
            action='fleet_lineup',
            action_target='fleet_lineup',
            action_result=False
            )
        )

    #줄서기 TTS
    fleet_finished_check = MovingStatus()

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
            current_goal_id='',
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
            current_goal_id='',
            tray_id=[0],
            task_status='moving',
            action='recovery',
            action_target='recovery',
            action_result=False
            )
        )

    #양보 TTS
    recovery_finished_check = MovingStatus()

    BB_start = BB_init()


    par_arv_evi = py_trees.composites.Parallel(
        name="par_arv_evi",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    arv_EVI_state_success = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'arv_EVI_state_success',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    arv_EVI_state_failed = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'arv_EVI_state_failed',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='failed',
            operator=operator.eq
        )
    )

    arv_EVI_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'arv_EVI_mode',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='ev_in',
            operator=operator.eq
        )
    )


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
    
    led_start_on_moving1 = PublishTopic(
                name='led_start_on_moving1',
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

    led_start_on_moving2 = PublishTopic(
                name='led_start_on_moving2',
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
       

    # LED_charging_f = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    # LED_charging_r = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    LED_charging_f = PublishTopic(
                name='LED_charging_f',
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

    LED_charging_r = PublishTopic(
                name='LED_charging_r',
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
       

    root_sel = py_trees.composites.Selector('ev_tree')
    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
    )

    seq_normal = py_trees.composites.Sequence()

    seq_evf = py_trees.composites.Sequence()

    par_evf_result = py_trees.composites.Parallel(
            name="par_evf_result",
            policy=py_trees.common.ParallelPolicy.SuccessOnOne(
            ))
    
    par_evf_success = py_trees.composites.Parallel(
            name="par_evf_success",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
            ))
    
    seq_evf_fail = py_trees.composites.Sequence()

    check_evf_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evf_mode', 
                check=py_trees.common.ComparisonExpression(
                variable="mode",
                value="normal",
                operator=operator.eq
            )
        )
    
    check_evf_status = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evf_status', 
                check=py_trees.common.ComparisonExpression(
                variable="nav_status",
                value="finished",
                operator=operator.eq
            )
        )
    
    check_evf_mode2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evf_mode2', 
                check=py_trees.common.ComparisonExpression(
                variable="mode",
                value="normal",
                operator=operator.eq
            )
        )
    
    check_evf_status2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evf_status2', 
                check=py_trees.common.ComparisonExpression(
                variable="nav_status",
                value="failed",
                operator=operator.eq
            )
        )
    
    par_evf_fail = py_trees.composites.Parallel(
            name="par_evf_result",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
            ))
    

    alarm_evf_fail = PublishTopic(
        name='EVI_boarding_fail_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),                    
            current_goal_id='',
            tray_id=[0],
            task_status='EVF_moving',
            action='Moving_Fail',
            action_target=py_trees.blackboard.Blackboard.get("route_index_num_floor"),
            action_result=False
            )
    )


    def request_generate_fn_movecall_EVW():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("route_index_num_waypoint_poi")
        req.goal_label = ''
        req.mode = 'normal'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_movecall_EVW(response):
        print(response.result)

    move_evw = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_movecall_EVW,
        response_fn=response_fn_movecall_EVW,
        name='movecall_EVW'
    )

    check_board_point = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_board_point', 
            check=py_trees.common.ComparisonExpression(
            variable="call_board_point",
            value="no",
            operator=operator.ne
        )
    )

    def request_generate_fn_movecall_EVF():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("call_board_point")
        req.goal_label = ''
        req.mode = 'normal'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_movecall_EVF(response):
        print(response.result)

    move_evf = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_movecall_EVF,
        response_fn=response_fn_movecall_EVF,
        name='move_evf'
    )

    seq_evi = py_trees.composites.Sequence()
    seq_evi_fail = py_trees.composites.Sequence()

    def request_generate_fn_movecall_EVI():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("EVI_board_point")
        req.goal_label = ''
        req.mode = 'ev_in'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_movecall_EVI(response):
        print(response.result)
    
    move_evi = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_movecall_EVI,
        response_fn=response_fn_movecall_EVI,
        name='move_evi'
    )

    par_evi_result = py_trees.composites.Parallel(
        name="par_evi_result",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        ))
    
    par_evi_success = py_trees.composites.Parallel(
        name="par_evi_success",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
        synchronise=False
        ))
    
    check_evi_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evi_mode', 
            check=py_trees.common.ComparisonExpression(
            variable="mode",
            value="ev_in",
            operator=operator.eq
        )
    )

    check_evi_status = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evi_status', 
                check=py_trees.common.ComparisonExpression(
                variable="nav_status",
                value="finished",
                operator=operator.eq
            )
        )

    
    check_evi_mode2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evi_mode2', 
                check=py_trees.common.ComparisonExpression(
                variable="mode",
                value="ev_in",
                operator=operator.eq
            )
        )
    
    check_evi_status2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evi_status2', 
                check=py_trees.common.ComparisonExpression(
                variable="nav_status",
                value="failed",
                operator=operator.eq
            )
        )
    
    par_evi_fail = py_trees.composites.Parallel(
            name="par_evi_fail",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
            ))
    

    alarm_evi_fail = PublishTopic(
        name='alarm_evi_fail',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),                    
            current_goal_id='',
            tray_id=[0],
            task_status='EV_IN',
            action='Boarding_Fail',
            action_target=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
            action_result=False
            )
    )



    def request_generate_fn_movecall_EVF2():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("route_index_num_waypoint_poi")
        req.goal_label = ''
        req.mode = 'normal'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_movecall_EVF2(response):
        print(response.result)

    move_evf2 = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_movecall_EVF2,
        response_fn=response_fn_movecall_EVF2,
        name='movecall_EVF'
    )


    seq_evr = py_trees.composites.Sequence()
    seq_evr_fail = py_trees.composites.Sequence()

    check_board_point2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_board_point', 
            check=py_trees.common.ComparisonExpression(
            variable="des_get_off_point",
            value="no",
            operator=operator.ne
        )
    )

    def request_generate_fn_movecall_EVR():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("des_get_off_point")
        req.goal_label = ''
        req.mode = 'ev_out'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_movecall_EVR(response):
        print(response.result)

    move_evr = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_movecall_EVR,
        response_fn=response_fn_movecall_EVR,
        name='movecall_EVR'
    )

    #EV 하차 시작 알림
    evr_getoff_req = PublishTopic(
        name='evr_getoff_req',
        topic_name='rm_agent/ev_boarding_status_request',
        topic_type = EVBoardStatus,
        msg_generate_fn=lambda: EVBoardStatus(
            api_code="BOARD_STATUS",
            create_date="", # TODO
            request_id="",
            get_off_zone=py_trees.blackboard.Blackboard.get("des_get_off_zone"),
            get_off_point=py_trees.blackboard.Blackboard.get("des_temp_get_off"),
            robot_id="",
            current_floor=py_trees.blackboard.Blackboard.get("des_current_floor"),
            board_type=1, # 0: board 1: getoff
            board_status="START"
            )
    )
    # EV 앞 이동 알림 전송
    evr_alarm =  PublishTopic(
                            name='EVR_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, 
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'EV_OUT',
                                action='EVR_Arriving',
                                action_target = py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
                                action_result = True
                                )   
                            )

    par_evr_result = py_trees.composites.Parallel(
        name="par_evr_result",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        ))
    
    par_evr_success = py_trees.composites.Parallel(
        name="par_evr_success",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
        synchronise=False
        ))
    
    check_evr_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evr_mode', 
            check=py_trees.common.ComparisonExpression(
            variable="mode",
            value="ev_out",
            operator=operator.eq
        )
    )

    check_evr_status = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evr_status', 
                check=py_trees.common.ComparisonExpression(
                variable="nav_status",
                value="finished",
                operator=operator.eq
            )
        )

    
    check_evr_mode2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evr_mode2', 
                check=py_trees.common.ComparisonExpression(
                variable="mode",
                value="ev_out",
                operator=operator.eq
            )
        )
    
    check_evr_status2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_evr_status2', 
                check=py_trees.common.ComparisonExpression(
                variable="nav_status",
                value="failed",
                operator=operator.eq
            )
        )
    
    par_evr_fail = py_trees.composites.Parallel(
            name="par_evr_fail",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
            ))
    

    alarm_evr_fail = PublishTopic(
        name='EVR_boarding_fail_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_OUT',
            action='EVR_Fail',
            action_target=py_trees.blackboard.Blackboard.get("route_index_num_+1_floor"),
            action_result=False
            )
    ) 


    def request_generate_fn_movecall_EVI2():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("next_EVI_board_point")
        req.goal_label = ''
        req.mode = 'ev_in'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_movecall_EVI2(response):
        print(response.result)

    move_evi2 = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_movecall_EVI2,
        response_fn=response_fn_movecall_EVI2,
        name='move_evi2'
    )

    evr_boarding_complete = PublishTopic(
        name='evr_boarding_complete',
        topic_name='rm_agent/ev_boarding_status_request',
        topic_type = EVBoardStatus,
        msg_generate_fn=lambda: EVBoardStatus(
            api_code="BOARD_STATUS",
            create_date="", # TODO
            request_id="",
            get_off_zone=py_trees.blackboard.Blackboard.get("des_get_off_zone"),
            get_off_point=py_trees.blackboard.Blackboard.get("des_temp_get_off"),
            robot_id="",
            current_floor=py_trees.blackboard.Blackboard.get("des_current_floor"),
            board_type=1, # 0: board 1: getoff
            board_status="complete"
            )
    )

    def request_generate_fn_movecall_EVW2():
        req = SetNavGoal.Request()
        req.target_label= py_trees.blackboard.Blackboard.get("route_index_num_waypoint_poi")
        req.goal_label = ''
        req.mode = 'normal'
        req.req_id.command = 0
        req.speed_scale = py_trees.blackboard.Blackboard.get('moving_speed')
        return req
    
    def response_fn_movecall_EVW2(response):
        print(response.result)

    move_evw2 = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_movecall_EVW2,
        response_fn=response_fn_movecall_EVW2,
        name='movecall_EVW'
    )



    seq_evf_success = py_trees.composites.Sequence()
    seq_evi_success = py_trees.composites.Sequence()
    seq_evr_success = py_trees.composites.Sequence()

    go_to_critical_error_tree = EnqueueNextService(
        service_name='critical_error_tree', service_version='2.0.0'
    )

    seq_error_flag = py_trees.composites.Sequence()

    check_error_flag_on = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'check_error_flag_on',
                check=py_trees.common.ComparisonExpression(
                variable='error_flag',
                value=True,
                operator= operator.eq
            )
        )

    par_evw_arrived_check = py_trees.composites.Parallel(
        name="par_evw_arrived_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
        ))

    par_evw_arrived_check2 = py_trees.composites.Parallel(
        name="par_evw_arrived_check2",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
        ))
    
    check_evw_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evw_mode', 
            check=py_trees.common.ComparisonExpression(
            variable="mode",
            value="normal",
            operator=operator.eq
        )
    )

    par_check_evw_status = py_trees.composites.Parallel(
        name="par_check_evw_status",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 

    par_check_evw_status2 = py_trees.composites.Parallel(
        name="par_check_evw_status2",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 

    check_evw_status_finished = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evw_status_finished', 
            check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value="finished",
            operator=operator.eq
        )
    )

    check_evw_status_failed = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evw_status_failed', 
            check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value="failed",
            operator=operator.eq
        )
    )

    check_evw_mode2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evw_mode2', 
            check=py_trees.common.ComparisonExpression(
            variable="mode",
            value="normal",
            operator=operator.eq
        )
    )

    check_evw_status_finished2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evw_status_finished2', 
            check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value="finished",
            operator=operator.eq
        )
    )

    check_evw_status_failed2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_evw_status_failed2', 
            check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value="failed",
            operator=operator.eq
        )
    )

    error_flag_Set = SetBlackBoard(BB_variable='error_flag', BB_value=True)
    error_flag_Set2 = SetBlackBoard(BB_variable='error_flag', BB_value=True)

    idling_error = Idling()
    idling_error2 = Idling()

    go_to_minor_error_tree2 = EnqueueNextService(service_name='minor_error_tree', service_version='2.0.0')
    go_to_minor_error_tree3 = EnqueueNextService(service_name='minor_error_tree', service_version='2.0.0')

    alarm_EVW_fail = PublishTopic(
        name='alarm_EVW_fail',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_Fail',
            action='EVW_arv',
            action_target='EVW',
            action_result=True
            )
    )
    alarm_EVW_fail_fail = PublishTopic(
        name='alarm_EVW_fail_fail',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_Fail',
            action='EVW_arv',
            action_target='EVW',
            action_result=False
            )
    ) 

    alarm_EVW_fail2 = PublishTopic(
        name='alarm_EVW_fail2',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_Fail',
            action='EVW_arv',
            action_target='EVW',
            action_result=True
            )
    ) 

    alarm_EVW_fail2_fail = PublishTopic(
        name='alarm_EVW_fail2_fail',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
            service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
            task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
            goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
            current_goal_id='',
            tray_id=[0],
            task_status='EV_Fail',
            action='EVW_arv',
            action_target='EVW',
            action_result=False
            )
    ) 

    seq_check_evw_status_finished = py_trees.composites.Sequence()
    seq_check_evw_status_failed = py_trees.composites.Sequence()
    go_to_critical_error_tree2 = EnqueueNextService(
        service_name='critical_error_tree', service_version='2.0.0'
    )

    seq_check_evw_status_finished2 = py_trees.composites.Sequence()
    seq_check_evw_status_failed2 = py_trees.composites.Sequence()
    go_to_critical_error_tree3 = EnqueueNextService(
        service_name='critical_error_tree', service_version='2.0.0'
    )

    par_return_EVI_status = py_trees.composites.Parallel(
        name="par_return_EVI_status",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    ) 

    seq_arv_EVI_success = py_trees.composites.Sequence()
    seq_arv_EVI_failed = py_trees.composites.Sequence()
    go_to_critical_error_tree4 = EnqueueNextService(
        service_name='critical_error_tree', service_version='2.0.0'
    )

    unset_nav_status1 = SetBlackBoard(BB_variable='nav_status', BB_value='')
    unset_nav_status2 = SetBlackBoard(BB_variable='nav_status', BB_value='')
    unset_nav_status3 = SetBlackBoard(BB_variable='nav_status', BB_value='')

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
            name='simple_Alarm',
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
    multirobot_available_t_1 = PublishTopic(
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
                                    action_result = True
                                    )   
                                ) 
    multirobot_available_f_1 = PublishTopic(
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
    
    root_sel.add_children([root_ele, go_to_ciritcal_error2])
    root_ele.add_children([parallel_get_msg, check_critical_error(), go_to_minor_error_tree(), minor_error_alarm(), check_manual_drive(), check_manual_charge(), emergency_button_check(), battery_under_15(), seq_error_flag, seq_collission, seq_blocked, seq_fleet_lineup, seq_recovery, main_seq])

    parallel_get_msg.add_children([emergency_button_info_to_BB, error_set_to_BB, button_status_to_BB, battery_state_to_BB, charging_state_to_BB,user_input_msgs_to_BB,EVcall_to_BB, dep_arv_noti_to_BB, des_arv_noti_to_BB,nav_status_to_BB,halt_Status_to_BB, halt_result_to_BB, beep_trigger_to_BB])

    seq_collission.add_children([collission_check, alarmplay_collision, collision_alarm, collision_key_reset])
    seq_blocked.add_children([blocked_check, blocked_alarm, tts_obstacle, blocked_pause_15])
    seq_fleet_lineup.add_children([fleet_lineup_check, tts_lineup_wating, led_start_on_lineup_front, led_start_on_lineup_rear, fleet_lineup_alarm, fleet_finished_check, led_start_on_moving_again1, led_start_on_moving_again2, fleet_lineup_alarm2])
    seq_recovery.add_children([recovery_check, tts_obstacle_robot, led_start_on_recovery_front, led_start_on_recovery_rear, recovery_alarm, recovery_finished_check, led_start_on_moving_again3, led_start_on_moving_again4, recovery_alarm2])


    seq_error_flag.add_children([check_error_flag_on, go_to_critical_error_tree])
    main_seq.add_children([BB_start, led_start_on_moving1, led_start_on_moving2, Flag_Count_set, seq_normal, route_index_num_add_2, go_to_moving])
    
    seq_normal.add_children([hall_call_progress(), seq_evf, seq_evi, seq_evr])

    seq_evf.add_children([check_board_point, move_evf,multirobot_available_t_1, par_evf_result])
    par_evf_result.add_children([seq_evf_success,seq_evf_fail])
    seq_evf_success.add_children([par_evf_success,multirobot_available_f_1, evf_alarm])
    par_evf_success.add_children([check_evf_mode, check_evf_status])
    seq_evf_fail.add_children([par_evf_fail, alarm_evf_fail, unset_nav_status1, NavigationCancel(), go_to_minor_error_tree3])
    par_evf_fail.add_children([check_evf_mode2, check_evf_status2])

    # seq_evf_fail.add_children([par_evf_fail, alarm_evf_fail, unset_nav_status1, move_evw, par_evw_arrived_check, alarm_EVW_fail, go_to_minor_error_tree3])
    # par_evf_fail.add_children([check_evf_mode2, check_evf_status2])
    # par_evw_arrived_check.add_children([check_evw_mode, par_check_evw_status])
    # par_check_evw_status.add_children([seq_check_evw_status_finished, seq_check_evw_status_failed])
    # seq_check_evw_status_finished.add_children([check_evw_status_finished])
    # seq_check_evw_status_failed.add_children([check_evw_status_failed, alarm_EVW_fail_fail, idling_for_fail()])

    seq_evi.add_children([ev_dep_arv_check, evi_set, move_evi, EVI_boarding_alarm, TTS_ev_in, BGM_moving_EVI_on, EVI_boarding_req, par_evi_result, EVI_boarding_complete,
                          LED_charging_f, LED_charging_r, next_evi_set, load_des_map_set])
    par_evi_result.add_children([seq_evi_success, seq_evi_fail])
    seq_evi_success.add_children([par_evi_success, evi_boarding_success_alarm,BGM_moving_evi_off])
    par_evi_success.add_children([check_evi_mode, check_evi_status])
    seq_evi_fail.add_children([par_evi_fail, unset_nav_status2, TTS_ev_in_fail, alarm_evi_fail, NavigationCancel(), go_to_minor_error_tree2])
    par_evi_fail.add_children([check_evi_mode2, check_evi_status2])

    # seq_evi_fail.add_children([par_evi_fail, TTS_ev_in_fail, alarm_evi_fail, unset_nav_status2, move_evw2, BGM_moving_evi_On2, par_evw_arrived_check2, alarm_EVW_fail2, BGM_moving_evi_off2, go_to_minor_error_tree2])
    # par_evi_fail.add_children([check_evi_mode2, check_evi_status2])
    # par_evw_arrived_check2.add_children([check_evw_mode2, par_check_evw_status2])
    # par_check_evw_status2.add_children([seq_check_evw_status_finished2, seq_check_evw_status_failed2])
    # seq_check_evw_status_finished2.add_children([check_evw_status_finished2])
    # seq_check_evw_status_failed2.add_children([check_evw_status_failed2, alarm_EVW_fail2_fail, idling_for_fail()])

    seq_evr.add_children([ev_des_arv_check, check_board_point2, move_evr, TTS_ev_out, BGM_moving_evr, evr_getoff_req,evr_alarm, par_evr_result, evr_boarding_complete])
    par_evr_result.add_children([seq_evr_success, seq_evr_fail])
    seq_evr_success.add_children([par_evr_success, evr_boarding_alarm ])
    par_evr_success.add_children([check_evr_mode, check_evr_status])
    seq_evr_fail.add_children([par_evr_fail, unset_nav_status3, TTS_ev_out_fail, alarm_evr_fail,NavigationCancel(), go_to_minor_error_tree1])
    par_evr_fail.add_children([check_evr_mode2, check_evr_status2])

    # seq_evr_fail.add_children([par_evr_fail, unset_nav_status3, move_evi2, TTS_ev_out_fail, alarm_evr_fail, BGM_moving_evi_On3, par_arv_evi, BGM_moving_evi_off3, EVI_alarm3, go_to_minor_error_tree1])
    # par_evr_fail.add_children([check_evr_mode2, check_evr_status2])
    # par_arv_evi.add_children([arv_EVI_mode, par_return_EVI_status])
    # par_return_EVI_status.add_children([seq_arv_EVI_success, seq_arv_EVI_failed])
    # seq_arv_EVI_success.add_children([arv_EVI_state_success])
    # seq_arv_EVI_failed.add_children([arv_EVI_state_failed, EVI_alarm3_fail, idling_for_fail()])




    
    return root_sel
