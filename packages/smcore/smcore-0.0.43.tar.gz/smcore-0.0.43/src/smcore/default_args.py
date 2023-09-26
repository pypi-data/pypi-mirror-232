import argparse
from . import types_pb2 as pb2
from google.protobuf import json_format

# ----------------------------------------
# default_args provides a minimal argument parser to start an agen 
# We need to provide invocation bindings that automatically
# account for dispatches from controller.  All of the currently
# configured runners that can call python will pass the following
# to the CLI:
#
#     - Agent spec (in JSON) --spec={...}
#     - Blackboard addr      --bb="localhost:8080"
#
# If you're modifying this code, make sure the runner that will
# dispatch your job will pass these arguments (or the arguments that
# you specify).  But note that an AgentSpec and a Blackboard address
# are required to start any agent.
def default_args(agent_filename):
    parser = argparse.ArgumentParser(prog=agent_filename)
    parser.add_argument('--spec', help="full agent spec in JSON")
    parser.add_argument('--blackboard', help="hostname:port of the blackboard to connect to")
    args = parser.parse_args()
    
    agent_spec = json_format.Parse(args.spec, pb2.AgentSpec())
    return (agent_spec, args.blackboard)
