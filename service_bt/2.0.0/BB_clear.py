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

from ktmw_bt_interfaces.msg import TaskStatus, HaltStatus, AuthRequest, HRI, ItemReturn
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

from std_msgs.msg import Empty
from std_msgs.msg import Int8MultiArray
import sensor_msgs.msg as sensor_msgs
from kt_msgs.msg import BoolCmdArray, LEDState, Location, LEDEffect

from std_srvs.srv import SetBool
from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm
# ** Required **
SERVICE_NAME = 'BB-clear-tree'
# ** Required **
SERVICE_VERSION = '0.1.0'

class BBclear(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        py_trees.blackboard.Blackboard.clear()


    def update(self):

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

        py_trees.blackboard.Blackboard.set('qr2map_flag', False)
        py_trees.blackboard.Blackboard.set('map_available_flag', False)
        py_trees.blackboard.Blackboard.set('no_standby',False)
        py_trees.blackboard.Blackboard.set('battery_low_warning',False)
        py_trees.blackboard.Blackboard.set('1/current_service_code', 101)
        py_trees.blackboard.Blackboard.set('a', 0)
        py_trees.blackboard.Blackboard.set('Tray_1_open_status','')
        py_trees.blackboard.Blackboard.set('Tray_2_open_status','')
        py_trees.blackboard.Blackboard.set('pw_count', 0)

        py_trees.blackboard.Blackboard.set('is_charging', '')
        py_trees.blackboard.Blackboard.set('auto_contacted', '')
        py_trees.blackboard.Blackboard.set('manual_contacted', '')   

        py_trees.blackboard.Blackboard.set('qr_id', '')
        py_trees.blackboard.Blackboard.set('qr_header', '')
        py_trees.blackboard.Blackboard.set('qr_pose', '')
        py_trees.blackboard.Blackboard.set('qr_result', None)   
        py_trees.blackboard.Blackboard.set('emergency_button', '')    
        py_trees.blackboard.Blackboard.set('emergency_button2', '')    

        py_trees.blackboard.Blackboard.set('previous_tree', 'BB_clear')
        py_trees.blackboard.Blackboard.set('previous_tree2', '') 
        py_trees.blackboard.Blackboard.set('ev_zone_result', 0)    
        py_trees.blackboard.Blackboard.set('unknown_zone_result', 0)                    
        py_trees.blackboard.Blackboard.set('keepout_zone_result', 0)        

        py_trees.blackboard.Blackboard.set('ev_unknown_flag', 0)

        
        py_trees.blackboard.Blackboard.set('docking_error_0', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_1', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_2', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_3', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_4', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_5', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_6', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_7', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_8', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_9', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_10', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_11', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_12', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_13', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_14', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_15', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_16', '')                    
        py_trees.blackboard.Blackboard.set('docking_error_17', '')               
        
        py_trees.blackboard.Blackboard.set('service_code', '')    

        py_trees.blackboard.Blackboard.set('mode', '')    
        py_trees.blackboard.Blackboard.set('nav_status', '')
        py_trees.blackboard.Blackboard.set('qr_manual_charging', 0)     

    def update(self):
        return py_trees.common.Status.SUCCESS

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
        
    par.add_children([error_set_to_BB, emergency_button_info_to_BB, button_status_to_BB, battery_state_to_BB, charging_state_to_BB])


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



    seq.add_children([manual_drive_button_check, manual_LED_dimming_front, manual_LED_dimming_rear, go_to_manual_drive  ])

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


    go_to_manualcharging = EnqueueNextService(
        service_name='manual_charging_tree', service_version='2.0.0'
    )

    seq.add_children([manual_contacted_check, go_to_manualcharging ])

    return seq

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


    #moving, ev, charging --> cancel_goal
    seq.add_children([emergency_button_check, go_to_emergency_tree])

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

    battery_seq.add_children([battery_under_15_check, battery_alarm, go_to_low_battery_tree ])
    
    return battery_seq

# ** Required ** tree generate function name: create_root
def create_root():
    """
    Black Board의 모든 key를 초기화하는 트리
    """

    root_seq = py_trees.composites.Sequence('BB_clear_tree')

    bb_clear = BBclear()

    BB_start = BB_init()

    def request_generate_fn_config_msgs():
        req = GetFile.Request()
        req.type = 'config'
        req.version = '1.0.0'
        req.file = 'service_app_config.json'
        return req
    
    def response_fn_config_msgs(response):
        val = response.data.string_value
        j_value = json.loads(val)
        moving_speed= j_value['moving_speed']
        recharge_battery_lev= j_value['recharge_battery_lev']
        standby_duration = j_value['standby_duration']
        user_input_duration = j_value['user_input_duration']
        charging_map_name = j_value['charging_loc']['map_name']
        charging_poi_id = j_value['charging_loc']['poi_id']

      
        py_trees.blackboard.Blackboard.set('moving_speed',moving_speed)
        py_trees.blackboard.Blackboard.set('recharge_battery_level',recharge_battery_lev)  
        py_trees.blackboard.Blackboard.set('standby_duration',standby_duration * 60)  
        py_trees.blackboard.Blackboard.set('standby_duration2',standby_duration * 30)
        py_trees.blackboard.Blackboard.set('user_input_duration',user_input_duration * 60)    
        py_trees.blackboard.Blackboard.set('charging_map_name',charging_map_name)    
        py_trees.blackboard.Blackboard.set('charging_poi_id',charging_poi_id )    

        #print(response.result)

    config_msgs_to_BB = ServiceCall('data_manager/get_file', GetFile, request_generate_fn_config_msgs,
                                         response_fn_config_msgs, name='config_msgs_to_BB')


    def request_generate_fn_admin_pw():
        req = GetFile.Request()
        req.type = 'auth'
        req.version = '1.0.0'
        req.file = 'admin_pw.json'
        return req
    
    def response_fn_admin_pw(response):
        re = response.result
        val = response.data.string_value
        j_value = json.loads(val)
        pw = j_value['code_1']

        py_trees.blackboard.Blackboard.set('admin_pw',pw)
        #print(response.result)

    auth_pw_msgs_to_BB = ServiceCall('data_manager/get_file_decrypt', GetFile, request_generate_fn_admin_pw,
                                         response_fn_admin_pw, name='auth_pw_msgs_to_BB')    


    go_to_Idle_tree = EnqueueNextService(
        service_name='idle_tree', service_version='2.0.0'
    )   

    root = py_trees.composites.Parallel(
        name="root",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )
    

    root.add_children([root_seq, go_to_minor_error_tree(), check_critical_error(), parallel_get_msg_toBB(),  check_manual_drive(), check_manual_charge(), emergency_button_check(), battery_under_15()])
         
    # Reset Every value of Blackboard
    root_seq.add_children([bb_clear, BB_start, config_msgs_to_BB, auth_pw_msgs_to_BB, go_to_Idle_tree])

    

    return root









