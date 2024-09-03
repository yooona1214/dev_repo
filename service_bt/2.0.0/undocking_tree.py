'''
KT Robot BehaviorTree version 2.0.1

Copyright ⓒ 2023 kt corp. All rights reserved.

This is a proprietary software of kt corp, and you may not use this file except in
compliance with license agreement with kt corp. Any redistribution or use of this
software, with or without modification shall be strictly prohibited without prior written
approval of kt corp, and the copyright notice above does not evidence any actual or
intended publication of such software.
'''

import operator
import py_trees



from ktmw_bt_interfaces.msg import TaskStatus,HaltStatus, StartService, AuthRequest
from kt_msgs.msg import BoxStates, BoolCmdArray, Password, LEDState, Location, LEDEffect

from ktmw_srvmgr_lib.common import  SetBlackBoard,  PublishTopic, EnqueueNextService, Idling, SubscribeTopic, ServiceCall, compareBBvariableforcorrect, compareBBvariableforincorrect,TTSPlay, BGMPlay 
from ktmw_srvmgr_lib.hardware import BoxClose, LEDControl

from config_manager_msgs.srv import GetPoiRoute
from std_msgs.msg import UInt8, Int8MultiArray


from kt_nav_msgs.msg import NavStatus

from ktmw_srvmgr_lib.navigation import  NavigationCancel, NavigationPause
from kt_nav_msgs.srv import SetNavGoal

import sensor_msgs.msg as sensor_msgs

from std_srvs.srv import SetBool
from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm
from slam_manager_msgs.srv import NavMapLoad



#RobotConfSrv

# ** Required **
SERVICE_NAME = 'undocking-tree'
# ** Required **
SERVICE_VERSION = '0.1.0'


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


class docking_error_0(py_trees.behaviour.Behaviour):
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
        self.bb1 = py_trees.blackboard.Blackboard.get('docking_error_5')
        self.bb2 = py_trees.blackboard.Blackboard.get('docking_error_6')
        self.bb3 = py_trees.blackboard.Blackboard.get('docking_error_7')
        self.bb4 = py_trees.blackboard.Blackboard.get('docking_error_12')
        self.bb5 = py_trees.blackboard.Blackboard.get('docking_error_14')
        self.bb6 = py_trees.blackboard.Blackboard.get('docking_error_15')
        self.bb7 = py_trees.blackboard.Blackboard.get('docking_error_8')
        self.bb8 = py_trees.blackboard.Blackboard.get('docking_error_9')
        self.bb9 = py_trees.blackboard.Blackboard.get('docking_error_10')
        self.bb10 = py_trees.blackboard.Blackboard.get('docking_error_11')
        self.bb11 = py_trees.blackboard.Blackboard.get('docking_error_16')
        self.bb12 = py_trees.blackboard.Blackboard.get('docking_error_17')
        self.bb13 = py_trees.blackboard.Blackboard.get('docking_error_13')

        if self.bb1 == 1 or self.bb2 == 1 or self.bb3 == 1 or self.bb4 == 1 or self.bb5 == 1 or self.bb6 == 1 or self.bb7 == 1 or self.bb8 == 1 or self.bb9 == 1 or self.bb10 == 1 or self.bb11 == 1 or self.bb12 == 1 or self.bb13 == 1:
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING  



class docking_error_1(py_trees.behaviour.Behaviour):
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
        self.bb1 = py_trees.blackboard.Blackboard.get('docking_error_5')
        self.bb2 = py_trees.blackboard.Blackboard.get('docking_error_6')
        self.bb3 = py_trees.blackboard.Blackboard.get('docking_error_7')
        self.bb4 = py_trees.blackboard.Blackboard.get('docking_error_12')
        self.bb5 = py_trees.blackboard.Blackboard.get('docking_error_14')
        self.bb6 = py_trees.blackboard.Blackboard.get('docking_error_15')

        if self.bb1 == 1 or self.bb2 == 1 or self.bb3 == 1 or self.bb4 == 1 or self.bb5 == 1 or self.bb6 == 1:
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING

class docking_error_2(py_trees.behaviour.Behaviour):
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
        self.bb1 = py_trees.blackboard.Blackboard.get('docking_error_8')
        self.bb2 = py_trees.blackboard.Blackboard.get('docking_error_9')
        self.bb3 = py_trees.blackboard.Blackboard.get('docking_error_16')
        self.bb4 = py_trees.blackboard.Blackboard.get('docking_error_11')
        self.bb5 = py_trees.blackboard.Blackboard.get('docking_error_10')
        self.bb6 = py_trees.blackboard.Blackboard.get('docking_error_17')
        self.bb7 = py_trees.blackboard.Blackboard.get('docking_error_13')


        if self.bb1 == 1 or self.bb2 == 1 or self.bb3 == 1 or self.bb4 == 1 or self.bb5 == 1 or self.bb6 == 1 or self.bb7==1 :
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING

class dockingStatus(py_trees.behaviour.Behaviour):
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

        if self.bb1 == 'docking' and self.bb2 == 'finished':
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING  

