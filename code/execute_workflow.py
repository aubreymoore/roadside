"""
Modified by Aubrey Moore 2020-10-13

Needs to run in local venv

"""
import onepanel.core.api
from onepanel.core.api.rest import ApiException
from onepanel.core.api.models import Parameter
import os
import sys
import plac

@plac.opt('input_video', abbrev='i')
@plac.opt('output_dir', abbrev='o')
def main(input_video='Rota01/20201013_145205.mp4', output_dir='Rota01/output/'):
    """
    Doc coming soon.
    """
    auth_token = os.getenv('ONEPANEL_AUTHORIZATION')
    configuration = onepanel.core.api.Configuration(
        host="https://app.cnas-re-uog.onepanel.io/api",
        api_key={'Bearer': auth_token})
    configuration.api_key_prefix['Bearer'] = 'Bearer'

    # Enter a context with an instance of the API client
    with onepanel.core.api.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = onepanel.core.api.WorkflowServiceApi(api_client)
        namespace = "crb"  # str |
        params = []
        params.append(Parameter(name="input-video", value=input_video))
        # params.append(Parameter(name="gps-csv-path", value=sys.argv[2]))
        # you can add more parameters but they are optional. here is an example.
        # you can change how many frame sto skip, by default its 7
        params.append(Parameter(name='skip-no', value="1"))
        params.append(Parameter(name="output-path", value=output_dir))

        body = onepanel.core.api.CreateWorkflowExecutionBody(parameters=params,
                                                             workflow_template_uid="process-inference")
        try:
            api_response = api_instance.create_workflow_execution(namespace, body)
            print("Successfully executed workflow.")
            sys.exit(0)
        except ApiException as e:
            print("Exception when calling WorkflowServiceApi->create_workflow_execution: {}\n".format(e))
            sys.exit(1)

if __name__ == '__main__':
    import plac; plac.call(main)
