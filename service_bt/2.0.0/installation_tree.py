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
from ktmw_srvmgr_lib.common import SetBlackBoard,  PublishTopic, EnqueueNextService, SubscribeTopic, ServiceCall, Idling, TTSPlay
from kt_msgs.msg import BoolCmdArray, Tag, LEDState, Location, LEDEffect
from ktmw_bt_interfaces.msg import TaskStatus, HRI
import py_trees.decorators
import sensor_msgs.msg as sensor_msgs
from std_msgs.msg import Int8MultiArray





# ** Required **
SERVICE_NAME = 'installation-tree'
# ** Required **s
SERVICE_VERSION = '0.1.0'

# 1. 3가지 토픽 블랙보드 초기화
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
        py_trees.blackboard.Blackboard.set('button_manual_driving', None)
        py_trees.blackboard.Blackboard.set('emergency_button', None)
        py_trees.blackboard.Blackboard.set('emergency_button2', None)
        py_trees.blackboard.Blackboard.set('hri_status', '')
        py_trees.blackboard.Blackboard.set('is_charging', '')
        py_trees.blackboard.Blackboard.set('auto_contacted', '')
        py_trees.blackboard.Blackboard.set('manual_contacted', '')   
        py_trees.blackboard.Blackboard.set('previous_tree', 'installation_tree')   
        py_trees.blackboard.Blackboard.set('service_code', '')
        py_trees.blackboard.Blackboard.set('qr_result', None)   


    def update(self):
        return py_trees.common.Status.SUCCESS

# 2. 각 토픽 수신해서 블랙보드에 set
def msgs_to_BB_parallel():

    par = py_trees.composites.Parallel(
        name="Msgs_to_BB_parallel",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )        
    )

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
    
    par.add_children([charging_state_to_BB, battery_state_to_BB, user_input_msgs_to_BB, button_status_to_BB, emergency_button_info_to_BB])

    return par

# 3.on/off일 때마다 task_status 알람, TTS, LED
#region Section 1: 수동운전버튼 - button/button_action_cmd
def check_manual_drive(): 

    par_manual = py_trees.composites.Parallel(
            name="par_manual",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )
    seq_manual_on = py_trees.composites.Sequence()
    seq_manual_off = py_trees.composites.Sequence()

    
    manual_drive_button_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_drive_button_check',
        check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=True,
            operator=operator.eq
        )
    )
    
    manual_drive_button_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_drive_button_check2',
        check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=True,
            operator=operator.eq
        )
    )

    idling = Idling()

    manual_driving_alarm = PublishTopic(
                            name='manual_driving_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'manual_manual_driving',
                                action = 'manual_manual_driving_mode',
                                action_target = 'manual_manual_driving_mode',
                                action_result = True
                                )   
                            )
    
    tts_manualdriving_on= TTSPlay(tts_name='manualdriving_start', play=True, sequence=False)

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
    
    manual_driving_off_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'manual_driving_off_check',
            check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=False,
            operator= operator.eq
            )
        )
    
    manual_driving_off_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'manual_driving_off_check2',
            check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=False,
            operator= operator.eq
            )
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
                                task_status = 'manual_manual_driving',
                                action = 'manual_manual_driving_mode',
                                action_target = 'manual_manual_driving_mode',
                                action_result = False
                                )   
                            )    
    tts_manualdriving_off= TTSPlay(tts_name='manualdriving_end', play=True, sequence=False)
    led_manual_driving_off_f = PublishTopic(
                name='led_manual_driving_off_f',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    led_manual_driving_off_r = PublishTopic(
                name='led_manual_driving_off_r',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=0,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )  


    
    par_manual.add_children([seq_manual_on, seq_manual_off])
    seq_manual_on.add_children([manual_drive_button_check, manual_driving_alarm, manual_LED_dimming_front, manual_LED_dimming_rear, manual_driving_off_check2])
    seq_manual_off.add_children([manual_driving_off_check, manual_driving_off_alarm, led_manual_driving_off_f, led_manual_driving_off_r, manual_drive_button_check2])

    return par_manual


#endregion

#region Section 2: 비상정지버튼 - button/button_action_cmd & button_status
##이벤트 트리거링 버튼상태 체크, 서비스 중 비상정지 눌림 확인 용도

def check_emergency_button():

    seq_emergency = py_trees.composites.Sequence()
    seq_emergency_on = py_trees.composites.Sequence()
    seq_emergency_off = py_trees.composites.Sequence()

    par_emergency_button_check = py_trees.composites.Parallel(
        name="par_emergency_button_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )

    button_action_cmd_on = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'button_action_cmd_on',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button",
            value=True,
            operator=operator.eq
        )
    )
    button_status_on = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'button_status_on',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button2",
            value=True,
            operator=operator.eq
        )
    )

    par_emergency_button_check2 = py_trees.composites.Parallel(
        name="par_emergency_button_check2",
        policy=py_trees.common.ParallelPolicy.SuccessOnOne(
        )
    )
    
    button_action_cmd_on2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'button_action_cmd_on2',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button",
            value=True,
            operator=operator.eq
        )
    )
    button_status_on2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'button_status_on2',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button2",
            value=True,
            operator=operator.eq
        )
    )

    emergency_button_push_alarm = PublishTopic(
        name='emergency_button_push_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='emergency',
            action='emergency',
            action_target='',
            action_result=True
            )
        )
    TTS_emo = TTSPlay(tts_name='emo_start', play=True, sequence=False)

    led_start_on_Emergency_front = PublishTopic(
                name='led_start_on_Emergency_front',
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
    led_start_on_Emergency_rear = PublishTopic(
                name='led_start_on_Emergency_rear',
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
    
    emergency_false_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'emergency_false_check',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button2",
            value=False,
            operator=operator.eq
        )
    )    

    
    emergency_false_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'emergency_false_check2',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button2",
            value=False,
            operator=operator.eq
        )
    )    

    emergency_button_off_alarm = PublishTopic(
        name='emergency_button_off_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='emergency',
            action='emergency',
            action_target='',
            action_result=False
            )
        )   

    led_start_off_Emergency_front = PublishTopic(
                name='led_start_off_Emergency_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )     

    led_start_off_Emergency_rear = PublishTopic(
                name='led_start_off_Emergency_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )    
    Idling_emergency = Idling(name='Idling_emergency')

    seq_emergency.add_children([seq_emergency_on, seq_emergency_off])

    seq_emergency_on.add_children([par_emergency_button_check, emergency_button_push_alarm, led_start_on_Emergency_front, led_start_on_Emergency_rear, emergency_false_check2])
    par_emergency_button_check.add_children([button_action_cmd_on, button_status_on])

    seq_emergency_off.add_children([emergency_false_check, emergency_button_off_alarm, led_start_off_Emergency_front, led_start_off_Emergency_rear, par_emergency_button_check2])
    par_emergency_button_check2.add_children([button_action_cmd_on2, button_status_on2])

    return seq_emergency

def check_emergency_button_off():

    seq = py_trees.composites.Sequence()

    emergency_false_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'emergency_false_check',
        check=py_trees.common.ComparisonExpression(
            variable="emergency_button2",
            value=False,
            operator=operator.eq
        )
    )    

    emergency_button_off_alarm = PublishTopic(
        name='emergency_button_off_alarm',
        topic_name='ktmw_bt/task_status',
        topic_type = TaskStatus,
        msg_generate_fn=lambda: TaskStatus(
            service_code=0,
            task_id='',
            goal_id='',
            current_goal_id='',
            tray_id=[0],
            task_status='emergency',
            action='emergency',
            action_target='',
            action_result=False
            )
        )   

    led_start_off_Emergency_front = PublishTopic(
                name='led_start_off_Emergency_front',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=1, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )     

    led_start_off_Emergency_rear = PublishTopic(
                name='led_start_off_Emergency_rear',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=0, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )    
    Idling_emergency = Idling(name='Idling_emergency')

    seq.add_children([emergency_false_check, emergency_button_off_alarm, led_start_off_Emergency_front, led_start_off_Emergency_rear, Idling_emergency])
    return seq

#endregion

def check_service_mode():

    seq = py_trees.composites.Sequence()
    
    check_hri_service = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'check_hri_service',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value="service_mode",
            operator=operator.eq
        )
    )    

    go_to_idle = EnqueueNextService( service_name='idle_tree', service_version='2.0.0')

    seq.add_children([check_hri_service, go_to_idle])

    return seq

