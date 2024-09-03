'''
KT Robot Middleware version 1.0.0

Copyright ⓒ 2022 kt corp. All rights reserved.

This is a proprietary software of kt corp, and you may not use this file except in
compliance with license agreement with kt corp. Any redistribution or use of this
software, with or without modification shall be strictly prohibited without prior written
approval of kt corp, and the copyright notice above does not evidence any actual or
intended publication of such software.
'''

import time
from datetime import datetime 
import py_trees
import py_trees_ros
import typing
import rclpy
from rclpy.task import Future
from rclpy.node import Node, Client, Service, Publisher, Subscription
from std_msgs.msg import Empty, Bool, String
from ktmw_srvmgr_interfaces.srv import Execute
from ktmw_bt_interfaces.msg import SoundControl
from . import WAIT_FOR_SERVICE_TIMEOUT_SEC

import logging

FLAG_LOG = False

if FLAG_LOG:
    now_time = datetime.now()

    now_time_ = now_time.strftime('%Y-%m-%d %H:%M:%S')
    file_n = f"/home/kt/LOG/log_bt_common_{now_time_}.log"
    logging.basicConfig(filename=file_n, level=logging.DEBUG)


class Sleep(py_trees.behaviour.Behaviour):
    """
    Delay execution for a given number of seconds.
    The argument may be a floating point number for subsecond precision.
    Do not guarantee exact time and affected by rate of Lifecycle manager.
    """

    def __init__(self, duration: float, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self.duration = duration
        self.start_time = None

    def initialise(self):
        if self.start_time is None:
            self.start_time = time.time()

    def update(self):
        if time.time() - self.start_time >= self.duration:
            self.start_time = None
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.RUNNING


class EnqueueNextService(py_trees.behaviour.Behaviour):
    """
    Enqueue next service by name & version, fetch from Datamanager
    """

    def __init__(self, service_name, service_version, priority=Execute.Request.PRIORITY_NORMAL, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self._service_name = service_name
        self._service_version = service_version
        self._priority = priority

        self.node: Node = None
        self.client: Client = None
        self.future: Future = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        self.client = self.node.create_client(Execute, 'ktmw_srvmgr/enqueue')

    def initialise(self):
        self.future = None

        request = Execute.Request()
        request.service_name = self._service_name
        request.service_version = self._service_version
        request.priority = self._priority
        self.node.get_logger().info(
            '@EnqueueNextService ({})'.format(self.name))
        self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', 'ktmw_srvmgr/enqueue')            
            return py_trees.common.Status.FAILURE
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        response: Execute.Response = self.future.result()
        if response.result > Execute.Response.RESULT_SUCCESS:
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', 'ktmw_srvmgr/enqueue')               
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS


class EnqueueNextServiceCode(py_trees.behaviour.Behaviour):
    """
    Enqueue next service by code string
    """

    def __init__(self, code, priority=Execute.Request.PRIORITY_NORMAL, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self._code = code
        self._priority = priority

        self.node: Node = None
        self.client: Client = None
        self.future: Future = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        self.client = self.node.create_client(
            Execute, 'ktmw_srvmgr/enqueue_code')

    def initialise(self):
        self.future = None
        request = Execute.Request()
        request.code = self._code
        request.priority = self._priority
        self.node.get_logger().info('@EnqueueNextServiceCode ({})'.format(self.name))
        self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            return py_trees.common.Status.FAILURE
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        response: Execute.Response = self.future.result()
        if response.result > Execute.Response.RESULT_SUCCESS:
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS


class Idling(py_trees.behaviour.Behaviour):
    '''
    특정상태(UI입력, 배터리 상태)를 감지하기 위해 Tick될때마다 Running를 반환
    '''

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)

    def update(self):
        return py_trees.common.Status.RUNNING


class CreateService(py_trees.behaviour.Behaviour):
    '''
    서비스 생성 및 처리 Node \n
    request 요청이 들어오면 callback_fn(request, response)을 호출 \n
    callback_fn은 반드시 Service Spec에 맞는 response를 채워서 return 해야 함 \n
    항상 RUNNING state
    '''

    def __init__(self,
                 service_name: str,
                 service_type: typing.Any,
                 callback_fn: typing.Callable[[typing.Any, typing.Any], typing.Any],
                 name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self.service_name = service_name
        self.service_type = service_type
        self.callback_fn = callback_fn

        self.node: Node = None
        self.service: Service = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

    def initialise(self):
        self.node.get_logger().debug(
            'initialise create service node, [{}]'.format(self.name))
        if self.service is None:
            self.service = self.node.create_service(
                self.service_type, self.service_name, self.on_request)

    def terminate(self, new_status):
        if self.node is not None and self.service is not None:
            self.node.get_logger().debug(
                'terminate create service node, [{}]'.format(self.name))
            self.node.destroy_service(self.service)
            self.service = None

    def update(self):
        return py_trees.common.Status.RUNNING

    def on_request(self, request, response):
        res = None
        try:
            res = self.callback_fn(request, response)
        except Exception as e:
            self.node.get_logger().warn(
                'CreateService [{}] callback funtion raise an error. {}'.format(self.name, str(e)))
            pass
        if res is None:
            self.node.get_logger().warn(
                'CreateSerivce [{}] callback funtion does not return any response value.'.format(self.name))
            return response
        return res


class ServiceCall(py_trees.behaviour.Behaviour):
    '''
    서비스 호출 및 처리 Node
    request 생성 및 response callback fn을 사용해 response 처리
    '''

    def __init__(self,
                 service_name: str,
                 service_type: typing.Any,
                 request_generate_fn: typing.Callable[[], typing.Any],
                 response_fn: typing.Callable[[typing.Any], typing.NoReturn],
                 name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self.service_name = service_name
        self.service_type = service_type
        self.request_generate_fn = request_generate_fn
        self.response_fn = response_fn

        self.node: Node = None
        self.client: Client = None
        self.future: Future = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        self.client = self.node.create_client(
            self.service_type, self.service_name)

    def initialise(self):
        self.future = None

        request = None
        try:
            request = self.request_generate_fn()
        except Exception as e:
            self.node.get_logger().warn(
                'ServiceCall [{}] request generation function raise an error. {}'.format(self.name, str(e)))
            pass
        if request is None:
            self.node.get_logger().warn(
                'ServiceCall [{}] request generation callback funtion does not return any request value.'.format(self.name))
        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        
        if FLAG_LOG:
            now_time__ = datetime.now()
            now_time__ = now_time__.strftime('%Y-%m-%d %H:%M:%S')

            logging.debug("------------------------------")
            logging.debug("TIME        : " + now_time__)

            #service code/ 목적지/ previous tree
            logging.debug("service_code: " + str(py_trees.blackboard.Blackboard.get("service_code")))
            logging.debug("current_tree: " + str(py_trees.blackboard.Blackboard.get("previous_tree")))
            logging.debug("service_uri : " + str(self.service_name))
            logging.debug("")


        if self.future is None:
            if FLAG_LOG:
                logging.debug("result      : FAILURE")
                logging.debug("debug       : Request error")

            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', self.service_name)

            return py_trees.common.Status.FAILURE
            
        if not self.future.done():
            if FLAG_LOG:
                logging.debug("result      : RUNNING")

            return py_trees.common.Status.RUNNING
        try:
            response = self.future.result()
            if self.response_fn is None:
                self.node.get_logger().warn(
                    'ServiceCall [{}] response callback funtion does not exist.'.format(self.name))
            else:
                self.response_fn(response)
        except Exception as e:
            if FLAG_LOG:
                logging.debug("result      : FAILURE")
                logging.debug("debug       : " + str(e))

            self.node.get_logger().warn(
                'ServiceCall [{}] response handler function raise an error. {}'.format(self.name, str(e)))
            py_trees.blackboard.Blackboard.set('exception_action_node', self.service_name)

            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', self.service_name)

            return py_trees.common.Status.FAILURE
        
        if FLAG_LOG:
            logging.debug("result      : SUCCESS")
        return py_trees.common.Status.SUCCESS


class PublishTopic(py_trees.behaviour.Behaviour):
    '''
    토픽 메시지 전송 Node. \n
    msg_generate_fn에 전송 할 메시지 Object를 Runtime에 생성하는 lambda funtion을 입력해 사용.

    예시: \n
    PublishTopic('/ktmw_bt/service_start_alarm', ServiceStartAlarm,
        msg_generate_fn=lambda: ServiceStartAlarm(
            service_code=py_trees.blackboard.Blackboard.get('service_code'),
            service_id=py_trees.blackboard.Blackboard.get('service_id'),
            task_id=py_trees.blackboard.Blackboard.get('task_id')
        ), name='ServiceStartAlarmToUI')
    '''

    def __init__(self,
                 topic_name: str,
                 topic_type: typing.Any,
                 msg_generate_fn: typing.Callable[[], typing.Any],
                 name: str = py_trees.common.Name.AUTO_GENERATED,
                 qos_profile: rclpy.qos.QoSProfile = rclpy.qos.QoSProfile(depth=1)):
        super().__init__(name=name)
        self.topic_name = topic_name
        self.topic_type = topic_type
        self.qos_profile = qos_profile
        self.msg_generate_fn = msg_generate_fn

        self.node: Node = None
        self.publisher: Publisher = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        self.publisher = self.node.create_publisher(
            msg_type=self.topic_type, topic=self.topic_name, qos_profile=self.qos_profile)

    def initialise(self):
        self._published = False

    def update(self):
        if FLAG_LOG:    
            now_time__ = datetime.now()
            now_time__ = now_time__.strftime('%Y-%m-%d %H:%M:%S')

            logging.debug("------------------------------")
            logging.debug("TIME        : " + now_time__)

            #service code/ 목적지/ previous tree
            logging.debug("service_code: " + str(py_trees.blackboard.Blackboard.get("service_code")))
            logging.debug("current_tree: " + str(py_trees.blackboard.Blackboard.get("previous_tree")))
            logging.debug("topic_uri   : " + str(self.topic_name))
            logging.debug("")

        try:
            if not self._published:
                self.node.get_logger().info(
                    '@PublishTopic ({}), topic_name: [{}]'.format(self.name, self.topic_name))
                msg = self.msg_generate_fn()
                self.publisher.publish(msg)
                self._published = True
                logging.debug("result      : RUNNING")

                return py_trees.common.Status.RUNNING
            if FLAG_LOG:
                logging.debug("result      : SUCCESS")
            return py_trees.common.Status.SUCCESS
        except Exception as e:
            error_message = 'Failed to publish topic [{}]: {}'.format(
                self.topic_name, str(e))
            self.node.get_logger().warn(error_message)
            if FLAG_LOG:

                logging.debug("result      : FAILURE")
                logging.debug("debug       : " + str(e))

            return py_trees.common.Status.FAILURE


class SubscribeTopic(py_trees.behaviour.Behaviour):
    def __init__(self,
                 topic_name: str,
                 topic_type: typing.Any,
                 on_msg_fn: typing.Callable[[typing.Any], typing.NoReturn],
                 name: str = py_trees.common.Name.AUTO_GENERATED,
                 qos_profile: rclpy.qos.QoSProfile = rclpy.qos.QoSProfile(depth=10)):
        super().__init__(name=name)
        self.topic_name = topic_name
        self.topic_type = topic_type
        self.on_msg_fn = on_msg_fn
        self.qos_profile = qos_profile

        self.node: Node = None
        self.subscription: Subscription = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

    def initialise(self):
        if self.subscription is None:
            self.subscription = self.node.create_subscription(
                self.topic_type, self.topic_name, self.on_message, self.qos_profile)
            self.node.get_logger().info('create-subscription {}'.format(self.topic_name))

    def on_message(self, msg):
        try:
            self.on_msg_fn(msg)
        except Exception as e:
            self.node.get_logger().warn(
                'SubscribeTopic [{}] on_msg_fn raise an error. {}'.format(self.name, str(e)))

    def update(self):
        if self.subscription is None:
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status):
        if self.node is not None and self.subscription is not None:
            self.node.destroy_subscription(self.subscription)
            self.subscription = None




class TTSPlay(py_trees.behaviour.Behaviour):
    '''
    TTS play UI로 요청
    '''
    URI = 'ktmw_bt/tts_control/service'

    TTS_SVC_START = "tts_service_start"
    TTS_AUTH_PW = "tts_auth_pw"
    TTS_ARRIVED_AUTO = "tts_arrived_auto"
    TTS_ARRIVED_PW = "tts_arrived_pw"
    TTS_ARRIVED_TALK = "tts_arrived_talk"
    TTS_SVC_CANCEL = "tts_service_cancel"
    TTS_TRAY_OBJECT = "tray_object"
    TTS_TRAY_OPEN = "tts_tray_open"
    TTS_TRAY_CLOSE = "tts_tray_close"
    TTS_SVC_FAIL = "tts_service_fail"
    TTS_NAV_BLOCKED = "tts_nav_blocked"
    TTS_NAV_ERROR_ALARM = "tts_nav_error_alarm"

    PLAY = True
    STOP = False

    def __init__(self, tts_name: str, play: bool, sequence: bool, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self.tts_name = tts_name
        self.play = play
        self.sequence = sequence

        self.node: Node = None
        self.node_: Node = None
        self.publisher: Publisher = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        self.publisher = self.node.create_publisher(
            msg_type=SoundControl, topic=TTSPlay.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())
        
        self.publisher_ = self.node.create_publisher(
            msg_type=SoundControl, topic=TTSPlay.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())        

    def initialise(self):
        self._published = False

    def update(self):
        try:
            if not self._published:
                msg = SoundControl(name=self.tts_name, play=self.play, sequence=self.sequence)
                self.publisher.publish(msg)
                self._published = True
                self.node.get_logger().info(
                    '@TTSPlay ({}) publish, tts_name: [{}]'.format(self.name, self.tts_name))
                return py_trees.common.Status.RUNNING
            self._published = False
            return py_trees.common.Status.SUCCESS
        except Exception as e:
            error_message = 'Failed to publish tts play topic: {}'.format(
                str(e))
            self.node.get_logger().warn(error_message)

            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Major')
            py_trees.blackboard.Blackboard.set('error_cause', TTSPlay.URI)

            return py_trees.common.Status.SUCCESS


class BGMPlay(py_trees.behaviour.Behaviour):
    '''
    TTS play UI로 요청
    '''
    URI = 'ktmw_bt/bgm_param/service'

    BGM_MOVING = "bgm_moving"
    BGM_OFF = "bgm_off"
    BGM_SURVEILLANCE_EVENT_ALARM = "bgm_surveillance_event_alarm"
    BGM_EVENT = "bgm_event"
    BGM_ERROR = "bgm_error"

    PLAY = True
    STOP = False

    def __init__(self, bgm_name: str, play: bool, repeat: bool, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self.bgm_name = bgm_name
        self.play = play
        self.repeat = repeat

        self.node: Node = None
        self.publisher: Publisher = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        self.publisher = self.node.create_publisher(
            msg_type=SoundControl, topic=BGMPlay.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

    def initialise(self):
        self._published = False

    def update(self):
        try:
            if not self._published:
                msg = SoundControl(name=self.bgm_name, play=self.play, repeat = self.repeat)
                self.publisher.publish(msg)
                self._published = True
                self.node.get_logger().info(
                    '@BGMPlay ({}) publish, bgm_name: [{}]'.format(self.name, self.bgm_name))
                return py_trees.common.Status.RUNNING
            return py_trees.common.Status.SUCCESS
        except Exception as e:
            error_message = 'Failed to publish tts play topic: {}'.format(
                str(e))
            self.node.get_logger().warn(error_message)
            
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Major')
            py_trees.blackboard.Blackboard.set('error_cause', BGMPlay.URI)
            
            return py_trees.common.Status.SUCCESS


class RequestNextServiceList(py_trees.behaviour.Behaviour):
    '''
    다음 서비스 조회 요청
    '''
    URI = 'ktmw_bt/next_service_list'

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)

        self.node: Node = None
        self.publisher: Publisher = None

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

        self.publisher = self.node.create_publisher(
            msg_type=Empty, topic=RequestNextServiceList.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

    def initialise(self):
        self._published = False

    def update(self):
        try:
            if not self._published:
                msg = Empty()
                self.publisher.publish(msg)
                self._published = True
                self.node.get_logger().info(
                    '@RequestNextServiceList ({}) publish'.format(self.name))
                return py_trees.common.Status.RUNNING
            return py_trees.common.Status.SUCCESS
        except Exception as e:
            error_message = 'Failed to publish request next service list topic: {}'.format(
                str(e))
            self.node.get_logger().warn(error_message)
            return py_trees.common.Status.FAILURE


class FailAction(py_trees.behaviour.Behaviour):
    '''
    fail tts 요청 --> UI
    fail 된 task에 포함된 트레이의 led red flash(점멸) 명령
    '''

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability

class GetCurrentTime(py_trees.behaviour.Behaviour):

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

#    def initialise(self):

    def update(self):

        py_trees.blackboard.Blackboard.set('start_time', time.time())

        return py_trees.common.Status.SUCCESS


class NoResponseCheck(py_trees.behaviour.Behaviour):
    """
    """

    def __init__(self, time1, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.time = time1

    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

#    def initialise(self):

    def update(self):

        count = py_trees.blackboard.Blackboard.get(self.time) #300
        start_time= py_trees.blackboard.Blackboard.get('start_time')
        py_trees.blackboard.Blackboard.set('current_time', time.time())            

        
        current_time= py_trees.blackboard.Blackboard.get('current_time')

        if (current_time - start_time) >= count:
            return py_trees.common.Status.SUCCESS

        else: 
            return py_trees.common.Status.RUNNING


class InitCount(py_trees.behaviour.Behaviour):
    """
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

#    def initialise(self):

    def update(self):

        py_trees.blackboard.Blackboard.set('start_time', time.time())

        return py_trees.common.Status.SUCCESS






                
    

class GetTrayStatus(py_trees.behaviour.Behaviour):
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



#    def initialise(self):

    def update(self):
        tray1_stat = py_trees.blackboard.Blackboard.get("Tray_1_open_status")
        tray2_stat = py_trees.blackboard.Blackboard.get("Tray_2_open_status")
        
        if tray1_stat == 1 and tray2_stat == 1:
            py_trees.blackboard.Blackboard.set("Tray_all_done", True)
            
        else:
            py_trees.blackboard.Blackboard.set("Tray_all_done", False)
                
        return py_trees.common.Status.SUCCESS
    


class SetBlackBoard(py_trees.behaviour.Behaviour):
    """
    BB init
    """

    def __init__(self, BB_variable, BB_value,  name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable = BB_variable
        self.BB_value = BB_value


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD



#    def initialise(self):

    def update(self):
        py_trees.blackboard.Blackboard.set(self.BB_variable, self.BB_value)
                
        return py_trees.common.Status.SUCCESS
    
class GetandSetBlackBoard(py_trees.behaviour.Behaviour):
    """
    BB init
    """

    def __init__(self, BB_variable, BB_value,  name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable = BB_variable
        self.BB_value = BB_value


    def setup(self, **kwargs):
        try:
            self.node = kwargs['node']
        except KeyError as e:
            error_message = "didn't find 'node' in setup's kwargs [{}][{}]".format(
                self.qualified_name)
            raise KeyError(error_message) from e  # 'direct cause' traceability
        # TODO TBD

    def update(self):
        self.bb_value=py_trees.blackboard.Blackboard.get(self.BB_value)
        py_trees.blackboard.Blackboard.set(self.BB_variable, self.bb_value)
                
        return py_trees.common.Status.SUCCESS        


class compareBBvariableforcorrect(py_trees.behaviour.Behaviour):
    """
    """

    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1
        self.BB_variable2 = BB_variable2


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
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)
        
        if self.bb1 == self.bb2:
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING    

                    


class compareBBvariableforincorrect(py_trees.behaviour.Behaviour):
    """
    """

    def __init__(self, BB_variable1, BB_variable2, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        
        self.BB_variable1 = BB_variable1
        self.BB_variable2 = BB_variable2


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
        self.bb1 = py_trees.blackboard.Blackboard.get(self.BB_variable1)
        self.bb2 = py_trees.blackboard.Blackboard.get(self.BB_variable2)
        
        if self.bb1 != self.bb2:
            return py_trees.common.Status.SUCCESS    
        else: 
            return py_trees.common.Status.RUNNING  