'''
KT Robot Middleware version 1.0.0

Copyright ⓒ 2022 kt corp. All rights reserved.

This is a proprietary software of kt corp, and you may not use this file except in
compliance with license agreement with kt corp. Any redistribution or use of this
software, with or without modification shall be strictly prohibited without prior written
approval of kt corp, and the copyright notice above does not evidence any actual or
intended publication of such software.
'''

import typing
import py_trees
import py_trees_ros
from rclpy.node import Node, Client
from rclpy.task import Future
from kt_msgs.msg import Location
from hardware_manager_msgs.srv import LEDEffect, BoxCtrl, VolumeCtrl, MuteCtrl
from . import HW_CTRL_UUID, WAIT_FOR_SERVICE_TIMEOUT_SEC
from datetime import datetime 
import logging

now_time = datetime.now()

now_time_ = now_time.strftime('%Y-%m-%d %H:%M:%S')
file_n = f"/home/kt/LOG/log_bt_common_{now_time_}.log"
logging.basicConfig(filename=file_n, level=logging.DEBUG)

class LEDControl(py_trees.behaviour.Behaviour):
    '''
    Control LED state
    position:
        LEDControl.POSITION_ALL
        LEDControl.POSITION_FRONT
        LEDControl.POSITION_REAR
        LEDControl.POSITION_LEFT
        LEDControl.POSITION_RIGHT
        LEDControl.POSITION_TOP
        LEDControl.POSITION_BOTTOM
    x: LEDControl location x
    y: LEDControl location y
    color:
        LEDControl.COLOR_OFF
        LEDControl.COLOR_RED
        LEDControl.COLOR_GREEN
        LEDControl.COLOR_BLUE
        LEDControl.COLOR_YELLOW
        LEDControl.COLOR_ORANGE
    effect:
        LEDControl.EFFECT_LED_OFF
        LEDControl.EFFECT_LED_ON
        LEDControl.EFFECT_LED_FLASH
        LEDControl.EFFECT_LED_SEQUENTIAL_LED_ON
        LEDControl.EFFECT_LED_SEQUENTIAL_LED_OFF
        LEDControl.EFFECT_LED_REVERSE_SEQUENTIAL_LED_ON
        LEDControl.EFFECT_LED_REVERSE_SEQUENTIAL_LED_OFF
        LEDControl.EFFECT_LED_SEQUENTIAL_LED_FLASH
        LEDControl.EFFECT_LED_REVERSE_SEQUENTIAL_LED_FLASH
    period_ms: 한번의 Effect Cycle이 완료되는 시간(ms)
    on_ms: Effect에서 단일 LED가 켜져있는 시간(ms)
    repeat_count: Effect 반복 횟수
    '''
    URI = 'hardware_manager/led/effect_type_control'

    POSITION_ALL = Location.POSITION_ALL
    POSITION_FRONT = Location.POSITION_FRONT
    POSITION_REAR = Location.POSITION_REAR
    POSITION_LEFT = Location.POSITION_LEFT
    POSITION_RIGHT = Location.POSITION_RIGHT
    POSITION_TOP = Location.POSITION_TOP
    POSITION_BOTTOM = Location.POSITION_BOTTOM

    COLOR_OFF = LEDEffect.Request.COLOR_OFF
    COLOR_RED = LEDEffect.Request.COLOR_RED
    COLOR_GREEN = LEDEffect.Request.COLOR_GREEN
    COLOR_BLUE = LEDEffect.Request.COLOR_BLUE
    COLOR_YELLOW = LEDEffect.Request.COLOR_YELLOW
    COLOR_ORANGE = LEDEffect.Request.COLOR_ORANGE
    COLOR_WHITE = LEDEffect.Request.COLOR_WHITE

    EFFECT_LED_OFF = LEDEffect.Request.EFFECT_LED_OFF
    EFFECT_LED_ON = LEDEffect.Request.EFFECT_LED_ON
    EFFECT_LED_FLASH = LEDEffect.Request.EFFECT_LED_FLASH
    EFFECT_SEQUENTIAL_LED_ON = LEDEffect.Request.EFFECT_SEQUENTIAL_LED_ON
    EFFECT_SEQUENTIAL_LED_OFF = LEDEffect.Request.EFFECT_SEQUENTIAL_LED_OFF
    EFFECT_REVERSE_SEQUENTIAL_LED_ON = LEDEffect.Request.EFFECT_REVERSE_SEQUENTIAL_LED_ON
    EFFECT_REVERSE_SEQUENTIAL_LED_OFF = LEDEffect.Request.EFFECT_REVERSE_SEQUENTIAL_LED_OFF
    EFFECT_SEQUENTIAL_LED_FLASH = LEDEffect.Request.EFFECT_SEQUENTIAL_LED_FLASH
    EFFECT_REVERSE_SEQUENTIAL_LED_FLASH = LEDEffect.Request.EFFECT_REVERSE_SEQUENTIAL_LED_FLASH

    def __init__(self, position, x, y, color, effect, period_ms, on_ms, repeat_count, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self._position = position
        self._x = x
        self._y = y
        self._color = color
        self._effect = effect
        self._period_ms = period_ms
        self._on_ms = on_ms
        self._repeat_count = repeat_count

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

    def initialise(self):
        self.future = None

        if self.client is None:
            self.client = self.node.create_client(
                LEDEffect, LEDControl.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        request = LEDEffect.Request()
        request.uuid = HW_CTRL_UUID
        request.location.position = self._position
        request.location.x = self._x
        request.location.y = self._y
        request.color = self._color
        request.effect = self._effect
        request.period_ms = self._period_ms
        request.on_ms = self._on_ms
        request.repeat_count = self._repeat_count
        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        now_time__ = datetime.now()
        now_time__ = now_time__.strftime('%Y-%m-%d %H:%M:%S')
        logging.debug("------------------------------")
        logging.debug("TIME        : " + now_time__)

        #service code/ 목적지/ previous tree
        logging.debug("service_code: " + str(py_trees.blackboard.Blackboard.get("service_code")))
        logging.debug("current_tree: " + str(py_trees.blackboard.Blackboard.get("previous_tree")))
        logging.debug("service_uri : " + str( LEDControl.URI))
        logging.debug("")


        if self.future is None:
            logging.debug("result      : FAILURE but PASS")
            logging.debug("debug       : Request error")
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Major')
            py_trees.blackboard.Blackboard.set('error_cause', LEDControl.URI)
            return py_trees.common.Status.SUCCESS #It was FAILURE
        if not self.future.done():
            logging.debug("result      : RUNNING")
            return py_trees.common.Status.RUNNING
        try:
            response: LEDEffect.Response = self.future.result()
        except:
            logging.debug("result      : FAILURE but PASS")
            logging.debug("debug       : Request error")           
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Major')
            py_trees.blackboard.Blackboard.set('error_cause', LEDControl.URI)
            return py_trees.common.Status.SUCCESS #It was FAILURE
        logging.debug("result      : SUCCESS")
        return py_trees.common.Status.SUCCESS




class LEDControlWithFn(py_trees.behaviour.Behaviour):
    '''
    Control LED State with callback functions.

    LEDControlWithFn(
                location_gen_fn=lambda: {"position": py_trees.blackboard.Blackboard.get('target_led_position'), "x": 1, "y": 1},
                color_gen_fn=lambda: LEDControl.COLOR_RED,
                effect_gen_fn=lambda: LEDControl.EFFECT_LED_FLASH,
                period_ms=500, on_ms=1000, repeat_count=1)
    '''

    def __init__(self,
                 location_gen_fn: typing.Callable[[], typing.Dict],
                 color_gen_fn: typing.Callable[[], int],
                 effect_gen_fn: typing.Callable[[], int],
                 period_ms, on_ms, repeat_count,
                 name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self.location_gen_fn = location_gen_fn
        self.color_gen_fn = color_gen_fn
        self.effect_gen_fn = effect_gen_fn
        self.period_ms = period_ms
        self.on_ms = on_ms
        self.repeat_count = repeat_count

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

    def initialise(self):
        self.future = None

        if self.client is None:
            self.client = self.node.create_client(
                LEDEffect, LEDControl.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        generated_location = None
        generated_color = None
        generated_effect = None

        try:
            generated_location = self.location_gen_fn()
            generated_color = self.color_gen_fn()
            generated_effect = self.effect_gen_fn()
        except Exception as e:
            self.node.get_logger().warn(
                'LEDControlWithFn [{}] message generation function raise an error. {}'.format(self.name, str(e)))

        request = LEDEffect.Request()
        request.uuid = HW_CTRL_UUID

        if generated_location is not None:
            if 'position' in generated_location:
                request.location.position = generated_location['position']
            else:
                self.node.get_logger().warn(
                    'LEDControlWithFn [{}] generated location return value has no position.'.format(self.name))

            if 'x' in generated_location:
                request.location.x = generated_location['x']
            else:
                self.node.get_logger().warn(
                    'LEDControlWithFn [{}] generated location return value has no x.'.format(self.name))

            if 'y' in generated_location:
                request.location.y = generated_location['y']
            else:
                self.node.get_logger().warn(
                    'LEDControlWithFn [{}] generated location return value has no y.'.format(self.name))

        if generated_color is not None:
            request.color = generated_color

        if generated_effect is not None:
            request.effect = generated_effect

        request.period_ms = self.period_ms
        request.on_ms = self.on_ms
        request.repeat_count = self.repeat_count
        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            return py_trees.common.Status.SUCCESS #It was FAILURE
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        try:
            response: LEDEffect.Response = self.future.result()
        except:
            return py_trees.common.Status.SUCCESS #It was FAILURE
        return py_trees.common.Status.SUCCESS




class LEDOff(LEDControl):
    '''
    Turn off all LED
    '''

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(LEDControl.POSITION_ALL, 0, 0, LEDControl.COLOR_OFF,
                         LEDControl.EFFECT_LED_OFF, 0, 0, 0, name=name)


class BoxControl(py_trees.behaviour.Behaviour):
    """
    Box control base node
    command:
        BoxControl.COMMAND_OPEN
        BoxControl.COMMAND_CLOSE
        BoxControl.COMMAND_CLOSE_AND_LOCK
        BoxControl.COMMAND_LOCK
        BoxControl.COMMAND_UNLOCK
    position:
        BoxControl.POSITION_ALL
        BoxControl.POSITION_FRONT
        BoxControl.POSITION_REAR
        BoxControl.POSITION_LEFT
        BoxControl.POSITION_RIGHT
        BoxControl.POSITION_TOP
        BoxControl.POSITION_BOTTOM
    x: BoxControl location x
    y: BoxControl location y
    """
    URI = 'hardware_manager/box/box_control'

    COMMAND_OPEN = BoxCtrl.Request.CMD_OPEN
    COMMAND_CLOSE = BoxCtrl.Request.CMD_CLOSE
    COMMAND_CLOSE_AND_LOCK = BoxCtrl.Request.CMD_CLOSE_AND_LOCK
    COMMAND_LOCK = BoxCtrl.Request.CMD_LOCK
    COMMAND_UNLOCK = BoxCtrl.Request.CMD_UNLOCK

    POSITION_ALL = Location.POSITION_ALL
    POSITION_FRONT = Location.POSITION_FRONT
    POSITION_REAR = Location.POSITION_REAR
    POSITION_LEFT = Location.POSITION_LEFT
    POSITION_RIGHT = Location.POSITION_RIGHT
    POSITION_TOP = Location.POSITION_TOP
    POSITION_BOTTOM = Location.POSITION_BOTTOM

    def __init__(self, command, position, x, y, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self._command = command
        self._position = position
        self._x = x
        self._y = y

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

    def initialise(self):
        self.future = None

        if self.client is None:
            self.client = self.node.create_client(
                BoxCtrl, BoxControl.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        request = BoxCtrl.Request()
        request.uuid = HW_CTRL_UUID
        request.data.box_command = self._command
        request.data.location.position = self._position
        request.data.location.x = self._x
        request.data.location.y = self._y

        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            logging.debug("result      : FAILURE but PASS")
            logging.debug("debug       : Request error")

            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', BoxControl.URI)
            return py_trees.common.Status.SUCCESS #It was FAILURE
        if not self.future.done():
            logging.debug("result      : RUNNING")
            return py_trees.common.Status.RUNNING
        try:
            response: BoxCtrl.Response = self.future.result()
            # TODO check result of response
        except:
            logging.debug("result      : FAILURE but PASS")
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', BoxControl.URI)
            return py_trees.common.Status.SUCCESS #It was FAILURE
        logging.debug("result      : SUCCESS")
        return py_trees.common.Status.SUCCESS




class BoxLock(BoxControl):
    def __init__(self, position: int, x: int, y: int, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(command=BoxControl.COMMAND_LOCK,
                         position=position, x=x, y=y, name=name)


class BoxUnlock(BoxControl):
    def __init__(self, position: int, x: int, y: int, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(command=BoxControl.COMMAND_UNLOCK,
                         position=position, x=x, y=y, name=name)


class BoxOpen(BoxControl):
    def __init__(self, position: int, x: int, y: int, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(command=BoxControl.COMMAND_OPEN,
                         position=position, x=x, y=y, name=name)


class BoxClose(BoxControl):
    def __init__(self, position: int, x: int, y: int, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(command=BoxControl.COMMAND_CLOSE,
                         position=position, x=x, y=y, name=name)


class BoxCloseAndLock(BoxControl):
    def __init__(self, position: int, x: int, y: int, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(command=BoxControl.COMMAND_CLOSE_AND_LOCK,
                         position=position, x=x, y=y, name=name)


class SpeakerMute(py_trees.behaviour.Behaviour):
    '''
    Mute speaker
    '''
    URI = 'hardware_manager/speaker/mute_control'

    def __init__(self, mute=True, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self._mute = mute

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

    def initialise(self):
        self.future = None

        if self.client is None:
            self.client = self.node.create_client(
                MuteCtrl, SpeakerMute.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        request = MuteCtrl.Request()
        request.uuid = HW_CTRL_UUID
        request.data.mute = self._mute
        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            return py_trees.common.Status.FAILURE
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        try:
            response: MuteCtrl.Response = self.future.result()
            # TODO check result of response
        except:
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS



class SpeakerUnmute(SpeakerMute):
    '''
    Unmute speaker
    '''

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(mute=False, name=name)


class SpeakerVolumeControl(py_trees.behaviour.Behaviour):
    '''
    Volume control
    volume: 0 ~ 100
    '''
    URI = 'hardware_manager/speaker/volume_control'

    def __init__(self, volume: int, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self._volume = volume

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

    def initialise(self):
        self.future = None

        if self.client is None:
            self.client = self.node.create_client(
                VolumeCtrl, SpeakerVolumeControl.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        request = VolumeCtrl.Request()
        request.uuid = HW_CTRL_UUID
        request.data.volume = self._volume
        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            return py_trees.common.Status.FAILURE
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        try:
            response: VolumeCtrl.Response = self.future.result()
            # TODO check result of response
        except:
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS


