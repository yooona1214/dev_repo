'''
KT Robot Middleware version 1.0.0

Copyright ⓒ 2022 kt corp. All rights reserved.

This is a proprietary software of kt corp, and you may not use this file except in
compliance with license agreement with kt corp. Any redistribution or use of this
software, with or without modification shall be strictly prohibited without prior written
approval of kt corp, and the copyright notice above does not evidence any actual or
intended publication of such software.
'''

import py_trees
import py_trees_ros
import typing
from rclpy.node import Node, Client
from rclpy.task import Future
from kt_nav_msgs.srv import SetNavGoal
from std_srvs.srv import Trigger, SetBool
from . import WAIT_FOR_SERVICE_TIMEOUT_SEC


class NavigationStart(py_trees.behaviour.Behaviour):
    '''
    주행 요청.
    req_generate_fn: 아래와 같은 구조의 Dict를 runtime에 생성하는 lambda function \n
    {'target_label': '', 'goal_label': '', 'mode': '', 'req_id': '', 'speed_scale': 0.5}
    '''
    URI = 'nav/set_nav_goal'

    def __init__(self, req_generate_fn: typing.Callable[[], typing.Dict], name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)

        self.req_generate_fn = req_generate_fn

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
                SetNavGoal, NavigationStart.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        target_label = None
        goal_label = None
        mode = None
        req_id = None
        speed_scale = None

        try:
            generated_msg = self.req_generate_fn()

            if not 'target_label' in generated_msg:
                self.node.get_logger().warn(
                    'NavigationStart [{}] generated request message has no target_label'.format(self.name))
            else:
                target_label = generated_msg['target_label']

            if not 'goal_label' in generated_msg:
                self.node.get_logger().warn(
                    'NavigationStart [{}] generated request message has no goal_label'.format(self.name))
            else:
                goal_label = generated_msg['goal_label']

            if not 'mode' in generated_msg:
                self.node.get_logger().warn(
                    'NavigationStart [{}] generated request message has no mode'.format(self.name))
            else:
                mode = generated_msg['mode']

            if not 'req_id' in generated_msg:
                self.node.get_logger().warn(
                    'NavigationStart [{}] generated request message has no req_id'.format(self.name))
            else:
                req_id = generated_msg['req_id']

            if not 'speed_scale' in generated_msg:
                self.node.get_logger().warn(
                    'NavigationStart [{}] generated request message has no speed_scale'.format(self.name))
            else:
                speed_scale = generated_msg['speed_scale']

        except Exception as e:
            self.node.get_logger().warn(
                'NavigationStart [{}] request generation function raise an error. {}'.format(self.name, str(e)))

        request = SetNavGoal.Request()

        if target_label is not None:
            request.target_label = target_label

        if goal_label is not None:
            request.goal_label = goal_label

        if mode is not None:
            request.mode = mode

        if req_id is not None:
            request.req_id = req_id

        if speed_scale is not None:
            request.speed_scale = speed_scale

        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            return py_trees.common.Status.FAILURE
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        try:
            response: SetNavGoal.Response = self.future.result()
            if not response.result:
                return py_trees.common.Status.FAILURE
        except:
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS



class NavigationCancel(py_trees.behaviour.Behaviour):
    '''
    실행/대기중인 주행 요청을 모두 취소한다.
    '''
    URI = 'nav/cancel_goal'

    def __init__(self, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)

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
                Trigger, NavigationCancel.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        request = Trigger.Request()

        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', NavigationCancel.URI)
            return py_trees.common.Status.SUCCESS
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        try:
            response: Trigger.Response = self.future.result()
            if not response.success:
                self.node.get_logger().warn('Navigation cancel failed: {}'.format(response.message))
                py_trees.blackboard.Blackboard.set('error_status', True)
                py_trees.blackboard.Blackboard.set('error_level', 'Critical')
                py_trees.blackboard.Blackboard.set('error_cause', NavigationCancel.URI)
                return py_trees.common.Status.SUCCESS
        except:
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', NavigationCancel.URI)
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.SUCCESS



class NavigationPause(py_trees.behaviour.Behaviour):
    '''
    실행/대기중인 주행 일시 정지 또는 해제한다.
    pause = True : 일시 정지
    pause = False: 주행 재개
    '''
    URI = 'nav/pause'

    def __init__(self, pause: bool, name: str = py_trees.common.Name.AUTO_GENERATED):
        super().__init__(name=name)
        self.pause = pause

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
                SetBool, NavigationPause.URI, qos_profile=py_trees_ros.utilities.qos_profile_unlatched())

        request = SetBool.Request()
        request.data = self.pause

        if self.client.wait_for_service(timeout_sec=WAIT_FOR_SERVICE_TIMEOUT_SEC):
            self.future = self.client.call_async(request)

    def update(self):
        if self.future is None:

            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', NavigationPause.URI)

            return py_trees.common.Status.SUCCESS
        if not self.future.done():
            return py_trees.common.Status.RUNNING
        try:
            response: SetBool.Response = self.future.result()
            if not response.success:
                self.node.get_logger().warn('Navigation cancel failed: {}'.format(response.message))

                py_trees.blackboard.Blackboard.set('error_status', True)
                py_trees.blackboard.Blackboard.set('error_level', 'Critical')
                py_trees.blackboard.Blackboard.set('error_cause', NavigationPause.URI)

                return py_trees.common.Status.SUCCESS
        except:
            py_trees.blackboard.Blackboard.set('error_status', True)
            py_trees.blackboard.Blackboard.set('error_level', 'Critical')
            py_trees.blackboard.Blackboard.set('error_cause', NavigationPause.URI)
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.SUCCESS




