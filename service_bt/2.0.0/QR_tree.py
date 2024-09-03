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

from std_msgs.msg import Bool, UInt8
from ktmw_srvmgr_lib.common import SetBlackBoard,  PublishTopic, EnqueueNextService,  SubscribeTopic, ServiceCall, TTSPlay 

import sensor_msgs.msg as sensor_msgs
from std_msgs.msg import Int8MultiArray
from std_srvs.srv import SetBool
from ktmw_srvmgr_lib.hardware import LEDControl
from hardware_manager_msgs.srv import SetEnable




from kt_msgs.msg import BoolCmdArray, Tag, LEDState, Location, LEDEffect

from ktmw_bt_interfaces.msg import TaskStatus, HRI


from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm

# ** Required **
SERVICE_NAME = 'QR-tree'
# ** Required **
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


        py_trees.blackboard.Blackboard.set('qr_result', None)   


    def update(self):
        return py_trees.common.Status.SUCCESS

def emergency_button_check1():

    seq = py_trees.composites.Sequence()


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
    seq.add_children([emergency_button_check, QR_Node_off, Driving_mode_off ,go_to_emergency_tree])

    return seq

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

    def on_msg_fn_emergency_button(msg):
            py_trees.blackboard.Blackboard.set('emergency_button2', msg.data[0].data) #True: 버튼 눌림 # False: 버튼 해제

    emergency_button_info_to_BB =  SubscribeTopic(
            topic_name='button/button_status',
            topic_type=BoolCmdArray,
            on_msg_fn=on_msg_fn_emergency_button,
            name='emergency_button_info_to_BB')    
    
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


    par.add_children([user_input_msgs_to_BB, error_set_to_BB, emergency_button_info_to_BB, button_status_to_BB, qr_result_to_BB, qr_state_to_BB, charging_state_to_BB ])


    return par

def QR_recognize():

    def request_generate_man_d_node():
        request = SetEnable.Request()
        request.uuid = 0
        request.data = True
        return request
    
    def response_man_d(response):

        py_trees.blackboard.Blackboard.set('manual_drive_success', response.success)
        print(response.success)

    manual_drive_on = ServiceCall(
        service_name='hardware_manager/button/manual_driving_enable',  #manual_driving_enable
        service_type= SetEnable,
        request_generate_fn=request_generate_man_d_node,
        response_fn= response_man_d, name='manual_drive_on'

    )

    manual_drive_on_alarm = PublishTopic(
                            name='manual_drive_on_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'initial_state',
                                action = 'manual_driving_mode',
                                action_target = 'manual_driving_mode',
                                action_result = True
                                )   
                            )    


    def request_generate_run_qr_node():
        request = SetBool.Request()
        request.data = True
        return request
    def response_QR_Node(response):
        print(response.success)

    Run_QR_Node = ServiceCall(
        service_name='qr/scan_enable',
        service_type= SetBool,
        request_generate_fn=request_generate_run_qr_node,
        response_fn= response_QR_Node, name='Run_QR_Node'

    )

    Driving_mode_set = PublishTopic(
        name='Driving_mode_set',
        topic_name='qr_pose_out_mode',
        topic_type = UInt8,
        msg_generate_fn=lambda: UInt8(
            data=2
            )
        )
    
    qr_start_alarm = PublishTopic(
                            name='qr_start_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'initial_state',
                                action = 'qr_node_start',
                                action_target = 'qr_node',
                                action_result = True
                                )   
                            )
    
    qr_result_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'qr_result_check',
                check=py_trees.common.ComparisonExpression(
                variable='qr_result',
                value=True,
                operator= operator.eq
            )
        )
    
    qr_success_alarm = PublishTopic(
                            name='qr_success_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'initial_state',
                                action = 'qr_localization',
                                action_target = 'qr_code',
                                action_result = True
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
        name='Driving_mode_set',
        topic_name='qr_pose_out_mode',
        topic_type = UInt8,
        msg_generate_fn=lambda: UInt8(
            data=0
            )
        )

    seq_qr_rec_success = py_trees.composites.Sequence()

    par_qr_status = py_trees.composites.Parallel(
        name="par_qr_status",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq_qr_rec_success],
            synchronise=False)
    )

    seq_qr_rec_start = py_trees.composites.Sequence()
    seq_qr_rec_fail = py_trees.composites.Sequence()

    
    qr_rec_start_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'qr_rec_start_check',
                check=py_trees.common.ComparisonExpression(
                variable='qr_status',
                value=1,
                operator= operator.eq
            )
        )

    qr_rec_success_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'qr_rec_success_check',
                check=py_trees.common.ComparisonExpression(
                variable='qr_status',
                value=2,
                operator= operator.eq
            )
        )
    
    qr_rec_success_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'qr_rec_success_check',
                check=py_trees.common.ComparisonExpression(
                variable='qr_status',
                value=2,
                operator= operator.eq
            )
        )

    qr_rec_fail_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'qr_rec_fail_check',
                check=py_trees.common.ComparisonExpression(
                variable='qr_status',
                value=3,
                operator= operator.eq
            )
        )
    
    qr_rec_fail_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'qr_rec_fail_check',
                check=py_trees.common.ComparisonExpression(
                variable='qr_status',
                value=3,
                operator= operator.eq
            )
        )
    
    qr_rec_start_alarm = PublishTopic(
                            name='qr_rec_start_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'initial_state',
                                action = 'qr_rec_start',
                                action_target = 'qr_code',
                                action_result = True
                                )   
                            )

    qr_rec_success_alarm = PublishTopic(
                            name='qr_rec_success_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'initial_state',
                                action = 'qr_success',
                                action_target = 'qr_code',
                                action_result = True
                                )   
                            )

    qr_rec_fail_alarm = PublishTopic(
                            name='qr_rec_fail_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'initial_state',
                                action = 'qr_fail',
                                action_target = 'qr_code',
                                action_result = True
                                )   
                            )

    # led_qr_rec_start_f = LEDControl(
    #     color=LEDControl.COLOR_BLUE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)

    # led_qr_rec_start_r = LEDControl(
    #     color=LEDControl.COLOR_BLUE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)

    led_qr_rec_start_f = PublishTopic(
                name='led_qr_rec_start_f',
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
    
    led_qr_rec_start_r = PublishTopic(
                name='led_qr_rec_start_r',
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
    
    tts_qr_ready1= TTSPlay(tts_name='qr_ready', play=True, sequence=True)
    tts_qr_ready2= TTSPlay(tts_name='qr_ready', play=True, sequence=True)
    tts_qr_recognize= TTSPlay(tts_name='qr_recognize', play=True, sequence=True)
    

    def request_generate_man_d_node_off():
        request = SetEnable.Request()
        request.uuid = 0
        request.data = False
        return request
    
    def response_man_d_off(response):

        py_trees.blackboard.Blackboard.set('manual_drive_success', response.success)
        print(response.success)

    manual_drive_off = ServiceCall(
        service_name='hardware_manager/button/manual_driving_enable',
        service_type= SetEnable,
        request_generate_fn=request_generate_man_d_node_off,
        response_fn= response_man_d_off, name='manual_drive_off'
    )

    manual_driving_off_alarm = PublishTopic(
                            name='manual_driving_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'initial_state',
                                action = 'manual_driving_mode',
                                action_target = 'manual_driving_mode',
                                action_result = False
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

    seq_qr = py_trees.composites.Sequence()

    go_to_idle_tree = EnqueueNextService(service_name='idle_tree', service_version='2.0.0')

    timer_3s = py_trees.timers.Timer("timer_3s", duration=3.0)

    par_success_or_fail = py_trees.composites.Parallel(
        name="par_success_or_fail",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )




    seq_qr.add_children([manual_drive_on, manual_drive_on_alarm, Run_QR_Node, Driving_mode_set, qr_start_alarm, timer_3s, manual_LED_dimming_front, manual_LED_dimming_rear, tts_qr_ready1, par_qr_status, qr_result_check, qr_success_alarm, QR_Node_off, Driving_mode_off, manual_drive_off, manual_driving_off_alarm, go_to_idle_tree])
    par_qr_status.add_children([seq_qr_rec_start, seq_qr_rec_fail, seq_qr_rec_success])
    seq_qr_rec_start.add_children([qr_rec_start_check, tts_qr_recognize, qr_rec_start_alarm, led_qr_rec_start_f, led_qr_rec_start_r, par_success_or_fail])
    par_success_or_fail.add_children([qr_rec_fail_check2, qr_rec_success_check2 ])
    seq_qr_rec_fail.add_children([qr_rec_fail_check, qr_rec_fail_alarm, led_qr_rec_fail_f, led_qr_rec_fail_r])
    seq_qr_rec_success.add_children([qr_rec_success_check, qr_rec_success_alarm])
    return seq_qr

def check_auto_charge(): 

    seq = py_trees.composites.Sequence()


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

    go_to_init_tree = EnqueueNextService(service_name='init_tree', service_version='2.0.0')


    seq.add_children([auto_contacted_check, auto_contacted_alarm, go_to_init_tree])
 
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

def create_root():
  
    root_par = py_trees.composites.Parallel(
        name="par_charging_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_manual_charging = py_trees.composites.Sequence()

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

    
    root_sel = py_trees.composites.Selector('QR_tree')
    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
    )

    root_seq = py_trees.composites.Sequence()
    bb_init = BB_init()
    
    root_sel.add_children([root_seq, go_to_ciritcal_error2])
    root_seq.add_children([bb_init, root_par])
    root_par.add_children([check_installation_mode(), check_critical_error(), go_to_minor_error_tree(), msgs_to_BB_parallel(), minor_error_alarm(), emergency_button_check1(), QR_recognize(), check_auto_charge(), seq_manual_charging])
    seq_manual_charging.add_children([manual_contacted_check, QR_Node_off, Driving_mode_off, go_to_manual_charging_tree])


    return root_sel



