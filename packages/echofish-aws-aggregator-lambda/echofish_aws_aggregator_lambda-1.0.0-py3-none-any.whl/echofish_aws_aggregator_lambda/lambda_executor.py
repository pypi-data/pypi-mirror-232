# lambda_executor.py

import json
import pandas as pd
from datetime import datetime
from botocore.exceptions import ClientError

TEMPDIR = "/tmp"


class LambdaExecutor:
    ############################################################################
    def __init__(
            self,
            s3_operations,
            dynamo_operations,
            sns_operations,
            table_name,
            done_topic_arn,
    ):
        self.__s3 = s3_operations
        self.__dynamo = dynamo_operations
        self.__sns_operations = sns_operations
        self.__table_name = table_name
        self.__done_topic_arn = done_topic_arn

    ############################################################################
    def __get_table_as_dataframe(
            self,
            ship_name,
            cruise_name,
            sensor_name,
    ) -> pd.DataFrame:
        print('get table as dataframe')
        try:
            print(self.__table_name)
            table = self.__dynamo.get_table(table_name=self.__table_name)
            # Note: table.scan() has 1 MB limit on results so pagination is used
            response = table.scan()
            data = response['Items']
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                data.extend(response['Items'])
        except ClientError as err:
            print('Problem finding the dynamodb table')
            raise err
        # Filter results when there are other cruises
        df = pd.DataFrame(data)  # TODO: this can be an expensive query if pulling all data
        df = df[
            (df['SHIP_NAME'] == ship_name) & (df['CRUISE_NAME'] == cruise_name) & (df['SENSOR_NAME'] == sensor_name)
        ]
        return df.sort_values(by='START_TIME', ignore_index=True)

    ############################################################################
    def __update_processing_status(
            self,
            file_name: str,
            cruise_name: str,
            pipeline_status: str,
            error_message: str = None,
    ):
        print(f"Updating processing status: {file_name}, {cruise_name}.")
        if error_message:
            print(f"Error message: {error_message}")
            self.__dynamo.update_item(
                table_name=self.__table_name,
                key={
                    'FILE_NAME': {'S': file_name},  # Partition Key
                    'CRUISE_NAME': {'S': cruise_name},  # Sort Key
                },
                attribute_names={
                    '#PT': 'PIPELINE_TIME',
                    '#PS': 'PIPELINE_STATUS',
                    '#EM': 'ERROR_MESSAGE',
                },
                expression='SET #PT = :pt, #PS = :ps, #EM = :em',
                attribute_values={
                    ':pt': {
                        'S': datetime.now().isoformat(timespec="seconds") + "Z"
                    },
                    ':ps': {
                        'S': pipeline_status
                    },
                    ':em': {
                        'S': error_message
                    }
                }
            )
        else:
            self.__dynamo.update_item(
                table_name=self.__table_name,
                key={
                    'FILE_NAME': {'S': file_name},  # Partition Key
                    'CRUISE_NAME': {'S': cruise_name},  # Sort Key
                },
                attribute_names={
                    '#PT': 'PIPELINE_TIME',
                    '#PS': 'PIPELINE_STATUS',
                },
                expression='SET #PT = :pt, #PS = :ps',
                attribute_values={
                    ':pt': {
                        'S': datetime.now().isoformat(timespec="seconds") + "Z"
                    },
                    ':ps': {
                        'S': pipeline_status
                    }
                }
            )
        print("Done updating processing status.")

    ############################################################################
    def __publish_done_message(
            self,
            message
    ) -> None:
        print("Sending done message")
        self.__sns_operations.publish(self.__done_topic_arn, json.dumps(message))

    ############################################################################
    def execute(self, input_message):
        ship_name = input_message['shipName']
        cruise_name = input_message['cruiseName']
        sensor_name = input_message['sensorName']
        file_name = input_message['fileName']
        #
        try:
            #########################################################################
            # [0] get dynamoDB table info
            df = self.__get_table_as_dataframe(ship_name, cruise_name, sensor_name)
            file_names = list(df['FILE_NAME'])
            ###################################################################
            completed_files = []
            failed_files = []
            processing_files = []
            #
            for select_file in file_names:
                current_status = list(df[df['FILE_NAME'] == select_file]['PIPELINE_STATUS'].values)[0]
                if current_status.find('SUCCESS_RESAMPLE_AND_WRITE_TO_ZARR_STORE') >= 0:
                    completed_files.append(select_file)
                elif current_status.find('FAIL') >= 0:
                    failed_files.append(select_file)
                else:
                    processing_files.append(select_file)
            # Don't want to send all the file names, just the counts
            if (len(completed_files) + len(failed_files)) == len(file_names):
                print('Completed files plus failed files is equal to all non-failure files.')
                # For the execution that has all files
                email_message = {
                    "completed_files": len(completed_files),
                    "processing_files": len(processing_files),  # TODO: this should(?) always be zero
                    "failed_files": len(failed_files),
                    # TODO: feature request is a list of the failed files included in the message
                    "shipName": ship_name,
                    "cruiseName": cruise_name,
                    "sensorName": sensor_name
                }
                # TODO: update statuses as DONE...
                for file_name in completed_files:  # REDUNDANT?
                    self.__update_processing_status(
                        file_name=file_name,
                        cruise_name=cruise_name,
                        pipeline_status='SUCCESS_AGGREGATOR',  # TODO: overwriting the dynamo error message???
                    )
                self.__publish_done_message(email_message)
            else:
                print(f'Signal from {file_name}, {len(completed_files)} successes, {len(failed_files)} failures, {len(processing_files)} processing.')
                return
            ###################################################################
            ###################################################################
        except Exception as err:
            print(f'Exception encountered: {err}')
            self.__update_processing_status(
                file_name=file_name,
                cruise_name=cruise_name,
                pipeline_status='FAILURE_AGGREGATOR',
                error_message=str(err),
            )
        finally:
            # Clean up
            print(f'Done processing {file_name}')
        #######################################################################
