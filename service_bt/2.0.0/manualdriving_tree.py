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

from ktmw_srvmgr_lib.common import EnqueueNextService,ServiceCall,SubscribeTopic,PublishTopic, TTSPlay, Idling, BGMPlay, SetBlackBoard
from kt_msgs.msg import  BoxStates, LEDState, Location, LEDEffect
from ktmw_bt_interfaces.msg import *
from ktmw_bt_interfaces.srv import *
from kt_msgs.msg import Tag
from config_manager_msgs.srv import GetPoiRoute

from ktmw_bt_interfaces.msg import TaskStatus
                                    


import sensor_msgs.msg as sensor_msgs

from ktmw_srvmgr_lib.hardware import BoxCtrl, LEDControl
                                

from std_srvs.srv import SetBool
from std_msgs.msg import UInt8, Int8MultiArray


from kt_msgs.msg import BoolCmdArray
from alarm_manager_msgs.msg import SetAlarm, NotifyAlarm


# ** Required **
SERVICE_NAME = 'manualdriving-tree'
# ** Required **
SERVICE_VERSION = '0.1.0'

class unset_current_route(py_trees.behaviour.Behaviour):
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
            py_trees.blackboard.Blackboard.set('route_index_num',1)
            py_trees.blackboard.Blackboard.set('poi_success_check',None)

            for i in range(a):
                py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/waypoint_poi','')
                py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_name','')
                py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/zone','')
                py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/floor','')
                py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/is_ev',False)
                py_trees.blackboard.Blackboard.set("r"+str(i+1)+'/map_change',False)
            return py_trees.common.Status.SUCCESS
                

# initialize BB params to check BBwait
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

        py_trees.blackboard.Blackboard.set('qr2map_flag', False)
        py_trees.blackboard.Blackboard.set('map_available_flag', False)
        py_trees.blackboard.Blackboard.set('manual_button', '')
        py_trees.blackboard.Blackboard.set('hri_status', '') #string
        py_trees.blackboard.Blackboard.set('hri_tray_id', 0) #string
        #py_trees.blackboard.Blackboard.set('previous_tree', 'manualdriving_tree') 수동운전 트리에서는 previous tree set하면 안됨.
        py_trees.blackboard.Blackboard.set('Tray_1_exception_status', 9)
        py_trees.blackboard.Blackboard.set('Tray_2_exception_status', 9)
        py_trees.blackboard.Blackboard.set('Tray_1_open_status', 1)
        py_trees.blackboard.Blackboard.set('Tray_2_open_status', 1)
    def update(self):
        return py_trees.common.Status.SUCCESS

class ev_unknown_check(py_trees.behaviour.Behaviour):
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
        self.bb1 = py_trees.blackboard.Blackboard.get('ev_zone_result')
        self.bb2 = py_trees.blackboard.Blackboard.get('unknown_zone_result')

        if self.bb1 == 1 or self.bb2 == 1:
            py_trees.blackboard.Blackboard.set('ev_unknown_flag', 1)
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING  
        
class just_manual_off(py_trees.behaviour.Behaviour):
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
        self.bb1 = py_trees.blackboard.Blackboard.get('ev_unknown_flag')
        self.bb2 = py_trees.blackboard.Blackboard.get('keepout_zone_result')

        if self.bb1 == 0 and self.bb2 == 0:
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING  

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





def generate_route():

    seq = py_trees.composites.Sequence()
    # par_route_ready_check에서 사용하는 함수 정의
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

    # seq에서 사용하는 함수 정의
    UnsetCurrentRoute = unset_current_route()
    # generate_route에서 사용하는 함수 정의
    
    #경로 to BB -> TBD
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

    route_to_BB = ServiceCall(
        service_name='configuration_manager/get_poi_route',
        service_type=GetPoiRoute,
        request_generate_fn=request_generate_fn_poi2bb,
        response_fn=response_fn_poi2bb,
        name='route_to_BB'
    )

    route_to_BB2 = ServiceCall(
    service_name='configuration_manager/get_poi_route',
    service_type=GetPoiRoute,
    request_generate_fn=request_generate_fn_poi2bb,
    response_fn=response_fn_poi2bb,
    name='route_to_BB2'
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
    #     repeat_count=1
    # )

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
                    on_ms=500,
                    repeat_count=1
                    )   
                )  

    wait_led= py_trees.timers.Timer("led_show", duration=0.75)

    

    # seq_route_fail_check에서 사용하는 함수 정의
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
    
    unset_route_fail = SetBlackBoard(BB_variable='poi_success_check', BB_value='')

    

    seq.add_children([UnsetCurrentRoute, route_to_BB, par_route_ready_check, led_service_start, wait_led])
    par_route_ready_check.add_children([route_ready_check, seq_route_fail_check])
    seq_route_fail_check.add_children([route_fail_check, route_fail_alarm, unset_route_fail, route_to_BB2])
    
    return seq

