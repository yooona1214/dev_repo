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
import py_trees_ros
import operator
import json

from kt_msgs.msg import BoxState, BoxStates
from ktmw_bt_interfaces.msg import (DoorState, InstalleStatus, NavStatusAlarm,
                                    ObjectSensing, 
                                    ServiceArrivedAlarm, ServiceFailAlarm,
                                    ServiceStartAlarm, SoundControl, Task,
                                    TaskStatus,
                                    ItemReturn, 
                                    HRI,
                                    AuthRequest)
from std_srvs.srv import SetBool

from std_msgs.msg import UInt8

from std_msgs.msg import Int8MultiArray
import sensor_msgs.msg as sensor_msgs
from kt_msgs.msg import BoolCmdArray, LEDState, Location, LEDEffect

from ktmw_srvmgr_lib.common import (CreateService,  
                                    ServiceCall,
                                    PublishTopic,
                                    SubscribeTopic,
                                    EnqueueNextService,
                                    NoResponseCheck,
                                    SetBlackBoard,
                                    compareBBvariableforcorrect,
                                    compareBBvariableforincorrect,
                                    GetTrayStatus,
                                    GetandSetBlackBoard,
                                    GetCurrentTime,
                                    InitCount,
                                    TTSPlay,
                                    Idling)

from config_manager_msgs.srv import GetPoiRoute


from ktmw_srvmgr_lib.hardware import (BoxCtrl, BoxLock, BoxUnlock, LEDControl,
                                      LEDControlWithFn, LEDOff)


from data_manager_msgs.srv import CreateFile, GetFile
from std_msgs.msg import Empty
from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm


SERVICE_NAME = 'tray_cancel1'
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

        py_trees.blackboard.Blackboard.set('previous_tree', 'tray_cancel1')
        py_trees.blackboard.Blackboard.set('go_to_next_state_passed', False)




    def update(self):
        return py_trees.common.Status.SUCCESS
    
class unset_route_info(py_trees.behaviour.Behaviour):
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
        py_trees.blackboard.Blackboard.set('route_index_num', 1)
        
        poi_len = py_trees.blackboard.Blackboard.get('poi_len')
        for i in range(poi_len):
            py_trees.blackboard.Blackboard.set('poi_success_check',None)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/waypoint_poi','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_name','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/zone','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/floor','')
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/is_ev',False)
            py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_change',False)

        return py_trees.common.Status.SUCCESS


class GetandSetCurrentTrayBlackBoard(py_trees.behaviour.Behaviour):
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
        
        self.a = 'Tray_'+str(py_trees.blackboard.Blackboard.get('tray1'))+'_stuff_status'
        #py_trees.blackboard.Blackboard.set('abc', 'Tray_'+str(py_trees.blackboard.Blackboard.get('tray1'))+'_stuff_status')
        py_trees.blackboard.Blackboard.set(self.BB_variable, py_trees.blackboard.Blackboard.get(self.a))
                
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

        py_trees.blackboard.Blackboard.set('a', py_trees.blackboard.Blackboard.get('goal_index_num'))

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
                                task_status = 'cancel_return',
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



# 비상정지 체크(무빙, ev, charging 캔슬 적용)
def emergency_button_check():

    seq = py_trees.composites.Sequence()


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
    seq.add_children([emergency_button_check ,go_to_emergency_tree])

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

    go_to_manualcharging = EnqueueNextService(
        service_name='manual_charging_tree', service_version='2.0.0'
    )

    seq.add_children([manual_contacted_check, go_to_manualcharging ])

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