class undockingStatus(py_trees.behaviour.Behaviour):
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

        if self.bb1 == 'undocking' and self.bb2 == 'finished':
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING 

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
                
        return py_trees.common.Status.SUCCESS   



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

        py_trees.blackboard.Blackboard.set('current_goal_count', -1)

        py_trees.blackboard.Blackboard.set('current_service_id', '')
        py_trees.blackboard.Blackboard.set('current_safe_mode', 0.0)
        #py_trees.blackboard.Blackboard.set('task_list', [0]) 

        py_trees.blackboard.Blackboard.set('goal_index_num', 1)
        py_trees.blackboard.Blackboard.set('route_index_num', 1)



        py_trees.blackboard.Blackboard.set('route_index_num_waypoint_poi', '')
        py_trees.blackboard.Blackboard.set('route_index_num_map_name', '')
        py_trees.blackboard.Blackboard.set('route_index_num_zone', '')
        py_trees.blackboard.Blackboard.set('route_index_num_floor', '')
        py_trees.blackboard.Blackboard.set('route_index_num_is_ev', '')
        py_trees.blackboard.Blackboard.set('route_index_num_map_change', '')

        py_trees.blackboard.Blackboard.set('route_index_num_+1', '')
        py_trees.blackboard.Blackboard.set('route_index_num_+1_waypoint_poi', '')



        py_trees.blackboard.Blackboard.set('goal_index_num_current_service_code', '' )
        py_trees.blackboard.Blackboard.set('goal_index_num_current_task_id', '')
        py_trees.blackboard.Blackboard.set('goal_index_num_current_tray_id', '')
        py_trees.blackboard.Blackboard.set('goal_index_num_current_goal_id', '' )
        py_trees.blackboard.Blackboard.set('goal_index_num_current_seq', '' )
        py_trees.blackboard.Blackboard.set('goal_index_num_current_lock_option', '' )

        py_trees.blackboard.Blackboard.set('poi_len', 0 )
        py_trees.blackboard.Blackboard.set('user_pw', '')
        py_trees.blackboard.Blackboard.set("tray1_pw","")
        py_trees.blackboard.Blackboard.set("tray2_pw","")

        py_trees.blackboard.Blackboard.set('hri_status', '')   
        py_trees.blackboard.Blackboard.set('hri_tray_id', 0)           

        py_trees.blackboard.Blackboard.set('start_time', '')    
        py_trees.blackboard.Blackboard.set('current_time', '')           
        
        py_trees.blackboard.Blackboard.set('moving_speed', 1.0)     

        py_trees.blackboard.Blackboard.set('tray1', 0)     
        py_trees.blackboard.Blackboard.set('tray2', 0)                     

        py_trees.blackboard.Blackboard.set('current_tts', '')       

        py_trees.blackboard.Blackboard.set('previous_tree', 'undocking_tree')  
        py_trees.blackboard.Blackboard.set('docking_fail_count', 5)    

        py_trees.blackboard.Blackboard.set('qr_result', None)   


    def update(self):
        return py_trees.common.Status.SUCCESS



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

    go_to_low_battery_tree = EnqueueNextService(
        service_name='low_battery_tree', service_version='2.0.0'
    )

    battery_seq.add_children([battery_under_15_check, battery_alarm, go_to_low_battery_tree])
    
    return battery_seq

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

    manual_contacted_alarm = PublishTopic(
        name='manual_contacted_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='manual_charging',
            action='manual_contact',
            action_target='',
            action_result=True
            )
        )

    manual_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="is_charging",
            value=1,
            operator=operator.eq
        )
    )

    manual_charging_alarm = PublishTopic(
        name='manual_contacted_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='initial_state',
            action='manual_charging',
            action_target='',
            action_result=True
            )
        )
    
    not_contacted_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'not_contaced_check',
        check=py_trees.common.ComparisonExpression(
            variable="manual_contacted",
            value=0,
            operator=operator.eq
        )
    )

    manual_uncontact_alarm = PublishTopic(
        name='manual_uncontact_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='manual_charging',
            action='manual_contact',
            action_target='',
            action_result=False
            )
        )

    go_to_init = EnqueueNextService(
        service_name='init_tree', service_version='2.0.0'
    )

    par_error_type = py_trees.composites.Parallel(
        name="par_error_type",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_hw_error = py_trees.composites.Sequence()
    seq_sw_error = py_trees.composites.Sequence()

    error_type_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'error_type_check1',
        check=py_trees.common.ComparisonExpression(
            variable="docking_error_type",
            value='HW',
            operator=operator.eq
        )
    )

    error_type_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'error_type_check2',
        check=py_trees.common.ComparisonExpression(
            variable="docking_error_type",
            value='SW',
            operator=operator.eq
        )
    )


    go_to_inner_peace = EnqueueNextService(
        service_name='inner_peace_tree', service_version='2.0.0'
    )

    seq_not_contacted_check = py_trees.composites.Sequence()

    par_charging_check = py_trees.composites.Parallel(
        name="par_charging_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq_not_contacted_check],
            synchronise=False
        )
    )

    seq_charging = py_trees.composites.Sequence()
    seq_not_charging = py_trees.composites.Sequence()


    manual_charging_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_charging_check2',
        check=py_trees.common.ComparisonExpression(
            variable="is_charging",
            value=0,
            operator=operator.eq
        )
    )

    manual_charging_alarm2 = PublishTopic(
        name='manual_charging_alarm2',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='manual_charging',
            action='manual_charging',
            action_target='',
            action_result=False
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
    
    none_manual_charging_check_again = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'none_manual_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="is_charging",
            value=0,
            operator=operator.eq
        )
    )

    manual_charging_check_again = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_charging_check2',
        check=py_trees.common.ComparisonExpression(
            variable="is_charging",
            value=1,
            operator=operator.eq
        )
    )

    seq.add_children([manual_contacted_check, manual_contacted_alarm, par_charging_check, par_error_type])
    par_charging_check.add_children([seq_charging, seq_not_charging, seq_not_contacted_check])
    seq_charging.add_children([manual_charging_check, manual_charging_alarm, LED_charging_f, LED_charging_r, none_manual_charging_check_again])
    seq_not_charging.add_children([manual_charging_check2, manual_charging_alarm2, manual_charging_check_again])
    seq_not_contacted_check.add_children([not_contacted_check, manual_uncontact_alarm])
    par_error_type.add_children([seq_hw_error, seq_sw_error])
    seq_hw_error.add_children([error_type_check1, go_to_inner_peace])
    seq_sw_error.add_children([error_type_check2, go_to_init])

    return seq



