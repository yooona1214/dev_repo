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



from ktmw_bt_interfaces.msg import TaskStatus,HaltStatus, StartService, AuthRequest, HRI
from kt_msgs.msg import BoxStates, BoolCmdArray, Password, RobotConf, LEDState, Location, LEDEffect


from ktmw_srvmgr_lib.common import  SetBlackBoard,  PublishTopic, EnqueueNextService, Idling, SubscribeTopic, ServiceCall, compareBBvariableforcorrect, compareBBvariableforincorrect, TTSPlay, BGMPlay 
from ktmw_srvmgr_lib.hardware import BoxClose, LEDControl

from config_manager_msgs.srv import GetPoiRoute
from std_msgs.msg import UInt8, Int8MultiArray

import sensor_msgs.msg as sensor_msgs

from std_srvs.srv import SetBool

from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm


#RobotConfSrv

# ** Required **
SERVICE_NAME = 'idle-tree'
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
        
        for i in range(3):
            py_trees.blackboard.Blackboard.set('current_service_id','')
            py_trees.blackboard.Blackboard.set('current_goal_count', -1)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_service_code','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_task_id','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_tray_id','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_goal_id','')
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_seq',0)
            py_trees.blackboard.Blackboard.set(str(i+1)+'/current_lock_option',0)

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
        py_trees.blackboard.Blackboard.set('flag_for_final_fail_time', False)
        py_trees.blackboard.Blackboard.set('tray_stucked', 0)
        py_trees.blackboard.Blackboard.set('ev_unknown_flag', 0)

        py_trees.blackboard.Blackboard.set('meomchwi', False)

        py_trees.blackboard.Blackboard.set('current_service_id', '')
        py_trees.blackboard.Blackboard.set('current_safe_mode', 0.0)

        py_trees.blackboard.Blackboard.set('goal_index_num', 1)
        py_trees.blackboard.Blackboard.set('route_index_num', 1)

        py_trees.blackboard.Blackboard.set('recharge_battery_level', 0.15) #hard coding
        py_trees.blackboard.Blackboard.set('current_battery_level', 2.0) #hard coding

        py_trees.blackboard.Blackboard.set('qr_result', None)   


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
        py_trees.blackboard.Blackboard.set("tray1_pw",'99999')
        py_trees.blackboard.Blackboard.set("tray2_pw",'99999')

        py_trees.blackboard.Blackboard.set('hri_status', '')   
        py_trees.blackboard.Blackboard.set('hri_tray_id', 0)           

        py_trees.blackboard.Blackboard.set('start_time', 0.0)    
        py_trees.blackboard.Blackboard.set('current_time', 0.0)           
        
        py_trees.blackboard.Blackboard.set('moving_speed', 1.0)     

        py_trees.blackboard.Blackboard.set('tray1', 0)     
        py_trees.blackboard.Blackboard.set('tray2', 0)                     

        py_trees.blackboard.Blackboard.set('current_tts', '')                     
        py_trees.blackboard.Blackboard.set('previous_tree', 'idle_tree')

        py_trees.blackboard.Blackboard.set('ev_zone_result', 0)    
        py_trees.blackboard.Blackboard.set('unknown_zone_result', 0)                    
        py_trees.blackboard.Blackboard.set('keepout_zone_result', 0)  

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

        py_trees.blackboard.Blackboard.set('error_status', False)

        py_trees.blackboard.Blackboard.set('admin_pw_from_ui', '')
        py_trees.blackboard.Blackboard.set('admin_pw_type', '')
        
        py_trees.blackboard.Blackboard.set('manual_lock_flag', True)

        py_trees.blackboard.Blackboard.set('from_fail2', False)

        py_trees.blackboard.Blackboard.set('halt_type', 0)
        py_trees.blackboard.Blackboard.set('halt_result', 0)
        py_trees.blackboard.Blackboard.set('beep_trigger', False)



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

    test = py_trees.behaviours.WaitForBlackboardVariableValue(
                name= 'test',
                check=py_trees.common.ComparisonExpression(
                variable='hri_status',
                value='test',
                operator= operator.eq
            )
        )

    battery_seq.add_children([battery_under_15_check, battery_alarm, go_to_low_battery_tree])
    
    return battery_seq

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
                name='led_start_on_pw_done_f',
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
    
    pw_check_reset = SetBlackBoard(BB_variable = 'pw_check',
                                  BB_value = False)  

    seq.add_children([wait_for_pw_req, par2])
    par2.add_children([seq4, final_seq])
    final_seq.add_children([final_check_pw_correct, auth_checkced_alarm,led_start_on_pw_done_f, led_start_on_pw_done_r, unset_admin_pw_from_ui1, pw_check_reset])
    seq4.add_children([wait_for_pw_req2, par3])
    par3.add_children([seq6, seq7])
    seq6.add_children([pw_correct_check, unset_pw_req1, pw_correct_set1])
    seq7.add_children([pw_incorrect_check,unset_admin_pw_from_ui2, unset_pw_req2, tts_password_fail1, failed_count_alarm, led_start_on_pw_incorrect_f, led_start_on_pw_incorrect_r ])

    return seq

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