def msgs_to_BB_parallel():

    par = py_trees.composites.Parallel(
        name="Msgs_to_BB_parallel",
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


    #item_return
    def on_msg_fn_item_return(msg):
        py_trees.blackboard.Blackboard.set('item_return_tray_id', msg.tray_id) #uint8
        py_trees.blackboard.Blackboard.set('item_return_check', msg.check) #bool

    item_return_msgs_to_BB =  SubscribeTopic(
        topic_name='ktmw_bt/item_return',
        topic_type=ItemReturn,
        on_msg_fn=on_msg_fn_item_return,
        name='item_return_msgs_to_BB')
    

    #HRI user touch
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
    


    #tray_status
    def on_msg_fn_tray_open(msg):
        for i in range(2):
            py_trees.blackboard.Blackboard.set('Tray_'+str(i+1)+'_open_status', msg.door_states[i].door_state)
            py_trees.blackboard.Blackboard.set('Tray_'+str(i+1)+'_stuff_status', msg.door_states[i].has_stuff)


    tray_open_status_to_BB = SubscribeTopic(
        topic_name='box/box_state',
        topic_type=BoxStates,
        on_msg_fn=on_msg_fn_tray_open,
        name='tray_open_status_to_BB')    
    
    #TODO
    #remote_unlock_req
    def on_msg_fn_tray_open(msg):
        py_trees.blackboard.Blackboard.set('remote_unlock', True)

    remote_unlock_status_to_BB = SubscribeTopic(
        topic_name='rm_agent/service_unlock_request',
        topic_type=Empty,
        on_msg_fn=on_msg_fn_tray_open,
        name='remote_unlock_status_to_BB') 
    
    
    #이벤트성 버튼 불리안
    def on_msg_fn_button_status(msg):
         # 0: power off, 1: power_reboot, 2: manual_driving, 3: emergency, 4: power_on
        py_trees.blackboard.Blackboard.set('button_power_off', msg.data[0].data)
        py_trees.blackboard.Blackboard.set('button_power_reboot', msg.data[1].data)            
        py_trees.blackboard.Blackboard.set('button_manual_driving', msg.data[2].data)            
        py_trees.blackboard.Blackboard.set('emergency_button', msg.data[3].data)  #button_emergency           
        py_trees.blackboard.Blackboard.set('button_power_on', msg.data[4].data)            
    
    def on_msg_fn_emergency_button(msg):
            py_trees.blackboard.Blackboard.set('emergency_button2', msg.data[0].data) #True: 버튼 눌림 # False: 버튼 해제

    emergency_button_info_to_BB =  SubscribeTopic(
            topic_name='button/button_status',
            topic_type=BoolCmdArray,
            on_msg_fn=on_msg_fn_emergency_button,
            name='emergency_button_info_to_BB')    
    
    button_status_to_BB =  SubscribeTopic(
        topic_name='button/button_action_cmd',
        topic_type=BoolCmdArray,
        on_msg_fn=on_msg_fn_button_status,
        name='button_info_to_BB')       


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

    #tray exception status to BB
    def on_msg_fn_box_exception(msg):
        py_trees.blackboard.Blackboard.set('Tray_'+str(msg.door_states[0].location.y)+'_exception_status', msg.door_states[0].door_state) # 1: 물건 끼임 / 2: 고장 동작 이상


    box_exception_to_BB = SubscribeTopic(
        topic_name='box/box_exception',
        topic_type=BoxStates,
        on_msg_fn=on_msg_fn_box_exception,
        name='box_exception_to_BB')

    par.add_children([emergency_button_info_to_BB, error_set_to_BB, item_return_msgs_to_BB, button_status_to_BB, battery_state_to_BB, charging_state_to_BB, user_input_msgs_to_BB, 
                      admin_pw_from_ui_req_msgs_to_BB,  tray_open_status_to_BB, remote_unlock_status_to_BB, box_exception_to_BB])



    return par


def time_delay_check_seq():

    seq = py_trees.composites.Sequence()

    par = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )

    seq_user_input_delay = py_trees.composites.Sequence()

    seq_no_user_input = py_trees.composites.Sequence()

    time_check = NoResponseCheck(time1='standby_duration')
    
    wait_for_next = py_trees.timers.Timer("wait_for_next", duration=1.5)

    par_hri_pw_check = py_trees.composites.Parallel(
        name="par_hri_pw_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )

    hri_arrived_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'hri_arrived_check',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value= 'Arrived_check',
                operator= operator.eq
            )
        )
    


    pw_input_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name='pw_input_check',
        check=py_trees.common.ComparisonExpression(
        variable='admin_pw_type',
        value='admin',
        operator= operator.eq
        )
    )

    user_input_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name='user_input_check',
        check=py_trees.common.ComparisonExpression(
        variable='hri_status',
        value='User_input',
        operator= operator.eq
        )
    )

    tts_user_input_delayed = TTSPlay(tts_name='user_input_delayed', play=True, sequence=True)

    get_start_time = GetCurrentTime()

    par_input_delay = py_trees.composites.Parallel(
        name="par",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    Idling1 = Idling()

    Flag_T = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'Flag_T',
                check=py_trees.common.ComparisonExpression(
                variable='flag_for_final_fail_time',
                value=True,
                operator= operator.eq
            )
        )
    
    Flag_F = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'Flag_F',
                check=py_trees.common.ComparisonExpression(
                variable='flag_for_final_fail_time',
                value=False,
                operator= operator.eq
            )
        )    

    par_sel = py_trees.composites.Parallel(
        name="par_sel",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[Flag_T],
            synchronise=False
        )
    )

    seq_no_res = py_trees.composites.Sequence()

    user_input_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name='user_input_check',
        check=py_trees.common.ComparisonExpression(
        variable='hri_status',
        value='User_input',
        operator= operator.eq
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

    seq.add_children([get_start_time, par, par_input_delay])
    par.add_children([seq_no_user_input, par_hri_pw_check])

    par_input_delay.add_children([seq_user_input_delay, Idling1])

    seq_no_user_input.add_children([time_check, wait_for_next, go_to_next_state()])
    par_hri_pw_check.add_children([hri_arrived_check, pw_input_check, user_input_check])

    seq_user_input_delay.add_children([par_sel, Flag_F])
    
    par_sel.add_children([seq_no_res, Flag_T])
    seq_no_res.add_children([no_response_check(time11='user_input_duration'), user_input_delay_alarm, go_to_next_state()])
    return seq

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

    # led_start_on_pw_done_f = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_start_on_pw_done_r = LEDControl(
    #     color=LEDControl.COLOR_BLUE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    led_start_on_pw_done_f = PublishTopic(
                name='led_start_on_pw_done_f',
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

    led_start_on_pw_done_r = PublishTopic(
                name='led_start_on_pw_done_r',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=0, b=255),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    seq.add_children([wait_for_pw_req, par2])
    par2.add_children([seq4, final_seq])
    final_seq.add_children([final_check_pw_correct, auth_checkced_alarm,led_start_on_pw_done_f, led_start_on_pw_done_r, unset_admin_pw_from_ui1])
    seq4.add_children([wait_for_pw_req2, par3])
    par3.add_children([seq6, seq7])
    seq6.add_children([pw_correct_check, unset_pw_req1, pw_correct_set1])
    seq7.add_children([pw_incorrect_check,unset_admin_pw_from_ui2, unset_pw_req2, tts_password_fail1, failed_count_alarm, led_start_on_pw_incorrect_f, led_start_on_pw_incorrect_r ])

    return seq


def tray_action_seq():

    seq = py_trees.composites.Sequence()

    wait_hri_tray_open_cmd = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_hri_tray_open_cmd',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Tray_open',
                operator= operator.eq
            )
        )


    def request_generate_fn_tray_open():
        request = BoxCtrl.Request()
        request.data.box_command = 1
        request.data.location.position = 1
        request.data.location.x = 1
        request.data.location.y = py_trees.blackboard.Blackboard.get('hri_tray_id')
        return request
    def response_fn_tray_open(response):
        print(response.success)

    tray_open = ServiceCall(
        service_name='hardware_manager/box/box_control',
        service_type= BoxCtrl,
        request_generate_fn=request_generate_fn_tray_open,
        response_fn= response_fn_tray_open, name='tray_open'

    )


    hri_finished_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'hri_finished_check',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Finished_check',
                operator= operator.eq
            )
        )
    

    seq.add_children([wait_hri_tray_open_cmd, tray_open, hri_finished_check])

    return seq