# 비상정지 체크(무빙, ev, charging 캔슬 적용)
def emergency_button_check():

    seq = py_trees.composites.Sequence()

    cancel_goal = NavigationCancel()

    emergency_button_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'emergency_button_check',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button2",
            value=True,
            operator=operator.eq
        )
    )

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
    
    
    go_to_emergency_tree = EnqueueNextService(service_name='emergency_tree', service_version='2.0.0')


    #moving, ev, charging --> cancel_goal
    seq.add_children([emergency_button_check, cancel_goal, cancel_alarm, go_to_emergency_tree])

    return seq

def charging_status_alarm():
    par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    par_charging = py_trees.composites.Parallel(
        name="par_charging",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )
    
    seq_uncontacted = py_trees.composites.Sequence()
    seq_contacted = py_trees.composites.Sequence()

    seq_nocharging = py_trees.composites.Sequence()
    seq_charging = py_trees.composites.Sequence()

    uncontacted_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'uncontacted_check',
                check=py_trees.common.ComparisonExpression(
                variable='auto_contacted',
                value=0,
                operator= operator.eq
            )
        )
    
    uncontacted_check_for_par = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'uncontacted_check_for_par',
                check=py_trees.common.ComparisonExpression(
                variable='auto_contacted',
                value=0,
                operator= operator.eq
            )
        )
    
    contacted_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'contacted_check',
                check=py_trees.common.ComparisonExpression(
                variable='auto_contacted',
                value=1,
                operator= operator.eq
            )
        )
    
    contacted_check_for_par = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'contacted_check_for_par',
                check=py_trees.common.ComparisonExpression(
                variable='auto_contacted',
                value=1,
                operator= operator.eq
            )
        )
    
    nocharging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'nocharging_check',
                check=py_trees.common.ComparisonExpression(
                variable='is_charging',
                value=0,
                operator= operator.eq
            )
        )
    
    nocharging_check_for_par = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'nocharging_check_for_par',
                check=py_trees.common.ComparisonExpression(
                variable='is_charging',
                value=0,
                operator= operator.eq
            )
        )
    
    charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'charging_check',
                check=py_trees.common.ComparisonExpression(
                variable='is_charging',
                value=1,
                operator= operator.eq
            )
        )
    
    charging_check_for_par = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'contacted_check_for_par',
                check=py_trees.common.ComparisonExpression(
                variable='is_charging',
                value=1,
                operator= operator.eq
            )
        )
    
    uncontacted_alarm = PublishTopic(
        name='uncontacted_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='charging',
            action='auto_contact',
            action_target='auto_contact',
            action_result=False
            )
        )
    
    contacted_alarm = PublishTopic(
        name='contacted_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='charging',
            action='auto_contact',
            action_target='auto_contact',
            action_result=True
            )
        )
    
    nocharging_alarm = PublishTopic(
        name='nocharging_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='charging',
            action='auto_charging',
            action_target='auto_charging',
            action_result=False
            )
        )
    
    charging_alarm = PublishTopic(
        name='charging_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='charging',
            action='auto_charging',
            action_target='auto_charging',
            action_result=True
            )
        )
    
    par_contacted_x = py_trees.composites.Parallel(
        name="par_contacted_x",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[contacted_check_for_par],
            synchronise=False
        )
    )

    par_charging_x = py_trees.composites.Parallel(
        name="par_charging_x",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[charging_check_for_par],
            synchronise=False
        )
    )


    # par.add_children([seq_uncontacted, seq_contacted])
    # seq_uncontacted.add_children([uncontacted_check, uncontacted_alarm, par_contacted_x])
    # par_contacted_x.add_children([battery_under_15(), contacted_check_for_par])

    # seq_contacted.add_children([contacted_check, contacted_alarm, par_charging, uncontacted_check_for_par])

    # par_charging.add_children([seq_nocharging, seq_charging])
    # seq_nocharging.add_children([nocharging_check, nocharging_alarm, par_charging_x])
    # par_charging_x.add_children([battery_under_15(), charging_check_for_par])


    # seq_charging.add_children([charging_check, charging_alarm, nocharging_check_for_par])

    par.add_children([battery_under_15(), seq_uncontacted, seq_contacted, seq_nocharging, seq_charging])
    seq_uncontacted.add_children([uncontacted_check, uncontacted_alarm, contacted_check_for_par])
    seq_contacted.add_children([contacted_check, contacted_alarm, uncontacted_check_for_par])
    seq_nocharging.add_children([nocharging_check, nocharging_alarm, charging_check_for_par])
    seq_charging.add_children([charging_check, charging_alarm, nocharging_check_for_par])
    

    return par

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



    seq.add_children([manual_drive_button_check,manual_LED_dimming_front, manual_LED_dimming_rear, go_to_manual_drive  ])

    return seq
    