def check_engineer_mode():

    seq = py_trees.composites.Sequence()
    
    check_hri_service = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'check_hri_service',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value="engineer_mode",
            operator=operator.eq
        )
    )    

    go_to_engineer_mode = EnqueueNextService( service_name='inner_peace_tree', service_version='2.0.0')

    seq.add_children([check_hri_service, go_to_engineer_mode])

    return seq


def check_manual_charge():

    par = py_trees.composites.Parallel(
        name="par_charging_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        ))

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
            task_status='initial_state',
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

    none_manual_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'none_manual_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="is_charging",
            value=0,
            operator=operator.eq
        )
    )

    none_manual_charging_alarm = PublishTopic(
        name='none_manual_charging_alarm',
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
            action_result=False
            )
        )
    
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
    
    LED_off_f = PublishTopic(
                name='LED_off_f',
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

    LED_off_r = PublishTopic(
                name='LED_off_r',
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
    
    LED_off_f1 = PublishTopic(
                name='LED_off_f',
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

    LED_off_r1 = PublishTopic(
                name='LED_off_r',
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
    
    LED_off_f2 = PublishTopic(
                name='LED_off_f',
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

    LED_off_r2 = PublishTopic(
                name='LED_off_r',
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
    

    full_check = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'full_check',
                check=py_trees.common.ComparisonExpression(
                variable='current_battery_level',
                value=1.0,
                operator= operator.eq
            )
        )
    

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
                name='LED_full_r',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=0, g=255, b=0),
                    effect=1,
                    period=1000,
                    on_ms=500,
                    repeat_count=0
                    )   
                )  
    
    Idling_full = Idling()


    seq_for_full = py_trees.composites.Sequence()


    manual_charging_seq = py_trees.composites.Sequence()
    none_manual_charging_seq = py_trees.composites.Sequence()

    seq_not_contacted_check = py_trees.composites.Sequence()


    par_charging_check = py_trees.composites.Parallel(
        name="par_charging_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[seq_not_contacted_check],
            synchronise=False
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

    par_none_manual_charging_and_15 = py_trees.composites.Parallel(
        name="par_none_manual_charging_and_15",
        policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[manual_charging_check_again],
            synchronise=False
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
            task_status='initial_state',
            action='manual_contact',
            action_target='',
            action_result=False
            )
        )

    par.add_children([seq, seq_for_full])
    
    seq_for_full.add_children([full_check, LED_full_f, LED_full_r, Idling_full])

    seq.add_children([manual_contacted_check, manual_contacted_alarm, LED_off_f, LED_off_r, par_charging_check])
    
    par_charging_check.add_children([ manual_charging_seq, none_manual_charging_seq, seq_not_contacted_check]) 

    manual_charging_seq.add_children([manual_charging_check, manual_charging_alarm, LED_charging_f, LED_charging_r, none_manual_charging_check_again])

    none_manual_charging_seq.add_children([none_manual_charging_check, LED_off_f1, LED_off_r1, none_manual_charging_alarm, par_none_manual_charging_and_15])
    par_none_manual_charging_and_15.add_children([battery_under_15(), manual_charging_check_again])
    seq_not_contacted_check.add_children([not_contacted_check, LED_off_f2, LED_off_r2, manual_uncontact_alarm])


    return par


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

    low_battery_idling = Idling()

    battery_seq.add_children([battery_under_15_check, battery_alarm, low_battery_idling])
    
    return battery_seq


def create_root():

    root_seq = py_trees.composites.Sequence(name='')
    BB_start = BB_init()
    # bb_clear = BBclear()
    root_par = py_trees.composites.Parallel(
            name="root_par",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )
    

    root_sel = py_trees.composites.Selector('installation_tree')
    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
    )

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
                                action_target = 'installation_tree',
                                action_result = True
                                )   
                            )

    
    root_sel.add_children([root_seq, go_to_ciritcal_error2])
    root_seq.add_children([BB_start, task_available_alarm, root_par])

    root_par.add_children([msgs_to_BB_parallel(), check_manual_drive(), check_emergency_button(), check_manual_charge(), check_engineer_mode()])


    return root_sel
