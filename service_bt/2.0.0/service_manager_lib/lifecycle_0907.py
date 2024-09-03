'''
KT Robot Middleware version 1.0.0

Copyright ⓒ 2022 kt corp. All rights reserved.

This is a proprietary software of kt corp, and you may not use this file except in
compliance with license agreement with kt corp. Any redistribution or use of this
software, with or without modification shall be strictly prohibited without prior written
approval of kt corp, and the copyright notice above does not evidence any actual or
intended publication of such software.
'''


import rclpy
import py_trees
import threading
from ktmw_srvmgr_interfaces.msg import Status, NodeStatus
from .btmgr import BehaviorTreeInstance
from .exceptions import LowPriorityError
from .governance import examine
from system_core_common.common import info

import time
from datetime import datetime 
import logging
now_time = datetime.now()

now_time_ = now_time.strftime('%Y-%m-%d %H:%M:%S')
file_n = f"/home/kt/LOG/log_bt_common_{now_time_}.log"
logging.basicConfig(filename=file_n, level=logging.DEBUG)


def pytrees_status_to_node_status(status: py_trees.common.Status):
    """
    Convert py_tree status to ros message status
    """
    ros_status = 0
    if status == py_trees.common.Status.SUCCESS:
        ros_status = NodeStatus.STATUS_SUCCESS
    elif status == py_trees.common.Status.FAILURE:
        ros_status = NodeStatus.STATUS_FAILURE
    else:
        ros_status = NodeStatus.STATUS_RUNNING
    return ros_status


