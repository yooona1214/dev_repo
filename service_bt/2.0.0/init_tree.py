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
import json
from std_msgs.msg import  UInt8
from ktmw_srvmgr_lib.common import SetBlackBoard,  PublishTopic, EnqueueNextService, SubscribeTopic, ServiceCall, Idling, TTSPlay
from slam_manager_msgs.srv import NavMapLoad
from data_manager_msgs.srv import  GetFile
import sensor_msgs.msg as sensor_msgs
from std_msgs.msg import Int8MultiArray
from ktmw_srvmgr_lib.hardware import LEDControl, BoxClose

from kt_msgs.msg import BoolCmdArray, Tag, LEDState, Location, LEDEffect

from ktmw_bt_interfaces.msg import TaskStatus ,HRI

from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm
from ktmw_srvmgr_lib.hardware import BoxCtrl
from kt_msgs.msg import BoxStates


# ** Required **
SERVICE_NAME = 'init-tree'
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


        # TODO TBD

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
        # TODO TBD

        py_trees.blackboard.Blackboard.set('qr2map_flag', False)
        py_trees.blackboard.Blackboard.set('map_available_flag', False)
        py_trees.blackboard.Blackboard.set('no_standby',False)
        py_trees.blackboard.Blackboard.set('battery_low_warning',False)
        py_trees.blackboard.Blackboard.set('1/current_service_code', 101)
        py_trees.blackboard.Blackboard.set('a', 0)
        py_trees.blackboard.Blackboard.set('Tray_1_open_status','')
        py_trees.blackboard.Blackboard.set('Tray_2_open_status','')
        py_trees.blackboard.Blackboard.set('Tray_1_exception_status', 0)
        py_trees.blackboard.Blackboard.set('Tray_2_exception_status', 0)        
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
        py_trees.blackboard.Blackboard.set('previous_tree', 'init_tree')
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

        py_trees.blackboard.Blackboard.set('error_status', False)
        py_trees.blackboard.Blackboard.set('error_cause', '')   
        py_trees.blackboard.Blackboard.set('error_level', '')   
        py_trees.blackboard.Blackboard.set('alarm_code_error_level', 0)
        py_trees.blackboard.Blackboard.set('hri_status', '')


    def update(self):
        return py_trees.common.Status.SUCCESS




