"""
Objects in videos are detected using the OnePanel API.

It is assumed that videos have been uploaded to an S3 bucket with a path something like:
s3://cnas-re.uog.onepanel.io/Guam01/20201008/

Output from the object detection processing will be deposited in:
s3://cnas-re.uog.onepanel.io/Guam01/20201008/output/

The S3 output bucket is synced with a directory on the local machine using something like:
aws s3 sync s3://cnas-re.uog.onepanel.io/Guam01/20201008/output/ /home/aubrey/Desktop/Guam01/20201008/output/
--exclude "*.mp4"

The sync request is repeated every 10 minutes until all CVAT XML files have been downloaded or a mximum time of 3 hours
has expired.
"""

import glob
import onepanel.core.api
from onepanel.core.api.rest import ApiException
from onepanel.core.api.models import Parameter
import os
import logging
from time import sleep
import subprocess
import plac
import sys


def execute_workflow(input_video='Rota01/20201013_145205.mp4', output_dir='Rota01/output/'):
    """
    Doc coming soon.
    """
    auth_token = os.environ['ONEPANEL_AUTHORIZATION']
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
            logging.info("Successfully executed workflow.")
            # sys.exit(0)
        except ApiException as e:
            logging.error("Exception when calling WorkflowServiceApi->create_workflow_execution: {}\n".format(e))
            sys.exit(1)


@plac.opt('datadir', abbrev='dd')
@plac.opt('videodate', abbrev='d')
def main(videodate=20201012, datadir='/home/aubrey/Desktop/Guam01'):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(funcName)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[logging.StreamHandler()])

    logging.info('Uploading videos to Amazon S3 storage')
    survey_name = datadir.split('/')[-1]
    s3_output_dir = f'{survey_name}/{videodate}/output/'
    from_dir = f'{datadir}/{videodate}/'  # local machine
    to_dir = f's3://cnas-re.uog.onepanel.io/{survey_name}/'  # s3 bucket
    output = subprocess.run(['aws', 's3', 'sync', from_dir, to_dir, '--exclude', '*original.mp4', '--exclude', '*.csv'])
    logging.info(f'subprocess response: {output}')

    logging.info('Detecting objects in videos on a OnePanel cloud computer')
    video_file_list = glob.glob(f'{datadir}/{videodate}/{videodate}_??????.mp4')
    video_file_count = len(video_file_list)
    for filepath in video_file_list:
        s3_input_video = f'{survey_name}/{os.path.basename(filepath)}'
        logging.debug(f'input_video={s3_input_video}, output_dir={s3_output_dir}')
        execute_workflow(input_video=s3_input_video, output_dir=s3_output_dir)

    logging.info('Downloading object detection results (CVAT XML files)')
    ntries = 0
    maxtries = 18  # 3 hours
    while True:
        from_dir = f's3://cnas-re.uog.onepanel.io/{s3_output_dir}'  # Bucket on s3
        to_dir = f'{datadir}/{videodate}'  # Destination dir on local machine
        output = subprocess.run(['aws', 's3', 'sync', from_dir, to_dir, '--exclude', '*.mp4'])
        logging.info(f'subprocess response: {output}')
        ntries += 1
        if not os.path.exists(to_dir):
            logging.info(f'{to_dir} does not yet exist.')
        else:
            xml_file_list = glob.glob(f'{to_dir}/*xml')
            xml_file_count = len(xml_file_list)
            logging.info(f'{xml_file_count} of {video_file_count} xml files have been downloaded to {to_dir}')
            if xml_file_count == video_file_count:
                break
        if ntries == maxtries:
            logging.info('Aborting: maxtries reached.')
            sys.exit(1)
        logging.info('Sleeping for 10 minutes.')
        sleep(600)  # sleep for 10 minutes


# MAIN

if __name__ == '__main__':
    import plac;

    plac.call(main)