def generate_route_for_undocking():

    seq = py_trees.composites.Sequence()
    # par_route_ready_check에서 사용하는 함수 정의
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

    # seq에서 사용하는 함수 정의
    UnsetCurrentRoute = unset_current_route()
    # generate_route에서 사용하는 함수 정의
    #경로 to BB -> TBD
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

    # 출발버튼 클릭 후 W 로테이션
    # led_service_start = LEDControl(
    #     color=LEDControl.COLOR_WHITE,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_REVERSE_SEQUENTIAL_LED_OFF, # 로테이션
    #     period_ms=2500,
    #     on_ms=0,
    #     repeat_count=1
    # )

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

    

    # seq_route_fail_check에서 사용하는 함수 정의
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
    
    unset_route_fail = SetBlackBoard(BB_variable='poi_success_check', BB_value='')

    route_to_BB2 = ServiceCall(
    service_name='configuration_manager/get_poi_route',
    service_type=GetPoiRoute,
    request_generate_fn=request_generate_fn_poi2bb,
    response_fn=response_fn_poi2bb,
    name='route_to_BB2'
    )

    seq.add_children([UnsetCurrentRoute, route_to_BB, par_route_ready_check, led_service_start, wait_led])
    par_route_ready_check.add_children([route_ready_check, seq_route_fail_check])
    seq_route_fail_check.add_children([route_fail_check, route_fail_alarm, unset_route_fail, route_to_BB2])
    
    return seq



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

    go_to_manualcharging = EnqueueNextService(
        service_name='manual_charging_tree', service_version='2.0.0'
    )

    seq.add_children([manual_contacted_check, go_to_manualcharging ])

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

    def on_msg_fn_qr_result(msg):
        py_trees.blackboard.Blackboard.set('qr_result', msg.success)

    qr_result_to_BB = SubscribeTopic(
        topic_name='map_to_robot_pose',
        topic_type=Tag,
        on_msg_fn=on_msg_fn_qr_result,
        name='qr_result_to_BB')

    def on_msg_fn_zone_check(msg):
        py_trees.blackboard.Blackboard.set('ev_zone_result', msg.data[0])
        py_trees.blackboard.Blackboard.set('unknown_zone_result', msg.data[1])
        py_trees.blackboard.Blackboard.set('keepout_zone_result', msg.data[2])

    zone_check_to_BB = SubscribeTopic(
        topic_name='nav/zone_check',
        topic_type=Int8MultiArray,
        on_msg_fn=on_msg_fn_zone_check,
        name='zone_check_to_BB')


    def on_msg_qr(msg):
        py_trees.blackboard.Blackboard.set('qr_status', msg.data)

    qr_state_to_BB = SubscribeTopic(
        topic_name="qr/qr_status",
        topic_type=UInt8,
        on_msg_fn=on_msg_qr,
        name='qr_state_to_BB'
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

    par.add_children([user_input_msgs_to_BB, box_exception_to_BB, error_set_to_BB, emergency_button_info_to_BB, button_status_to_BB, tray_open_status_to_BB, qr_result_to_BB, zone_check_to_BB, battery_state_to_BB, qr_state_to_BB, charging_state_to_BB])

    return par

def QR_recognize():

    seq = py_trees.composites.Sequence()

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
                                task_status = 'manual_driving',
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
                                task_status = 'manual_driving',
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
    

    qr_rec_fail_check = py_trees.behaviours.WaitForBlackboardVariableValue(
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
                                task_status = 'manual_driving',
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
                                task_status = 'manual_driving',
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
                                task_status = 'manual_driving',
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
    
    tts_qr_ready2= TTSPlay(tts_name='qr_ready', play=True, sequence=True)
    tts_qr_recognize= TTSPlay(tts_name='qr_recognize', play=True, sequence=True)

    unset_qr = py_trees.behaviours.UnsetBlackboardVariable('qr_status')
    unset_qr2 = py_trees.behaviours.UnsetBlackboardVariable('qr_status')
    unset_qr3 = py_trees.behaviours.UnsetBlackboardVariable('qr_status')

    tts_manualdriving_off= TTSPlay(tts_name='manualdriving_end', play=True, sequence=False)


    seq.add_children([Run_QR_Node, Driving_mode_set, qr_start_alarm, par_qr_status, qr_result_check, qr_success_alarm, QR_Node_off, Driving_mode_off])
    par_qr_status.add_children([seq_qr_rec_start, seq_qr_rec_fail, seq_qr_rec_success])
    seq_qr_rec_start.add_children([qr_rec_start_check, qr_rec_start_alarm, led_qr_rec_start_f, led_qr_rec_start_r, unset_qr])
    seq_qr_rec_fail.add_children([qr_rec_fail_check, qr_rec_fail_alarm, tts_qr_ready2, led_qr_rec_fail_f, led_qr_rec_fail_r, unset_qr2])
    seq_qr_rec_success.add_children([qr_rec_success_check, qr_rec_success_alarm, tts_qr_recognize, unset_qr3])

    return seq

def next_step():

    par = py_trees.composites.Parallel(
        name = "par",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_charging = py_trees.composites.Sequence()
    seq_ev = py_trees.composites.Sequence()
    seq_idle = py_trees.composites.Sequence()
    seq_moving = py_trees.composites.Sequence()
    seq_tray_cancel1 = py_trees.composites.Sequence()
    seq_tray_cancel2 = py_trees.composites.Sequence()
    seq_tray_fail1 = py_trees.composites.Sequence()
    seq_tray_fail2 = py_trees.composites.Sequence()
    seq_tray_load1 = py_trees.composites.Sequence()
    seq_tray_load2 = py_trees.composites.Sequence()
    seq_tray_unload1 = py_trees.composites.Sequence()
    seq_tray_unload2 = py_trees.composites.Sequence()
    seq_bb_clear = py_trees.composites.Sequence()

    bbclear_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'bbclear_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="BB_clear",
            operator= operator.eq
            )
        )
    
    go_to_bbclear = EnqueueNextService(
        service_name='BB_clear', service_version='2.0.0'
    )

    charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'charging_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="charging_tree",
            operator= operator.eq
            )
        )
    
    go_to_charging_tree = EnqueueNextService(
        service_name='manual_charging_tree2', service_version='2.0.0'
    )

    ev_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'ev_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="ev_tree",
            operator= operator.eq
            )
        )
    
    go_to_ev_tree = EnqueueNextService(
        service_name='moving_tree', service_version='2.0.0'
    )

    idle_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'idle_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="idle_tree",
            operator= operator.eq
            )
        )
    
    go_to_idle_tree = EnqueueNextService(
        service_name='idle_tree', service_version='2.0.0'
    )

    moving_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'moving_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="moving_tree",
            operator= operator.eq
            )
        )
    
    




    go_to_moving_tree = EnqueueNextService(
        service_name='moving_tree', service_version='2.0.0'
    )

    tray_cancel1_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_cancel1_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_cancel1",
            operator= operator.eq
            )
        )
    
    go_to_tray_cancel1_tree = EnqueueNextService(
        service_name='tray_cancel1', service_version='2.0.0'
    )

    tray_cancel2_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_cancel2_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_cancel2",
            operator= operator.eq
            )
        )
    
    go_to_tray_cancel2_tree = EnqueueNextService(
        service_name='tray_cancel2', service_version='2.0.0'
    )

    tray_fail1_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_fail1_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_fail1",
            operator= operator.eq
            )
        )
    
    go_to_tray_fail1_tree = EnqueueNextService(
        service_name='tray_fail1', service_version='2.0.0'
    )

    tray_fail2_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_fail2_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_fail2",
            operator= operator.eq
            )
        )
    
    go_to_tray_fail2_tree = EnqueueNextService(
        service_name='tray_fail2', service_version='2.0.0'
    )

    tray_load1_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_load1_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_load1",
            operator= operator.eq
            )
        )
    
    go_to_tray_load1_tree = EnqueueNextService(
        service_name='tray_load1', service_version='2.0.0'
    )

    tray_load2_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_load2_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_load2",
            operator= operator.eq
            )
        )
    
    go_to_tray_load2_tree = EnqueueNextService(
        service_name='tray_load2', service_version='2.0.0'
    )

    tray_unload1_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_unload1_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_unload1",
            operator= operator.eq
            )
        )
    
    go_to_tray_unload1_tree = EnqueueNextService(
        service_name='tray_unload1', service_version='2.0.0'
    )

    tray_unload2_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'tray_unload2_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="tray_unload2",
            operator= operator.eq
            )
        )
    
    go_to_tray_unload2_tree = EnqueueNextService(
        service_name='tray_unload2', service_version='2.0.0'
    )

    seq = py_trees.composites.Sequence()

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
    
    # manual_LED_dimming_front_off = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, 
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # manual_LED_dimming_rear_off = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_REAR,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, 
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    manual_LED_dimming_front_off = PublishTopic(
                name='manual_LED_dimming_front_off',
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

    manual_LED_dimming_rear_off = PublishTopic(
                name='manual_LED_dimming_rear_off',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    seq_undocking = py_trees.composites.Sequence()

    undocking_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'undocking_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="undocking_tree",
            operator= operator.eq
            )
        )

    go_to_undocking_moving_tree = EnqueueNextService(
        service_name='moving_tree', service_version='2.0.0'
    )

    seq_manual_charging_tree2 = py_trees.composites.Sequence()

    manual_charging_tree2_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'manual_charging_tree2_check',
            check=py_trees.common.ComparisonExpression(
            variable="previous_tree",
            value="manual_charging_tree2",
            operator= operator.eq
            )
        )

    go_to_manual_charging_tree2 = EnqueueNextService(
        service_name='manual_charging_tree2', service_version='2.0.0'
    )

    par_charging_check = py_trees.composites.Parallel(
        name = "par",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_next = py_trees.composites.Sequence()
    seq_manual_charging = py_trees.composites.Sequence()


    manual_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'manual_charging_check',
        check=py_trees.common.ComparisonExpression(
            variable="manual_contacted",
            value=1,
            operator=operator.eq
        )
    )

    not_manual_charging_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'not_manual_charging_check',
            check=py_trees.common.ComparisonExpression(
            variable="manual_contacted",
            value=0,
            operator= operator.eq
            )
        )
    
    IdlingIdling = Idling()


    par_serv = py_trees.composites.Parallel(
        name="par_serv",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
        )
    
    seq_after_req = py_trees.composites.Sequence()
    seq_before_req = py_trees.composites.Sequence()

    after_req_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'after_req_check',
            check=py_trees.common.ComparisonExpression(
            variable="current_goal_count",
            value=1,
            operator= operator.ge
        )
    )
    before_req_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'before_req_check',
            check=py_trees.common.ComparisonExpression(
            variable="current_goal_count",
            value=0,
            operator= operator.lt
        )
    )

    go_to_moving_tree_idle = EnqueueNextService(
        service_name='moving_tree', service_version='2.0.0'
    )

    tts_restart = TTSPlay(tts_name='remote_restart', play=True, sequence=True)

    seq.add_children([manual_driving_off_alarm, manual_LED_dimming_front_off, manual_LED_dimming_rear_off,  par_charging_check])
    par_charging_check.add_children([seq_manual_charging,seq_next])
    seq_manual_charging.add_children([manual_charging_check, IdlingIdling])
    seq_next.add_children([not_manual_charging_check, tts_restart, par])
    par.add_children([seq_bb_clear, seq_charging, seq_ev, seq_idle, seq_moving, seq_tray_cancel1, seq_tray_cancel2, seq_tray_fail1, seq_tray_fail2, seq_tray_load1, seq_tray_load2, seq_tray_unload1, seq_tray_unload2, seq_undocking, seq_manual_charging_tree2])
    seq_charging.add_children([charging_check, go_to_charging_tree])
    seq_ev.add_children([ev_check, generate_route(), go_to_ev_tree])
    seq_idle.add_children([idle_check, par_serv])

    par_serv.add_children([seq_before_req, seq_after_req])
    seq_before_req.add_children([before_req_check, go_to_idle_tree ])
    seq_after_req.add_children([after_req_check, generate_route_for_undocking(), go_to_moving_tree_idle ])
    


    seq_moving.add_children([moving_check, generate_route(), go_to_moving_tree])

    seq_tray_cancel1.add_children([tray_cancel1_check, go_to_tray_cancel1_tree])
    seq_tray_cancel2.add_children([tray_cancel2_check, go_to_tray_cancel2_tree])
    seq_tray_fail1.add_children([tray_fail1_check, go_to_tray_fail1_tree])
    seq_tray_fail2.add_children([tray_fail2_check, go_to_tray_fail2_tree])
    seq_tray_load1.add_children([tray_load1_check, go_to_tray_load1_tree])
    seq_tray_load2.add_children([tray_load2_check, go_to_tray_load2_tree])
    seq_tray_unload1.add_children([tray_unload1_check, go_to_tray_unload1_tree])
    seq_tray_unload2.add_children([tray_unload2_check, go_to_tray_unload2_tree])
    seq_undocking.add_children([undocking_check, generate_route_for_undocking(), go_to_undocking_moving_tree])
    seq_manual_charging_tree2.add_children([manual_charging_tree2_check, go_to_manual_charging_tree2])
    seq_bb_clear.add_children([bbclear_check, go_to_bbclear])



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

    
    tts_tray_error1 = TTSPlay(tts_name='tray_error', play=True, sequence=True)

    par_stuck_close.add_children([seq_stuck1, seq_stuck2])

    seq_stuck1.add_children([tray1_stuck_check, unset_hri1, unset_hri_status1, stuck_alarm1, unset_stuck1, tts_tray_error, par_selected1, tray_not_ing_check(), tray_close1])
    
    par_selected1.add_children([par_close_cmd1, seq_stuck_for_delay1])
    par_close_cmd1.add_children([wait_hri_tray2_id_cmd, tray_close_check1, hri_finished_check1])
    seq_stuck_for_delay1.add_children([tray1_stuck_check2, stuck_alarm1_2, tts_tray_error1, unset_stuck1_2])

    seq_stuck2.add_children([tray2_stuck_check,  unset_hri2, unset_hri_status2, stuck_alarm2, unset_stuck2, tts_tray_error2, par_selected2, tray_not_ing_check(), tray_close2])
    
    par_selected2.add_children([par_close_cmd2, seq_stuck_for_delay2])
    par_close_cmd2.add_children([wait_hri_tray1_id_cmd, tray_close_check2, hri_finished_check2])
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

