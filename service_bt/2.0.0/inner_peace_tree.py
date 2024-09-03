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
from ktmw_bt_interfaces.msg import TaskStatus, HRI

# ** Required **
SERVICE_NAME = 'Inner-peace-tree'
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
        
        py_trees.blackboard.Blackboard.set('hri_status', '')  


    def update(self):
        return py_trees.common.Status.SUCCESS

def check_map_gen_mode():

    seq = py_trees.composites.Sequence()
    
    check_hri_service = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'check_installation_mode',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value="installation_mode",
            operator=operator.eq
        )
    )    

    go_to_installation_mode = EnqueueNextService( service_name='installation_tree', service_version='2.0.0')

    seq.add_children([check_hri_service, go_to_installation_mode])

    return seq

def check_service_mode():

    seq = py_trees.composites.Sequence()
    
    check_hri_service = py_trees.behaviours.WaitForBlackboardVariableValue(
        name= 'check_service_mode',
        check=py_trees.common.ComparisonExpression(
            variable="hri_status",
            value="service_mode",
            operator=operator.eq
        )
    )    

    go_to_idle_mode = EnqueueNextService( service_name='idle_tree', service_version='2.0.0')

    seq.add_children([check_hri_service, go_to_idle_mode])

    return seq



def create_root():
  


    root_seq = py_trees.composites.Sequence('inner_peace_tree')

    root_par = py_trees.composites.Parallel(
            name="root_par",
            policy=py_trees.common.ParallelPolicy.SuccessOnAll(
                synchronise=False
            )
        )

    Inner_peace_start = Idling(name='Inner_peace_start')

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
                                action_target = 'engineer_tree',
                                action_result = True
                                )   
                            )
    
    BB_start = BB_init()

    root_seq.add_children([BB_start, task_available_alarm, root_par, Inner_peace_start])

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


    root_par.add_children([user_input_msgs_to_BB, check_map_gen_mode(), check_service_mode()])


    return root_seq