def tray_close_seq():
    
   
    tray_close1 = BoxClose(position=1, x=1, y=1)
    tray_close2 = BoxClose(position=1, x=1, y=2) 

    #tray_closed = BoxClose(position=1, x=1, y=0) 

    tray_close_seq = py_trees.composites.Sequence()

    tray_close_par1 = py_trees.composites.Parallel(
        name="tray_close_par1",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[tray_close1],
            synchronise=False
        )
    )

    tray_close_par2 = py_trees.composites.Parallel(
        name="tray_close_par1",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[tray_close2],
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
    
    tray_closed_alarm = PublishTopic(
        name='tray_closed_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='moving_tree',
            action='tray_closed',
            action_target='all_tray',
            action_result=True
            )
        )
    
    tray_close_seq.add_children([tray_close_par1, tray_close_par2, tray_closed_alarm ])
    tray_close_par1.add_children([tray_close1, tray1_closed_check])
    tray_close_par2.add_children([tray_close2, tray2_closed_check])

    return tray_close_seq

def admin_password_check_seq():
    
    seq = py_trees.composites.Sequence()  
    
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
    
    


    
    failed_count_alarm = PublishTopic(
                            name='failed_count_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
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
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'admin_auth_check',
                                action = 'admin_auth_success',
                                action_target = 'tray_',
                                action_result = True
                                )   
                            )



    unset_admin_pw_from_ui1 = SetBlackBoard(BB_variable='admin_pw_from_ui', BB_value='')
    unset_admin_pw_from_ui2 = SetBlackBoard(BB_variable='admin_pw_from_ui', BB_value='')

    tts_password_fail1= TTSPlay(tts_name='password_fail', play=True, sequence=True)

    pw_check_reset = SetBlackBoard(BB_variable = 'pw_check',
                                  BB_value = False)  

    seq.add_children([wait_for_pw_req, par2])
    par2.add_children([seq4, final_seq])
    final_seq.add_children([final_check_pw_correct, auth_checkced_alarm, pw_check_reset, unset_admin_pw_from_ui1])
    seq4.add_children([wait_for_pw_req2, par3])
    par3.add_children([seq6, seq7])
    seq6.add_children([pw_correct_check, unset_pw_req1, pw_correct_set1])
    seq7.add_children([pw_incorrect_check,unset_admin_pw_from_ui2, unset_pw_req2, tts_password_fail1, failed_count_alarm ])

    return seq


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
    
    seq_critical_error.add_children([critical_error_check, NavigationCancel(), go_to_critical_error_tree])
    
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
    

    seq_go_to_minor_error_tree.add_children([par_major_error_check_all,NavigationCancel(),  go_to_minor_error_tree])
    par_major_error_check_all.add_children([major_error_level_check, major_error_code_check])
    
    return seq_go_to_minor_error_tree