def go_to_next_state():
    


    
    #setBlackboard
    
    seq1 = py_trees.composites.Sequence()

    par1 = py_trees.composites.Parallel(
        name="par1",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )



    seq3 = py_trees.composites.Sequence()
    seq4 = py_trees.composites.Sequence()

    tray_object_sensing_full_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'object_full',
        check=py_trees.common.ComparisonExpression(
        variable="Tray_current_stuff_status",
        value=True,
        operator= operator.eq
        )
    )

    tray_object_sensing_empty_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'object_empty',
        check=py_trees.common.ComparisonExpression(
        variable="Tray_current_stuff_status",
        value=False,
        operator= operator.eq
        )
    )

    task_fail_alarm = PublishTopic(
                            name='task_fail_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'cancel_return',
                                action = 'fail',
                                action_target = 'tray_'+str(py_trees.blackboard.Blackboard.get('tray1')),
                                action_result = True
                                )   
                            )     

                       
    
    set_BB_fail = SetBlackBoard(BB_variable='no_standby', BB_value=True)

    go_to_cancel_again = EnqueueNextService(
        service_name='idle_tree', service_version=''
    )
    go_to_idle2 = EnqueueNextService(
        service_name='BB_clear', service_version=''
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
                                task_status = 'cancel_return',
                                action = 'cancel_return',
                                action_target = 'tray1',
                                action_result = True
                                )   
                            )
    


    tray_current_set = GetandSetCurrentTrayBlackBoard(BB_variable='Tray_current_stuff_status')  

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

    tray2_closed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_closed_check',
            check=py_trees.common.ComparisonExpression(
            variable="Tray_2_open_status",
            value=1,
            operator= operator.eq
            )
        )

    go_to_next_state_passed_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'go_to_next_state_passed_check',
        check=py_trees.common.ComparisonExpression(
        variable="go_to_next_state_passed",
        value=False,
        operator= operator.eq
        )
    )

    set_go_to_next_state = SetBlackBoard(BB_variable='go_to_next_state_passed', BB_value=True)

    seq1.add_children([opened_tray_check_and_close(), go_to_next_state_passed_check, set_go_to_next_state, par_tray_all_closed, tray_current_set, par1])

    # seq1.add_children([opened_tray_check_and_close(), par_tray_all_closed, tray_current_set, par1])
    par_tray_all_closed.add_children([tray1_closed_check, tray2_closed_check])

    par1.add_children([seq3, seq4])
    seq3.add_children([tray_object_sensing_full_check, task_fail_alarm, set_BB_fail, go_to_cancel_again])
    seq4.add_children([tray_object_sensing_empty_check, task_finished_alarm, go_to_idle2 ])

    return seq1


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
    
    seq_critical_error.add_children([critical_error_check, go_to_critical_error_tree])
    
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
    

    seq_go_to_minor_error_tree.add_children([par_major_error_check_all, go_to_minor_error_tree])
    par_major_error_check_all.add_children([major_error_level_check, major_error_code_check])
    
    return seq_go_to_minor_error_tree

