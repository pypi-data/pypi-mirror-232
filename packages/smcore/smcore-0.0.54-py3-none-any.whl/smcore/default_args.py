import os
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

    # TODO: pick better defaults.  If a user tries to run without values,
    #       we should give a sane error message, not traceback
    blackboard = "localhost:8080"
    agent_spec = None
    if args.spec != None:

        spec_string = args.spec
        
        # Check if user is passing a spec file vs json
        if os.path.exists(args.spec):
            with open(args.spec, "r") as f:
                spec_string = f.read()
                print("agent spec read from file:\n", spec_string)
            
        agent_spec = json_format.Parse(spec_string, pb2.AgentSpec())
    else:
        print('No agent spec provided.  Defaulting to {"name":"new-agent"}')
        print('If this is a mistake, please provide an agent spec using the --spec option')
        print('More documentation on agent specs can be found here: ')
        
        default_spec = '{"name":"new-agent","pingIntervalMs":"1000","pollIntervalMs":"1000"}'
        
        agent_spec = json_format.Parse(default_spec, pb2.AgentSpec())
        
    if args.blackboard != None:
        blackboard = args.blackboard
    else:
        print('No blackboard specified. Defaulting to "localhost:8080"')
        print('If this is a mistake, please provide a blackboard address using the --blackboard option')
    
    return (agent_spec, blackboard)