# 실시간 버튼 상태 체크. 부팅 시, 비상정지 눌림 확인용도 
def emergency_button_check2():

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

    tray_close_check1 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray_close_check1',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Tray_close',
                operator= operator.eq
            )
        )


    tray_close_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'tray_close_check2',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Tray_close',
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


    wait_tray_close1 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_tray_close1',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Tray_close',
                operator= operator.eq
            )
        )
    wait_tray_close2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'wait_tray_close2',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='Tray_close',
                operator= operator.eq
            )
        )


    par_stuck_close.add_children([seq_stuck1, seq_stuck2])

    seq_stuck1.add_children([tray1_stuck_check, unset_hri1, unset_hri_status1, stuck_alarm1, unset_stuck1, tts_tray_error, tray_not_ing_check(), wait_tray_close1,tray_close1])


    seq_stuck2.add_children([tray2_stuck_check,  unset_hri2, unset_hri_status2, stuck_alarm2, unset_stuck2, tts_tray_error2, tray_not_ing_check(), wait_tray_close2, tray_close2])
    
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

    def on_msg_fn_emergency_button(msg):
            py_trees.blackboard.Blackboard.set('emergency_button2', msg.data[0].data) #True: 버튼 눌림 # False: 버튼 해제

    emergency_button_info_to_BB =  SubscribeTopic(
            topic_name='button/button_status',
            topic_type=BoolCmdArray,
            on_msg_fn=on_msg_fn_emergency_button,
            name='emergency_button_info_to_BB')    
    

    def on_msg_fn_button_status(msg):
         # 0: power off, 1: power_reboot, 2: manual_driving, 3: emergency, 4: power_on
        py_trees.blackboard.Blackboard.set('button_power_off', msg.data[0].data)
        py_trees.blackboard.Blackboard.set('button_power_reboot', msg.data[1].data)            
        py_trees.blackboard.Blackboard.set('button_manual_driving', msg.data[2].data)            
        py_trees.blackboard.Blackboard.set('emergency_button', msg.data[3].data)            
        py_trees.blackboard.Blackboard.set('button_power_on', msg.data[4].data)            

    button_status_to_BB =  SubscribeTopic(
        topic_name='button/button_action_cmd',
        topic_type=BoolCmdArray,
        on_msg_fn=on_msg_fn_button_status,
        name='button_status_to_BB')        

    def on_msg_batt(msg):
        py_trees.blackboard.Blackboard.set('current_battery_level', msg.percentage) #0.0 ~ 1.0

    battery_state_to_BB = SubscribeTopic(
        topic_name="bms/battery_state",
        topic_type=sensor_msgs.BatteryState,
        on_msg_fn=on_msg_batt,
        name='Battery_state_to_BB'
    )            

    #data[0]: 충전 여부, data[1]: 오토컨택 여부, data[2]: 수동컨택 여부
    def on_msg_charg(msg):
        py_trees.blackboard.Blackboard.set('is_charging', msg.data[0])
        py_trees.blackboard.Blackboard.set('auto_contacted', msg.data[1])
        py_trees.blackboard.Blackboard.set('manual_contacted', msg.data[2]) 


    charging_state_to_BB = SubscribeTopic(
        topic_name="bms/charging_state",
        topic_type= Int8MultiArray,
        on_msg_fn=on_msg_charg,
        name='Battery_state_to_BB'
    )            


    def on_msg_fn_qr_result(msg):
        py_trees.blackboard.Blackboard.set('qr_result', msg.success)

    qr_result_to_BB = SubscribeTopic(
        topic_name='map_to_robot_pose',
        topic_type=Tag,
        on_msg_fn=on_msg_fn_qr_result,
        name='qr_result_to_BB')

    def on_msg_qr(msg):
        py_trees.blackboard.Blackboard.set('qr_status', msg.data)

    qr_state_to_BB = SubscribeTopic(
        topic_name="qr/qr_status",
        topic_type=UInt8,
        on_msg_fn=on_msg_qr,
        name='qr_state_to_BB'
    )  

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


    #tray exception status to BB
    def on_msg_fn_box_exception(msg):
        py_trees.blackboard.Blackboard.set('Tray_'+str(msg.door_states[0].location.y)+'_exception_status', msg.door_states[0].door_state) # 1: 물건 끼임 / 2: 고장 동작 이상

    box_exception_to_BB = SubscribeTopic(
        topic_name='box/box_exception',
        topic_type=BoxStates,
        on_msg_fn=on_msg_fn_box_exception,
        name='box_exception_to_BB')

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
    
    par.add_children([tray_open_status_to_BB, user_input_msgs_to_BB, box_exception_to_BB, error_set_to_BB, button_status_to_BB, emergency_button_info_to_BB, battery_state_to_BB, charging_state_to_BB, qr_result_to_BB, qr_state_to_BB ])

    return par

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