class LifeCycleManager:
    """
    Behavior tree execution manager.
    """

    def __init__(self, node, rate=5, continuous=True):
        self._node = node
        self._rate = self._node.create_rate(rate)
        self._current_instance = None
        self._continuous = continuous
        self._instance_lock = threading.RLock()
        self._next_instance = None

        self._status_publisher = self._node.create_publisher(
            Status, 'ktmw_srvmgr/status', 10)

        self._executor = rclpy.executors.SingleThreadedExecutor()
        threading.Thread(target=self._executor.spin).start()

    def _generate_status_msg(self):
        active_nodes = self._current_instance.get_active_nodes()

        def generate_node_status(nodes):
            for node in nodes:
                msg = NodeStatus()
                msg.name = node.name
                msg.status = pytrees_status_to_node_status(node.status)
                yield msg

        node_statuses = [
            status for status in generate_node_status(active_nodes)]

        msg = Status()
        msg.time = self._node.get_clock().now().to_msg()
        msg.service_name = self._current_instance.name
        msg.service_version = self._current_instance.version
        msg.instance_id = self._current_instance.id
        msg.node_statuses = node_statuses
        return msg

    def _publish_status(self):
        msg = self._generate_status_msg()
        if msg.node_statuses != []:
            self._status_publisher.publish(msg)

    def _publish_root_status(self, status):
        root = self._current_instance.behaviour.root
        root_node_status = NodeStatus()
        root_node_status.name = root.name
        root_node_status.status = status

        msg = Status()
        msg.time = self._node.get_clock().now().to_msg()
        msg.service_name = self._current_instance.name
        msg.service_version = self._current_instance.version
        msg.instance_id = self._current_instance.id
        msg.node_statuses = [root_node_status]
        self._status_publisher.publish(msg)

    def _activate_instance(self, instance: BehaviorTreeInstance):
        instance.behaviour.setup()
        self._executor.add_node(instance.behaviour.node)
        instance.is_active = True

    def _deactive_instance(self, instance: BehaviorTreeInstance):
        # Terminate current working action nodes
        instance.behaviour.shutdown()
        instance.is_active = False
        self._executor.remove_node(instance.behaviour.node)

    def start(self):
        self._thread = threading.Thread(target=self.spin)
        self._thread.start()

    def spin(self):
        """
        Execution loop function
        """

        count = 0
        while True:
            exit_flag = False
            try:
                self._instance_lock.acquire()
                if self._current_instance is not None:
                    if self._current_instance.is_active:

                        self._current_instance.tick()

                        # Publish current node status
                        self._publish_status()

                        # # display current status
                        # self._node.get_logger().info('\n' + py_trees.display.unicode_tree(
                        #     self._current_instance.behaviour.root, show_status=True))

                        if count == 17 : 
                            logging.debug("------------------------------")
                            logging.debug('\nUNICODE\n' + py_trees.display.unicode_tree(self._current_instance.behaviour.root, show_status=True))

                            count = 0

                        count +=1

                        # if self._previous_instance is not self._current_instance:

                        #     logging.debug("IS------------------------------")
                        #     logging.debug('\nUNICODE\n' + py_trees.display.unicode_tree(self._current_instance.behaviour.root, show_status=True))      
                        #     self._deactive_instance(self._previous_instance)


                        # import difflib
                        # sm = difflib.SequenceMatcher(None, str(self._next_instance), (self._current_instance))
                        # ratio = sm.ratio()
                        # if ratio != 1:
                        #     logging.debug("Ratio------------------------------")
                        #     logging.debug('\nUNICODE\n' + py_trees.display.unicode_tree(self._current_instance.behaviour.root, show_status=True))       



                        # check working state
                        root_status = self._current_instance.behaviour.root.status
                        self._node.get_logger().info(
                            'Status of [%s]: [%s]' % (self._current_instance.name, root_status))

                        if root_status == py_trees.common.Status.SUCCESS:
                            msg = 'Behavior tree has completed. service_name: [{}]'.format(
                                self._current_instance.name)
                            self._node.get_logger().info(msg)
                            # info('service_manager', msg)
                        if root_status == py_trees.common.Status.FAILURE:
                            msg = 'Behavior tree has failed. service_name: [{}]'.format(
                                self._current_instance.name)
                            self._node.get_logger().info(msg)
                            # info('service_manager', msg)

                        if self._next_instance is not None:
                            
                            # info('service_manager', 'Switch behavior tree. current: [{}], next: [{}]'.format(
                            #     self._current_instance.name, self._next_instance.name))

                            self._previous_instance = self._current_instance
                            self._deactive_instance(self._current_instance)
                            self._current_instance = self._next_instance
                            self._next_instance = None
                            self._activate_instance(self._current_instance)


                        if not self._continuous:
                            if root_status == py_trees.common.Status.SUCCESS or root_status == py_trees.common.Status.FAILURE:
                                exit_flag = True

            except Exception as e:
                self._node.get_logger().error("Any Behaviour threw exception : {}.".format(e))
                if self._current_instance is not None and self._current_instance.is_active:
                    last_running_behaviour = self._current_instance.behaviour.tip()
                    if last_running_behaviour is not None: 
                        if last_running_behaviour.has_parent_with_instance_type(py_trees.composites.Parallel) or \
                            isinstance(last_running_behaviour, py_trees.composites.Parallel):
                            # if a last running behaviour is under parallel, others could also occurs exception.
                            while last_running_behaviour is not None:
                                if isinstance(last_running_behaviour, py_trees.composites.Parallel):
                                    break
                                last_running_behaviour = last_running_behaviour.parent

                            last_running_behaviours = last_running_behaviour.children
                            self._node.get_logger().info("Last running behaviour is in parallel : {}".format(last_running_behaviour.name))
                            self._node.get_logger().info("Last running behaviours : ")
                            for last_running_behaviour in last_running_behaviours:
                                self._node.get_logger().info("\tBehaviour name : {}".format(last_running_behaviour.name))
                                self._node.get_logger().info("\tBehaviour status : {}\n".format(last_running_behaviour.status))
                        else:
                            self._node.get_logger().info("Last running behaviour name : {}".format(last_running_behaviour.name))
                            self._node.get_logger().info("Last running behaviour status : {}\n".format(last_running_behaviour.status))
                    else:
                        self._node.get_logger().info("Could not track last running behaviours...")
            finally:
                self._instance_lock.release()

            if exit_flag:
                break

            try:
                self._rate.sleep()
            except rclpy.exceptions.ROSInterruptException:
                self._node.get_logger().warning('Lifecycle loop interrupted.')
                break

    def execute(self, instance: BehaviorTreeInstance, priority: int):
        """
        Execute given behavior tree instance with priority check.
        """
        try:
            self._instance_lock.acquire()
            if self._current_instance is not None:
                if self._current_instance.is_active:

                    # Examine governance
                    examine(instance, self._current_instance)

                    self._deactive_instance(self._current_instance)
                    self._node.get_logger().info(
                        'Behavior [%s] stopped.' % self._current_instance.name)
                    info('service_manager',
                         'Behavior [%s] stopped.' % self._current_instance.name)
                    # Publish stopped tree status
                    self._publish_root_status(NodeStatus.STATUS_STOPPED)
            self._current_instance = instance
            self._current_instance.set_priority(priority)
            self._activate_instance(self._current_instance)
        finally:
            self._instance_lock.release()

    def enqueue(self, instance: BehaviorTreeInstance, priority: int):
        """
        Enqueue next execution service
        """
        self._next_instance = instance
        self._next_instance.set_priority(priority)

    def halt(self, priority):
        """
        Terminate current running tree.
        """
        try:
            self._instance_lock.acquire()
            if self._current_instance is not None:
                if self._current_instance.is_active:
                    if self._current_instance.priority > priority:
                        raise LowPriorityError()
                    self._deactive_instance(self._current_instance)
                    self._node.get_logger().info(
                        'Behavior [%s] stopped.' % self._current_instance.name)
                    info('service_manager',
                         'Behavior [%s] stopped.' % self._current_instance.name)
                    # Publish stopped tree status
                    self._publish_root_status(NodeStatus.STATUS_STOPPED)
        finally:
            self._instance_lock.release()

    def get_status(self):
        """
        Get current running status
        """
        msg = None
        try:
            self._instance_lock.acquire()
            if self._current_instance is not None:
                if self._current_instance.is_active:
                    msg = self._generate_status_msg()
        finally:
            self._instance_lock.release()
        return msg

    def shutdown(self):
        self._executor.shutdown()