def create_root():

    # root 선언 - parallel
    root = py_trees.composites.Parallel(
        name="Tray_cancel1_tree",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )
    main_seq = py_trees.composites.Sequence()

    tray_action_start_tts= TTSPlay(tts_name='delivering_arrived', play=True, sequence=True)

    
                            
    get_tray_info = GetTrayInfo()


    bb_start = BB_init()

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
                name='LED_charging_f',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=255),
                    effect=1,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )  

    pw_check_set = SetBlackBoard(BB_variable = 'pw_check',
                                 
                                  BB_value = False)  
    task_available_alarm = PublishTopic(
                            name='task_available_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_id'),
                                service_code=py_trees.blackboard.Blackboard.get('goal_index_num_current_service_code'),
                                task_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_task_id'),
                                goal_id=py_trees.blackboard.Blackboard.get('goal_index_num_current_goal_id'),
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'task_available',
                                action = 'task_available',
                                action_target = 'task_available',
                                action_result = True
                                )   
                            )          
    
    root_sel = py_trees.composites.Selector('tray_cancel1')
    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
    )

    hri_finished_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'hri_finished_check',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Finished_check',
                operator= operator.eq
            )
        )    
    
    par_action = py_trees.composites.Parallel(
        name="par1",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )

    root_sel.add_children([root, go_to_ciritcal_error2])
    root.add_children([msgs_to_BB_parallel(), check_critical_error(), go_to_minor_error_tree(), minor_error_alarm(), check_manual_drive(), check_manual_charge(), emergency_button_check(), battery_under_15(), time_delay_check_seq(), tray_stuck_seq_new(), main_seq ])
    main_seq.add_children([bb_start, pw_check_set, LED_charging_f, LED_charging_r, get_tray_info, tray_action_start_tts, task_available_alarm, par_action, go_to_next_state()])
    par_action.add_children([hri_finished_check, tray_action_seq()])
    
    return root_sel