def create_root():


    # 최상단
    root_seq = py_trees.composites.Sequence()

    BB_start = BB_init()


    # root 선언 - parallel
    root = py_trees.composites.Parallel(
        name="root",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    parallel_get_msg = py_trees.composites.Parallel(
        name="Parallel1",
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
        name='button_status_to_BB')       
    
    def on_msg_fn_emergency_button(msg):
            py_trees.blackboard.Blackboard.set('emergency_button2', msg.data[0].data) #True: 버튼 눌림 # False: 버튼 해제

    emergency_button_info_to_BB =  SubscribeTopic(
            topic_name='button/button_status',
            topic_type=BoolCmdArray,
            on_msg_fn=on_msg_fn_emergency_button,
            name='emergency_button_info_to_BB')    
    

    def on_msg_fn_halt_Status(msg):
        for i in range(2):
            py_trees.blackboard.Blackboard.set('halt_status', msg.halt_status)
            py_trees.blackboard.Blackboard.set('cancel_return_status', msg.cancel_return_status)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/cancel_return_tray_id', msg.tray_id[i].tray_id)
            py_trees.blackboard.Blackboard.set('cancel_return_service_code', msg.service_code)
            py_trees.blackboard.Blackboard.set('cancel_return_service_id', msg.service_id)
            py_trees.blackboard.Blackboard.set('cancel_return_task_id', msg.task_id)
            py_trees.blackboard.Blackboard.set('cancel_return_return_location', msg.return_location)
            py_trees.blackboard.Blackboard.set('cancel_return_moving_status', msg.return_)
    
    halt_Status_to_BB = SubscribeTopic(
        topic_name='ktmw_bt/halt_status',
        topic_type=HaltStatus,
        on_msg_fn=on_msg_fn_halt_Status,
        name='halt_status_to_BB'
    )



    #user_pw request
    def on_msg_fn_pw_req(msg):
        py_trees.blackboard.Blackboard.set('admin_pw_type', msg.type) #user/admin 
        py_trees.blackboard.Blackboard.set('admin_pw_tray_id', msg.tray_id) #string
        py_trees.blackboard.Blackboard.set('admin_pw_from_ui', msg.pw) #uint8

    admin_pw_from_ui_req_msgs_to_BB =  SubscribeTopic(
        topic_name='ktmw_bt/auth_request',
        topic_type=AuthRequest,
        on_msg_fn=on_msg_fn_pw_req,
        name='pw_req_msgs_to_BB')        
     
    

    def on_msg_batt(msg):
        py_trees.blackboard.Blackboard.set('current_battery_level', msg.percentage) #0.0 ~ 1.0

    battery_state_to_BB = SubscribeTopic(
        topic_name="bms/battery_state",
        topic_type=sensor_msgs.BatteryState,
        on_msg_fn=on_msg_batt,
        name='Battery_state_to_BB'
    )    

    #current service start to BB
    def on_msg_fn_current_service_start(msg):

        for i in range(len(msg.task_list)):
            py_trees.blackboard.Blackboard.set('current_service_id', msg.service_id)
            py_trees.blackboard.Blackboard.set('current_goal_count', msg.goal_count)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_service_code', msg.task_list[i].service_code)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_task_id', msg.task_list[i].task_id)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_tray_id', msg.task_list[i].tray_id)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_goal_id', msg.task_list[i].goal_id)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_seq', msg.task_list[i].seq)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_lock_option', msg.task_list[i].lock_option)

    current_service_start_to_BB = SubscribeTopic(
        topic_name='ktmw_bt/current_service_start',
        topic_type=StartService, 
        on_msg_fn=on_msg_fn_current_service_start,
        name='current_service_start_to_BB'
    )

    #tray open status to BB
    def on_msg_fn_tray_open(msg):
        for i in range(2):
            py_trees.blackboard.Blackboard.set('Tray_'+str(i+1)+'_open_status', msg.door_states[i].door_state)

    tray_open_status_to_BB = SubscribeTopic(
        topic_name='box/box_state',
        topic_type=BoxStates,
        on_msg_fn=on_msg_fn_tray_open,
        name='tray_open_status_to_BB')

    #수동운전 상태 to BB -> TBD
    def on_msg_fn_manual_button(msg):
        py_trees.blackboard.Blackboard.set('manual_button', msg.data) #uint8         # passive on:1 passive off:2 emergency on:3, emergency off:4

    manual_to_BB =  SubscribeTopic(
        topic_name='ktmw_bt/button_status',
        topic_type=UInt8,
        on_msg_fn=on_msg_fn_manual_button,
        name='manual_to_BB')


    #경로 to BB -> TBD
    def request_generate_fn_poi2bb():
        req = GetPoiRoute.Request()
        req.goal_label = py_trees.blackboard.Blackboard.get('1/current_goal_id')
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

    route_to_BB = ServiceCall(
        service_name='configuration_manager/get_poi_route',
        service_type=GetPoiRoute,
        request_generate_fn=request_generate_fn_poi2bb,
        response_fn=response_fn_poi2bb,
        name='route_to_BB'
    )

    def on_msg_fn_docking_status(msg):
        for i in range(18):
            py_trees.blackboard.Blackboard.set('docking_error_'+str(i), msg.data[i])

    docking_status_to_BB = SubscribeTopic(
        topic_name='docking/status',
        topic_type=Int8MultiArray,
        on_msg_fn=on_msg_fn_docking_status,
        name='docking_status_to_BB') 



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


    seq_for_serv = py_trees.composites.Sequence("sequence_for_service")

    Service_requested_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'Service_requested_check',
            check=py_trees.common.ComparisonExpression(
            variable="current_goal_count",
            value=0,
            operator= operator.ge
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

    #goal_index_num_reset = py_trees.blackboard.Blackboard.set('goal_index_num', 1)
    #route_index_num_reset = py_trees.blackboard.Blackboard.set('route_index_num', 1)

    go_to_moving = EnqueueNextService(
        service_name='moving_tree', service_version='')


    TTS_par = py_trees.composites.Parallel(
            name="TTS_par",
            policy=py_trees.common.ParallelPolicy.SuccessOnOne(
            )
        )
    
    tts_seq_1 = py_trees.composites.Sequence()
    tts_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'tts_check1',
        check=py_trees.common.ComparisonExpression(
            variable="1/current_service_code",
            value=101,
            operator=operator.eq
        )
    )

    tts_play1 = TTSPlay(tts_name='delivering_start', play=True, sequence=True)

    tts_seq_2 = py_trees.composites.Sequence()
    tts_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'tts_check2',
        check=py_trees.common.ComparisonExpression(
            variable="1/current_service_code",
            value=102,
            operator=operator.eq
        )
    )

    tts_play2 = TTSPlay(tts_name='delivering_start', play=True, sequence=True)

    tts_seq_3 = py_trees.composites.Sequence()

    tts_check3 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'tts_check3',
        check=py_trees.common.ComparisonExpression(
            variable="1/current_service_code",
            value=103,
            operator=operator.eq
        )
    )

    tts_play3 = TTSPlay(tts_name='delivering_resume', play=True, sequence=True)


    tts_seq_4 = py_trees.composites.Sequence()

    tts_check4 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'tts_check4',
        check=py_trees.common.ComparisonExpression(
            variable="1/current_service_code",
            value=901,
            operator=operator.eq
        )
    )

    tts_play4 = TTSPlay(tts_name='returning_start', play=True, sequence=True)

    tts_seq_5 = py_trees.composites.Sequence()
    tts_check5 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'tts_check5',
        check=py_trees.common.ComparisonExpression(
            variable="1/current_service_code",
            value=902,
            operator=operator.eq
        )
    )

    tts_play5 = TTSPlay(tts_name='returning_start', play=True, sequence=True)

    tts_seq_6 = py_trees.composites.Sequence()
    tts_check6 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'tts_check6',
        check=py_trees.common.ComparisonExpression(
            variable="1/current_service_code",
            value=903,
            operator=operator.eq
        )
    )

    tts_play6 = TTSPlay(tts_name='charging_start', play=True, sequence=True)


    # ledoff_1 = LEDControl(
    #     color=LEDControl.COLOR_OFF,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    # ledoff_2 = LEDControl(
    #     color=LEDControl.COLOR_OFF,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    ledoff_1 = PublishTopic(
                name='ledoff_1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )    
    
    ledoff_2 = PublishTopic(
                name='ledoff_2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )    

    
    # rotation
    # led_service_start = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_REVERSE_SEQUENTIAL_LED_OFF, # 로테이션
    #     period_ms=2500,
    #     on_ms=0,
    #     repeat_count=1)
    
    led_service_start = PublishTopic(
                name='led_service_start',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=4,
                    period=2500,
                    on_ms=0,
                    repeat_count=1
                    )   
                )    
    

    wait_led= py_trees.timers.Timer("led_show", duration=0.75)


    BGM_off_cancel = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)




    undocking_seq = py_trees.composites.Sequence()
    

    def request_generate_fn_undocking():
        req = SetNavGoal.Request()
        req.target_label= ''
        req.goal_label = ''
        req.mode = 'undocking'
        req.req_id.command = 0
        req.speed_scale = 1.0
        return req
    
    def response_fn_undocking(response):
        print(response.result)

    undocking_start = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type=SetNavGoal,
        request_generate_fn=request_generate_fn_undocking,
        response_fn=response_fn_undocking,
        name='undocking_start'
    )

    undocking_start_alarm = PublishTopic(
        name='arrived_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('current_service_id'),            
            service_code=903,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='undocking',
            action='undocking_start',
            action_target='docking_station',
            action_result=True
            )
        )

    undocking_finished_alarm = PublishTopic(
        name='arrived_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_id=py_trees.blackboard.Blackboard.get('current_service_id'),        
            service_code=903,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='undocking',
            action='undocking_finished',
            action_target='docking_station',
            action_result=True
            )
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

    seq_undocking_finished = py_trees.composites.Sequence()
    par_undocking_status = py_trees.composites.Parallel(
        name="par_undocking_status",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq_undocking_finished],
            synchronise=False
        )
    )


    par_for_serv_full = py_trees.composites.Parallel(
        name="par_for_serv_full",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        ))

    seq_for_full = py_trees.composites.Sequence()

    full_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'full_check',
                check=py_trees.common.ComparisonExpression(
                variable='current_battery_level',
                value=1.0,
                operator= operator.eq
            )
        )

    # LED_full_f = LEDControl(
    #     color=LEDControl.COLOR_GREEN,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    # LED_full_r = LEDControl(
    #     color=LEDControl.COLOR_GREEN,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    LED_full_f = PublishTopic(
                name='LED_full_f',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )    
    
    LED_full_r = PublishTopic(
                name='LED_full_rs',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=1,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )    

    Idling_full = Idling()



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

    seq_undocking_error = py_trees.composites.Sequence()

    undocking_error_modu_check_1 = docking_error_0()
    undocking_error_modu_check_2 = docking_error_0()
    undocking_error_modu_check_3 = docking_error_0()
    
    par_undocking_fail_count = py_trees.composites.Parallel(
        name="par_undocking_fail_count",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False)
    )

    seq_undocking_fail = py_trees.composites.Sequence()
    seq_final_undocking_fail = py_trees.composites.Sequence()

    undocking_fail_count_check_1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'undocking_fail_count_check_1',
            check=py_trees.common.ComparisonExpression(
            variable="docking_fail_count",
            value=0,
            operator= operator.gt
            )
        )

    fail_reduce1 = Reduce_1(BB_variable = 'docking_fail_count')


    def request_generate_error_reset():
        request = SetNavGoal.Request()
        request.target_label = ''
        request.goal_label = ''
        request.mode = 'docking_error_clear'
        request.req_id.command = 0
        request.speed_scale = 1.0
        return request
    def response_fn_error_reset(response):
        print(response.result)

    undocking_error_reset = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type= SetNavGoal,
        request_generate_fn=request_generate_error_reset,
        response_fn= response_fn_error_reset, name='undocking_error_reset'
    )

    def request_generate_error_reset():
        request = SetNavGoal.Request()
        request.target_label = ''
        request.goal_label = ''
        request.mode = 'docking_error_clear'
        request.req_id.command = 0
        request.speed_scale = 1.0
        return request
    def response_fn_error_reset(response):
        print(response.result)

    undocking_error_reset2 = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type= SetNavGoal,
        request_generate_fn=request_generate_error_reset,
        response_fn= response_fn_error_reset, name='error_reset'
    )
    
    def request_generate_re_docking():
        request = SetNavGoal.Request()
        request.target_label = ''
        request.goal_label = ''
        request.mode = 'undocking'
        request.req_id.command = 0
        request.speed_scale = 1.0
        return request
    def response_fn_re_docking(response):
        print(response.result)

    re_undocking = ServiceCall(
        service_name='nav/set_nav_goal',
        service_type= SetNavGoal,
        request_generate_fn=request_generate_re_docking,
        response_fn= response_fn_re_docking, name='re_undocking'
    )

    re_undocking_alarm = PublishTopic(
        name='re_undocking_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='undocking',
            action='undocking_fail_retry',
            action_target='',
            action_result=True
            )
        )

    undocking_fail_count_check_2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'undocking_fail_count_check_2',
            check=py_trees.common.ComparisonExpression(
            variable="docking_fail_count",
            value=0,
            operator= operator.eq
            )
        )
    
    par_undocking_error_clear_check2 = py_trees.composites.Parallel(
        name="par_undocking_error_clear_check2",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    undocking_error_clear_check_state2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_error_clear_check_state2',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    undocking_error_clear_check_mode2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_error_clear_check_mode2',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='docking_error_clear',
            operator=operator.eq
        )
    )

    par_undocking_fail_check = py_trees.composites.Parallel(
        name="par_undocking_fail_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    undocking_fail_check_state = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_fail_check_state',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='failed',
            operator=operator.eq
        )
    )

    undocking_fail_check_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_fail_check_mode',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='undocking',
            operator=operator.eq
        )
    )

    par_undocking_finished_check = py_trees.composites.Parallel(
        name="par_undocking_finished_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    undocking_finished_state_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_finished_state_check',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    undocking_finished_mode_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_finished_mode_check',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='undocking',
            operator=operator.eq
        )
    )

    par_undocking_error_clear_check = py_trees.composites.Parallel(
        name="par_undocking_error_clear_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    undocking_error_clear_check_state = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_error_clear_check_state',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    undocking_error_clear_check_mode = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_error_clear_check_mode',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='docking_error_clear',
            operator=operator.eq
        )
    )

    par_undocking_error_clear_check2 = py_trees.composites.Parallel(
        name="par_undocking_error_clear_check2",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    undocking_error_clear_check_state2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_error_clear_check_state2',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    undocking_error_clear_check_mode2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_error_clear_check_mode2',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='docking_error_clear',
            operator=operator.eq
        )
    )

    par_undocking_fail_check2 = py_trees.composites.Parallel(
        name="par_undocking_fail_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    undocking_fail_check_state2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_fail_check_state',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='failed',
            operator=operator.eq
        )
    )

    undocking_fail_check_mode2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'docking_fail_check_mode',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='undocking',
            operator=operator.eq
        )
    )

    par_undocking_finished_check = py_trees.composites.Parallel(
        name="par_undocking_finished_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    undocking_finished_state_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_finished_state_check',
        check=py_trees.common.ComparisonExpression(
            variable="nav_status",
            value='finished',
            operator=operator.eq
        )
    )

    undocking_finished_mode_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'undocking_finished_mode_check',
        check=py_trees.common.ComparisonExpression(
            variable="mode",
            value='undocking',
            operator=operator.eq
        )
    )

    par_undocking_error_analysis = py_trees.composites.Parallel(
        name="par_undocking_error_analysis",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )
    seq_undocking_hw_error = py_trees.composites.Sequence()
    seq_undocking_just_error = py_trees.composites.Sequence()

    undocking_hw_error_check = docking_error_1()
    undocking_just_error_check = docking_error_2()

    undocking_hw_error_alarm = PublishTopic(
                            name='undocking_hw_error_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'undocking',
                                action = 'hw_error',
                                action_target = 'docking_station',
                                action_result = True
                                )   
                            )
    
    undocking_sw_error_alarm = PublishTopic(
                            name='undocking_sw_error_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'undocking',
                                action = 'sw_error',
                                action_target = 'docking_station',
                                action_result = True                                
                                )   
                            )

    set_undocking_error_type1 = SetBlackBoard('docking_error_type', 'HW')
    set_undocking_error_type2 = SetBlackBoard('docking_error_type', 'SW')

   
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

    root_sel = py_trees.composites.Selector('undocking_tree')
    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
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
    
    unset_current_service = unset_current()
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

    def on_msg_fn_auth_pw_status(msg):
        py_trees.blackboard.Blackboard.set('admin_pw', msg.update_code_list)
       

    auth_pw_topic_to_BB = SubscribeTopic(
        topic_name='rm_agent/admin_pw_change_alarm_by_robot',
        topic_type=Password,
        on_msg_fn=on_msg_fn_auth_pw_status,
        name='auth_pw_topic_to_BB')      

    def request_generate_fn_auto_map():
        req = NavMapLoad.Request()
        req.map_name = py_trees.blackboard.Blackboard.get('charging_map_name')
        req.reset = False
        req.localization_only = True
        req.resolution = 0.0 #float64
        req.label = py_trees.blackboard.Blackboard.get('charging_poi_id')
        return req
    def response_fn_auto_map(response):
        #print(response.success)
        print(response.result)
        py_trees.blackboard.Blackboard.set('map_check', response.result)

    auto_charging_map_set = ServiceCall(service_name='nav/map_load', service_type=NavMapLoad, request_generate_fn= request_generate_fn_auto_map,
                       response_fn= response_fn_auto_map , name='map_set')    
    
    root_sel.add_children([root_seq, go_to_ciritcal_error2])

    root_seq.add_children([BGM_off_cancel, BB_start, root])
    
    root.add_children([parallel_get_msg, check_critical_error(), go_to_minor_error_tree(), minor_error_alarm(), charging_status_alarm(), check_manual_drive(), check_manual_charge(), emergency_button_check(), par_for_serv_full, admin_password_check_seq()])
    parallel_get_msg.add_children([error_set_to_BB,emergency_button_info_to_BB, button_status_to_BB, charging_state_to_BB, nav_status_to_BB, admin_pw_from_ui_req_msgs_to_BB, halt_Status_to_BB, battery_state_to_BB,current_service_start_to_BB, tray_open_status_to_BB, manual_to_BB, docking_status_to_BB, auth_pw_topic_to_BB ])
    
    par_for_serv_full.add_children([seq_for_full, seq_for_serv])
    seq_for_full.add_children([full_check, LED_full_f, LED_full_r, Idling_full])
    seq_for_serv.add_children([Service_requested_check, route_to_BB, par_route_ready_check, led_service_start, wait_led, TTS_par, undocking_seq, go_to_moving])
    par_route_ready_check.add_children([route_ready_check, seq_route_fail_check])
    seq_route_fail_check.add_children([route_fail_check, route_fail_alarm, unset_current_service, unset_route_fail, Service_requested_check2, route_to_BB2])


    undocking_seq.add_children([undocking_start, led_start_on_restart_f, led_start_on_restart_r, undocking_start_alarm, par_undocking_status])
    par_undocking_status.add_children([seq_undocking_error, seq_undocking_finished])
    
    seq_undocking_error.add_children([par_undocking_fail_check2, undocking_error_modu_check_1, par_undocking_fail_count])
    par_undocking_fail_check2.add_children([undocking_fail_check_state2, undocking_fail_check_mode2])
    par_undocking_fail_count.add_children([seq_undocking_fail, seq_final_undocking_fail])
    seq_undocking_fail.add_children([undocking_error_modu_check_2, undocking_fail_count_check_1,  undocking_error_reset, par_undocking_error_clear_check2, re_undocking, re_undocking_alarm, par_undocking_fail_check, fail_reduce1])
    par_undocking_error_clear_check2.add_children([undocking_error_clear_check_state2, undocking_error_clear_check_mode2])
    par_undocking_fail_check.add_children([undocking_fail_check_state, undocking_fail_check_mode])
    seq_final_undocking_fail.add_children([undocking_error_modu_check_3, undocking_fail_count_check_2, undocking_error_reset2, par_undocking_error_clear_check, par_undocking_error_analysis])
    par_undocking_error_clear_check.add_children([undocking_error_clear_check_state, undocking_error_clear_check_mode])
    par_undocking_error_analysis.add_children([seq_undocking_hw_error, seq_undocking_just_error])
    seq_undocking_hw_error.add_children([undocking_hw_error_check, undocking_hw_error_alarm, set_undocking_error_type1, battery_under_15()])
    seq_undocking_just_error.add_children([undocking_just_error_check, undocking_sw_error_alarm, set_undocking_error_type2, battery_under_15()])

    seq_undocking_finished.add_children([par_undocking_finished_check,auto_charging_map_set, undocking_finished_alarm])
    par_undocking_finished_check.add_children([undocking_finished_state_check, undocking_finished_mode_check])

    TTS_par.add_children([tts_seq_1,tts_seq_2,tts_seq_3,tts_seq_4,tts_seq_5,tts_seq_6])
    tts_seq_1.add_children([tts_check1, tts_play1])
    tts_seq_2.add_children([tts_check2, tts_play2])
    tts_seq_3.add_children([tts_check3, tts_play3])
    tts_seq_4.add_children([tts_check4, tts_play4])
    tts_seq_5.add_children([tts_check5, tts_play5])
    tts_seq_6.add_children([tts_check6, tts_play6])

    return root_sel