def check_auto_charge(): 

    seq = py_trees.composites.Sequence()

    par = py_trees.composites.Parallel(
            name="check_auto_charge",
            policy=py_trees.common.ParallelPolicy.SuccessOnOne(
            )
        )

    auto_contacted_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'auto_contaced_check',
        check=py_trees.common.ComparisonExpression(
            variable="auto_contacted",
            value=1,
            operator=operator.eq
        )
    )

    auto_contacted_alarm = PublishTopic(
        name='auto_contacted_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='initial_state',
            action='auto_contact',
            action_target='',
            action_result=True
            )
        )

    auto_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'auto_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="is_charging",
            value=1,
            operator=operator.eq
        )
    )

    auto_charging_alarm = PublishTopic(
        name='auto_contacted_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='initial_state',
            action='auto_charging',
            action_target='',
            action_result=True
            )
        )

    none_auto_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'none_auto_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="is_charging",
            value=0,
            operator=operator.eq
        )
    )

    none_auto_charging_alarm = PublishTopic(
        name='none_auto_charging_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='initial_state',
            action='auto_charging',
            action_target='',
            action_result=False
            )
        )



    auto_charging_seq = py_trees.composites.Sequence()
    none_auto_charging_seq = py_trees.composites.Sequence()

    #LED_charging_f = LEDControl(
    #    color=LEDControl.COLOR_WHITE,
    #    position=LEDControl.POSITION_FRONT,
    #    x=1,
    #    y=1,
    #    effect=LEDControl.EFFECT_LED_ON, # on
    #    period_ms=0,
    #    on_ms=0,
    #    repeat_count=0)

    #LED_charging_r = LEDControl(
    #    color=LEDControl.COLOR_WHITE,
    #    position=LEDControl.POSITION_REAR,
    #    x=1,
    #    y=1,
    #    effect=LEDControl.EFFECT_LED_ON, # on
    #    period_ms=0,
    #    on_ms=0,
    #    repeat_count=0)

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
                name='manual_LED_dimming_rear',
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

    seq.add_children([auto_contacted_check, auto_contacted_alarm, par])
    par.add_children([ auto_charging_seq, none_auto_charging_seq]) 
    auto_charging_seq.add_children([auto_charging_check, auto_charging_alarm, LED_charging_f, LED_charging_r])
    none_auto_charging_seq.add_children([none_auto_charging_check, none_auto_charging_alarm])


    return seq


def not_charge_check(): 

    par = py_trees.composites.Parallel(
            name="par",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )

    not_manual_contacted_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'not_manual_contacted_check',
        check=py_trees.common.ComparisonExpression(
            variable="manual_contacted",
            value=0,
            operator=operator.eq
        )
    )


    not_auto_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'not_auto_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="auto_contacted",
            value=0,
            operator=operator.eq
        )
    )

    par.add_children([not_manual_contacted_check, not_auto_charging_check ])

    return par

def tray_close_seq():
    
   
    tray_close1 = BoxClose(position=1, x=1, y=1)
    tray_close2 = BoxClose(position=1, x=1, y=2) 

    tray_close_seq = py_trees.composites.Sequence()
    tray_close_seq1 = py_trees.composites.Sequence()
    tray_close_seq2 = py_trees.composites.Sequence()



    
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
            task_status='init_tree',
            action='tray_closed',
            action_target='all_tray',
            action_result=True
            )
        )
    
    tray_close_seq.add_children([tray_close1, tray1_closed_check, tray_close2, tray2_closed_check, tray_closed_alarm ])

    return tray_close_seq


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



def battery_check():

    par = py_trees.composites.Parallel(
            name="par",
            policy=py_trees.common.ParallelPolicy.SuccessOnOne(
            )
        )
    
    available_seq = py_trees.composites.Sequence()
    unavailable_seq = py_trees.composites.Sequence()


    Battery_available_guard = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'Battery_condition_guard',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=0.2,
            operator= operator.ge
            )
        )

    Battery_unavailable_guard = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'Battery_condition_guard',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=0.2, ############ 0.2
            operator= operator.lt
            )
        )

    low_battery_alarm = PublishTopic(
        name='low_battery_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='low_battery',
            action='low_battery',
            action_target='battery',
            action_result=True
            )
        )
    
    tts_low_battery = TTSPlay(tts_name='charging_fail', play=True, sequence=True)
    
    battery_idle = Idling(name='Idling')

    go_to_low_battery_tree = EnqueueNextService(
        service_name='low_battery_tree', service_version='2.0.0'
    )

    go_to_QR_tree = EnqueueNextService(
        service_name='QR_tree', service_version=''
    )

    par.add_children([available_seq, unavailable_seq])
    available_seq.add_children([Battery_available_guard, go_to_QR_tree])
    unavailable_seq.add_children([Battery_unavailable_guard, low_battery_alarm, go_to_low_battery_tree])

    return par

def check_installation_mode():

    seq = py_trees.composites.Sequence()
    
    check_hri_service = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'check_hri_service',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value="installation_mode",
            operator=operator.eq
        )
    )    

    go_to_installation = EnqueueNextService( service_name='installation_tree', service_version='2.0.0')

    seq.add_children([check_hri_service, go_to_installation])

    return seq



# ** Required ** tree generate function name: create_root
def create_root():

    root_seq = py_trees.composites.Sequence()

    root_par = py_trees.composites.Parallel(
            name="init_tree",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )


    BB_start = BB_init()


    main_par = py_trees.composites.Parallel(
            name="main_par",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )
    
    auto_charge_seq = py_trees.composites.Sequence()
    manual_charge_seq = py_trees.composites.Sequence()
    not_charge_seq = py_trees.composites.Sequence()

    go_to_undocking_tree = EnqueueNextService(
        service_name='undocking_tree', service_version=''
    )    
          
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
    

    #LED_docking_f = LEDControl(
    #    color=LEDControl.COLOR_WHITE,
    #    position=LEDControl.POSITION_FRONT,
    #    x=1,
    #    y=1,
    #    effect=LEDControl.EFFECT_LED_ON, # on
    #    period_ms=0,
    #    on_ms=0,
    #    repeat_count=0)
#
    #LED_docking_r = LEDControl(
    #    color=LEDControl.COLOR_WHITE,
    #    position=LEDControl.POSITION_REAR,
    #    x=1,
    #    y=1,
    #    effect=LEDControl.EFFECT_LED_ON, # on
    #    period_ms=0,
    #    on_ms=0,
    #    repeat_count=0)

    LED_docking_f = PublishTopic(
                name='LED_docking_f',
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

    LED_docking_r = PublishTopic(
                name='LED_docking_r',
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
    

    bb_clear = BBclear()


    go_to_manual_charging_tree = EnqueueNextService(
        service_name='manual_charging_tree', service_version=''
    )

    manual_contacted_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_contaced_check',
        check=py_trees.common.ComparisonExpression(
            variable="manual_contacted",
            value=1,
            operator=operator.eq
        )
    )

    go_to_QR_tree = EnqueueNextService(
        service_name='QR_tree', service_version=''
    )   


    def request_generate_fn_config_msgs():
        req = GetFile.Request()
        req.type = 'config'
        req.version = '1.0.0'
        req.file = 'service_app_config.json'
        return req
    
    def response_fn_config_msgs(response):
        re = response.result
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
        py_trees.blackboard.Blackboard.set('user_input_duration',user_input_duration * 60)    
        py_trees.blackboard.Blackboard.set('charging_map_name',charging_map_name)    
        py_trees.blackboard.Blackboard.set('charging_poi_id',charging_poi_id )    

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

    auth_pw_msgs_to_BB = ServiceCall('data_manager/get_file_decrypt', GetFile, request_generate_fn_admin_pw,
                                         response_fn_admin_pw, name='auth_pw_msgs_to_BB')    

    root_sel = py_trees.composites.Selector('init_tree')

    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
    )

    main_seq = py_trees.composites.Sequence()

    task_available_alarm = PublishTopic(
                            name='task_available_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'task_available',
                                action = 'task_available',
                                action_target = 'init_tree',
                                action_result = True
                                )   
                            )

    root_sel.add_children([root_seq, go_to_ciritcal_error2])
    root_seq.add_children([bb_clear, BB_start, config_msgs_to_BB, auth_pw_msgs_to_BB,  root_par])
    root_par.add_children([msgs_to_BB_parallel(), check_installation_mode(), go_to_minor_error_tree(), check_critical_error(), minor_error_alarm(), emergency_button_check2(), tray_stuck_seq_new(), main_seq])

    main_seq.add_children([task_available_alarm, tray_close_seq(), main_par])
    main_par.add_children([auto_charge_seq, manual_charge_seq, not_charge_seq])
    
    auto_charge_seq.add_children([check_auto_charge(), auto_charging_map_set, LED_docking_f, LED_docking_r, go_to_undocking_tree ])

    manual_charge_seq.add_children([manual_contacted_check, go_to_manual_charging_tree])

    not_charge_seq.add_children([not_charge_check(), battery_check()])

    return root_sel







