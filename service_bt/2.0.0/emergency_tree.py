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

from ktmw_srvmgr_lib.common import  PublishTopic,  Idling, SubscribeTopic,  TTSPlay, BGMPlay
from ktmw_srvmgr_lib.common import Idling, EnqueueNextService
from ktmw_srvmgr_lib.hardware import LEDControl

from kt_msgs.msg import BoolCmdArray, LEDState, Location, LEDEffect

from ktmw_bt_interfaces.msg import TaskStatus

# ** Required **
SERVICE_NAME = 'emergency-tree'
# ** Required **
SERVICE_VERSION = '0.1.0'

def create_root():
  
    root_par = py_trees.composites.Parallel(
        name="emergency_tree",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )        
    )

    seq_msg_to_BB = py_trees.composites.Sequence()
    seq_main = py_trees.composites.Sequence()

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

    # led_start_on_Emergency_front = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)
    
    # led_start_on_Emergency_rear = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_FLASH,
    #     period_ms=1000,
    #     on_ms=500,
    #     repeat_count=0)

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

    # led_start_off_Emergency_front = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_start_off_Emergency_rear = LEDControl(
    #     color=LEDControl.COLOR_RED,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

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
    
    Idling_emergency = Idling(name='Idling_emergency')
    go_to_init_tree = EnqueueNextService(
        service_name='init_tree', service_version='2.0.0'
    )

    TTS_emo = TTSPlay(tts_name='emo_start', play=True, sequence=False)

    BGM_off_cancel = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)

    # Emergency_tree: This tree is called when emergency button is pushed

    root_par.add_children([seq_msg_to_BB, seq_main])
    seq_msg_to_BB.add_children([emergency_button_info_to_BB])
    seq_main.add_children([emergency_button_push_alarm, BGM_off_cancel, TTS_emo, led_start_on_Emergency_front, led_start_on_Emergency_rear, emergency_false_check, emergency_button_off_alarm, led_start_off_Emergency_front, led_start_off_Emergency_rear, go_to_init_tree])


    return root_par