# main tree
def create_root():

    root_init = py_trees.composites.Sequence()
    BB_start = BB_init()

    root_par = py_trees.composites.Parallel(
        name="manual_tree",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_main = py_trees.composites.Sequence()


    par_zone_check = py_trees.composites.Parallel(
        name="par_zone_check",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=False
        )
    )

    seq_EV_Unknown = py_trees.composites.Sequence()
    seq_keepout = py_trees.composites.Sequence()

    ev_unknown_result_wait = ev_unknown_check()

    localization_needed = PublishTopic(
                            name='localization_needed',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'manual_driving',
                                action = 'qr_localization_needed',
                                action_target = 'qr_code',
                                action_result = True
                                )   
                            )

    unset_ev_zone_result = SetBlackBoard('ev_zone_result', '')
    unset_unknown_zone_result = SetBlackBoard('unknown_zone_result', '')

    keepout_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'keepout_check',
            check=py_trees.common.ComparisonExpression(
            variable="keepout_zone_result",
            value=1,
            operator= operator.eq
            )
        )

    keepout_alarm = PublishTopic(
                            name='keepout_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'manual_driving',
                                action = 'keep_out_zone',
                                action_target = 'keep_out_zone',
                                action_result = True
                                )   
                            )
    
    non_keepout_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'non_keepout_check',
            check=py_trees.common.ComparisonExpression(
            variable="keepout_zone_result",
            value=0,
            operator= operator.eq
            )
        )

    non_keepout_alarm = PublishTopic(
                            name='non_keepout_alarm',
                            topic_name='ktmw_bt/task_status',
                            topic_type = TaskStatus, #TODO
                            msg_generate_fn=lambda: TaskStatus(
                                service_code=0,
                                task_id='',
                                goal_id='',
                                current_goal_id='',
                                tray_id=[0],             
                                task_status = 'manual_driving',
                                action = 'keep_out_zone',
                                action_target = 'keep_out_zone',
                                action_result = False
                                )   
                            )

    unset_keepout_zone_result = py_trees.behaviours.UnsetBlackboardVariable('keepout_zone_result')

    manual_driving_off_check_1 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'manual_driving_off_check_1',
            check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=False,
            operator= operator.eq
            )
        )

    manual_driving_off_check_2 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'manual_driving_off_check_2',
            check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=False,
            operator= operator.eq
            )
        )
    
    # led_manual_driving_off_f_1 = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_manual_driving_off_r_1 = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    led_manual_driving_off_f_1 = PublishTopic(
                name='led_manual_driving_off_f_1',
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

    led_manual_driving_off_r_1 = PublishTopic(
                name='led_manual_driving_off_r_1',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  

    # led_manual_driving_off_f_2 = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_manual_driving_off_r_2 = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    led_manual_driving_off_f_2 = PublishTopic(
                name='led_manual_driving_off_f_2',
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
    
    led_manual_driving_off_r_2 = PublishTopic(
                name='led_manual_driving_off_r_2',
                topic_name='led/set_led_effect_type',
                topic_type = LEDEffect,
                msg_generate_fn=lambda: LEDEffect(
                    cmd_id=0,
                    location=Location(position=2, x=1, y=1),
                    color=LEDState(cmd_id=1,r=255, g=255, b=0),
                    effect=0,
                    period=0,
                    on_ms=0,
                    repeat_count=0
                    )   
                )  
    
    # led_manual_driving_off_f_3 = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    # led_manual_driving_off_r_3 = LEDControl(
    #     color=LEDControl.COLOR_YELLOW,
    #     position=LEDControl.POSITION_FRONT,
    #     x=1,
    #     y=1,
    #     effect=LEDControl.EFFECT_LED_OFF, # on
    #     period_ms=0,
    #     on_ms=0,
    #     repeat_count=0)
    
    led_manual_driving_off_f_3 = PublishTopic(
                name='led_manual_driving_off_f_3',
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
    
    led_manual_driving_off_r_3 = PublishTopic(
                name='led_manual_driving_off_r_3',
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

    seq_just_off = py_trees.composites.Sequence()

    manual_driving_off_check_3 = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'manual_driving_off_check_3',
            check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=False,
            operator= operator.eq
            )
        )
    
    just_off_check = just_manual_off()

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

    BGM_off = BGMPlay(bgm_name=BGMPlay.BGM_OFF, play=BGMPlay.STOP, repeat = False)

    tts_qr_ready1= TTSPlay(tts_name='qr_ready', play=True, sequence=True)



    par_tray_check = py_trees.composites.Parallel(
        name="Msgs_to_BB_parallel",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(
            synchronise=True
        )        
    )

    seq_tray_open = py_trees.composites.Sequence()
    seq_tray_closed = py_trees.composites.Sequence()

    root_sel = py_trees.composites.Selector('manualdriving_tree')
    go_to_ciritcal_error2 = EnqueueNextService(
        service_name='critical_error_tree2', service_version='2.0.0'
    )
    idling_for_zone_checker = Idling()

    tts_manualdriving_off= TTSPlay(tts_name='manualdriving_end', play=True, sequence=True)

    seq_tts_1 = py_trees.composites.Sequence()
    
    manual_on_check = py_trees.behaviours.WaitForBlackboardVariableValue(
            name= 'manual_on_check',
            check=py_trees.common.ComparisonExpression(
            variable='button_manual_driving',
            value=True,
            operator= operator.eq
            )
        )   

    par_off = py_trees.composites.Parallel(
            name="par_off",
            policy=py_trees.common.ParallelPolicy.SuccessOnSelected(
            children=[manual_on_check],
            synchronise=False
            )
        )



    seq_manual_off = py_trees.composites.Sequence()

    root_sel.add_children([root_init, go_to_ciritcal_error2])

    root_init.add_children([BB_start, BGM_off, root_par])
    root_par.add_children([check_critical_error(), go_to_minor_error_tree(), msgs_to_BB_parallel(), minor_error_alarm(), check_manual_charge(), emergency_button_check(), battery_under_15(), check_auto_charge(), tray_stuck_seq_new(), seq_main, par_zone_check])

    seq_main.add_children([manual_driving_alarm, tts_manualdriving_on, opened_tray_check_and_close(), idling_for_zone_checker])

    par_zone_check.add_children([seq_EV_Unknown, seq_keepout, seq_just_off])
    seq_EV_Unknown.add_children([ev_unknown_result_wait, tts_qr_ready1, localization_needed, QR_recognize(), unset_ev_zone_result, unset_unknown_zone_result, seq_tts_1, led_manual_driving_off_f_1, led_manual_driving_off_r_1, next_step()])
    seq_tts_1.add_children([tts_manualdriving_off, manual_driving_off_check_1])
    seq_keepout.add_children([keepout_check, keepout_alarm, non_keepout_check, non_keepout_alarm, unset_keepout_zone_result])
    #manual_driving_off_check_2, led_manual_driving_off_f_2, led_manual_driving_off_r_2, next_step()
    seq_just_off.add_children([manual_driving_off_check_3, par_off])
    par_off.add_children([manual_on_check, seq_manual_off])
    seq_manual_off.add_children([just_off_check, manual_driving_off_check_2, led_manual_driving_off_f_3, led_manual_driving_off_r_3,next_step()])
    return root_sel