def create_root():


    # 최상단
    root_seq = py_trees.composites.Sequence()

    BB_start = BB_init()

    seq_idle_alarm = py_trees.composites.Sequence()

    idle_alarm = PublishTopic(
            name='idle_alarm',
            topic_name='ktmw_bt/task_status',
            topic_type = TaskStatus,
            msg_generate_fn=lambda: TaskStatus(
                service_code=0,
                task_id='',
                goal_id='',
                current_goal_id='',
                tray_id=[0],
                task_status='task_idle',
                action='task_idle',
                action_target='task_idle',
                action_result=True
                )
            )

    # root 선언 - parallel
    root = py_trees.composites.Parallel(
        name="Idle_Tree",
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

    #error msg

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

    #tray exception status to BB
    def on_msg_fn_box_exception(msg):
        py_trees.blackboard.Blackboard.set('Tray_'+str(msg.door_states[0].location.y)+'_exception_status', msg.door_states[0].door_state) # 1: 물건 끼임 / 2: 고장 동작 이상

    box_exception_to_BB = SubscribeTopic(
        topic_name='box/box_exception',
        topic_type=BoxStates,
        on_msg_fn=on_msg_fn_box_exception,
        name='box_exception_to_BB')
    

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

    par_bat_serv = py_trees.composites.Parallel(
        name="par_bat_serv",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_for_batt = py_trees.composites.Sequence("sequence_for_battery")


    Battery_unavailable_guard = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'Battery_condition_guard',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=0.2,
            operator= operator.le
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
    
    battery_idle = Idling(name='Idling')
    
    seq_for_serv = py_trees.composites.Sequence("sequence_for_service")

    Service_requested_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'Service_requested_check',
            check=py_trees.common.ComparisonExpression(
            variable="current_goal_count",
            value=0,
            operator= operator.ge
        )
    )

    Service_requested_check2 = py_trees.behaviours.WaitForBlackboardVariableValue(
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

    tts_play5 = TTSPlay(tts_name='returning_item', play=True, sequence=True)

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


    


    # led_off_1 = LEDControl(
    #     color=LEDControl.COLOR_OFF,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    # led_off_2 = LEDControl(
    #     color=LEDControl.COLOR_OFF,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF,
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)

    led_off_1 = PublishTopic(
                name='led_off_1',
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

    led_off_2 = PublishTopic(
                name='led_off_2',
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
    # led_start_on1 = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_start_on2 = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_ON, #on
    #    period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    led_start_on1 = PublishTopic(
                name='led_start_on1',
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

    led_start_on2 = PublishTopic(
                name='led_start_on2',
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
    
    # 출발버튼 클릭 후 W 로테이션
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

    idle_main_seq = py_trees.composites.Sequence()

    BGM_off_cancel = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)

    pw_check_reset = SetBlackBoard(BB_variable = 'pw_check',
                                  BB_value = False)  


    def on_msg_fn_auth_pw_status(msg):
        py_trees.blackboard.Blackboard.set('admin_pw', msg.update_code_list)
       

    auth_pw_topic_to_BB = SubscribeTopic(
        topic_name='rm_agent/admin_pw_change_alarm_by_robot',
        topic_type=Password,
        on_msg_fn=on_msg_fn_auth_pw_status,
        name='auth_pw_topic_to_BB')       


    def on_msg_fn_config_status(msg):

        py_trees.blackboard.Blackboard.set('moving_speed',msg.moving_speed)
        py_trees.blackboard.Blackboard.set('recharge_battery_level',msg.recharge_battery_lev)  
        py_trees.blackboard.Blackboard.set('standby_duration',msg.standby_duration * 60)  
        py_trees.blackboard.Blackboard.set('standby_duration2',msg.standby_duration * 30)
        py_trees.blackboard.Blackboard.set('user_input_duration',msg.user_input_duration * 60)    
        py_trees.blackboard.Blackboard.set('charging_map_name',msg.charging_loc.map_name)    
        py_trees.blackboard.Blackboard.set('charging_poi_id', msg.charging_loc.poi_id )    


    config_topic_to_BB = SubscribeTopic(
        topic_name='rm_agent/conf_info_request',
        topic_type=RobotConf,
        on_msg_fn=on_msg_fn_config_status,
        name='config_topic_to_BB')   


    root_sel = py_trees.composites.Selector('idle_tree')
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

    tts_battery= TTSPlay(tts_name='charging_fail', play=True, sequence=True)

    par_battery = py_trees.composites.Parallel(
            name="par_battery",
            policy=py_trees.common.ParallelPolicy.SuccessOnOne(
            )
        )
    
    check_battery_lt_20 =  py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_battery_lt_20',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=0.2,
            operator= operator.lt
            )
        )
    
    check_battery_ge_20 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_battery_ge_20',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=0.2,
            operator= operator.ge
            )
        )
    
    seq_battery_lt_20 = py_trees.composites.Sequence()
    seq_battery_ge_20 = py_trees.composites.Sequence()

    check_batt2bb = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_batt2bb',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=1.0,
            operator= operator.le
            )
        )

    check_low_battery = py_trees.composites.Sequence()


    check_battery_lt_20_2 =  py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_battery_lt_20_2',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=0.2,
            operator= operator.lt
            )
        )
    
    check_battery_ge_20_2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'check_battery_ge_20_2',
            check=py_trees.common.ComparisonExpression(
            variable="current_battery_level",
            value=0.2,
            operator= operator.ge
            )
        )
    
    low_battery_alarm2 = PublishTopic(
        name='low_battery_alarm2',
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

    root_sel.add_children([root_seq, go_to_ciritcal_error2])
    root_seq.add_children([BGM_off_cancel, led_off_1,led_off_2, BB_start, root])
    root.add_children([parallel_get_msg, check_low_battery, check_engineer_mode(), check_installation_mode(), check_critical_error(), go_to_minor_error_tree(), check_manual_drive(), check_manual_charge(), emergency_button_check(), battery_under_15(),  minor_error_alarm(), idle_main_seq])

    #Conf_to_BB
    parallel_get_msg.add_children([emergency_button_info_to_BB, user_input_msgs_to_BB, error_set_to_BB, button_status_to_BB, battery_state_to_BB, charging_state_to_BB, admin_pw_from_ui_req_msgs_to_BB, auth_pw_topic_to_BB, config_topic_to_BB, halt_Status_to_BB,current_service_start_to_BB, tray_open_status_to_BB])

    check_low_battery.add_children([check_battery_lt_20_2, low_battery_alarm2, check_battery_ge_20_2])

    idle_main_seq.add_children([check_batt2bb, par_battery, seq_idle_alarm, pw_check_reset, par_bat_serv])
    par_battery.add_children([seq_battery_lt_20, seq_battery_ge_20])
    seq_battery_lt_20.add_children([check_battery_lt_20, seq_for_batt])
    seq_battery_ge_20.add_children([check_battery_ge_20])
    seq_idle_alarm.add_children([idle_alarm,led_start_on1, led_start_on2])

    par_bat_serv.add_children([admin_password_check_seq(),seq_for_serv])

    seq_for_batt.add_children([low_battery_alarm])
    seq_for_serv.add_children([Service_requested_check, route_to_BB, par_route_ready_check, led_service_start, wait_led, TTS_par, go_to_moving])
    par_route_ready_check.add_children([route_ready_check, seq_route_fail_check])
    seq_route_fail_check.add_children([route_fail_check, unset_current_service, unset_route_fail, route_fail_alarm, Service_requested_check2, route_to_BB2])

    TTS_par.add_children([tts_seq_1,tts_seq_2,tts_seq_3,tts_seq_4,tts_seq_5,tts_seq_6])
    tts_seq_1.add_children([tts_check1, tts_play1])
    tts_seq_2.add_children([tts_check2, tts_play2])
    tts_seq_3.add_children([tts_check3, tts_play3])
    tts_seq_4.add_children([tts_check4, tts_play4])
    tts_seq_5.add_children([tts_check5, tts_play5])
    tts_seq_6.add_children([tts_check6, tts_play6])

    return root_sel

