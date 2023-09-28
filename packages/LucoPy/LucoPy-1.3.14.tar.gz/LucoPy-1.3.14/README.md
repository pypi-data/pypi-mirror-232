# LucoPy

Python SDK to interact with the Luco API.

Contact: support@lu.co

---

## How to Use

Install the latest version from PyPI using PIP

```bash
pip install LucoPy
```

Or, specify a version

```bash
pip install LucoPy==x.x.x
```

Import the LucoApi class from the LucoPy library in your script and create an object of this class by passing in the API base url and the appropriate credentials. E.g.

```bash
from LucoPy import LucoApi

api = LucoApi(base_url, tenant_id, client_id, client_secret, resource_id)
```

---

## Authentication

In order to make calls to the API endpoints, LucoPy must be able to generate an authenticated access token. Authentication is managed by the ApiCore class using an identity provided during the instantiation of the LucoApi object.

### Azure Service Principal

If the Luco instance is hosted on Azure, a service principal can be used to authenticate to the API. In order to use a service principal, an App Registration must be created in the same Azure subscription as the Luco instance. The required credentials must then be passed as arguments to the LucoApi class when instantiating it. These credentials are:

- `tenant_id` - Directory (tenant) ID of the App Registration representing LucoPy
- `client_id` - Application (client) ID of the App Registration representing LucoPy
- `client_secret` - Secret value of the App Registration representing LucoPy
- `resource_id` - Application (client) ID of the target App Registration representing the API

If these values are not passed as direct arguments to the LucoApi class, the object will look for the following environment variables:

- LUCO_TENANT_ID
- LUCO_CLIENT_ID
- LUCO_CLIENT_SECRET
- LUCO_RESOURCE_ID

### Other Identities

Any custom identity object can be passed into the LucoApi class via the `identity` kwarg when instantiating the LucoApi class. This idenity object must have a method called `generate_token()` which returns an access token validated to the API and the expiry datetime of this token.

---

### LucoApi Class

`LucoApi(base_url=None, tenant_id=None, client_id=None, client_secret=None, resource_id=None, identity=None, timeout=20, log=False)`

This class acts as the gateway to the Luco platform. An instance of this class should be created at the beginning of each script, API calls are then made through the ApiCore which handles the necessary authentication.

The base URL of the API instance must be passed as a parameter to this object, or as an environment variable called LUCO_BASE_URL, along with the method of authentication.

The `timeout` option defines the maximum time (seconds) to wait for an HTTPS response from the API before causing a failure.

Use the `log` argument to turn logging on or off. Logs are generated and sent to a log.txt file in the base directory alongside where the script is being run.

1) `find_slot_id(tag, slot_sequence)`

    Find slot id from a tag/date and slot sequence definition. If the slot sequence does not have an active delivery schedule and a new tag is provided - a new slot will be created with this tag and the id of this slot will be returned.

    Args:
    - tag (str) : Date(time) (ISO 8601) for scheduled deliveries or unique tag for unscheduled deliveries
    - slot_sequence (dict) : Slot sequence name as key:value pairs. Order matters - this determines parameter position.

    Returns:
    - slot_id (int)

2) `get_submission(slot_id, submission_id)`

    Returns a submission object representing an existing submission.

    Args:
    - slot_id (int)
    - submission_id (int)

    Returns:
    - submission (Submission)

3) `create_submission(slot_id)`

    Create a submission against a slot and returns a Submission object representing it. Optionally provide stage and run environment details upon creation.

    Args:
    - slot_id (int)
    - stage (string) : Optional
    - run_environment (dict or list of dicts) : Optional

    Returns:
    - submission (Submission)

4) `find_submission_in_slot_sequence(slotId, submissionId, OnlyCompletedSubmissions=False, TimeDifference=None, FindClosest='historic')`

    Returns a Slot and Submission ID and whether it is an exact match based on the search criteria, and what the relative difference is in terms of time and number of slots.

    Args:
    - slot_id (int)
    - submission_id (int)
    - OnlyCompletedSubmissions (bool)
    - TimeDifference (str) : d:HH:MM:SS
    - FindClosest (str) : historic, future, either or exact

    Returns:
    - Response JSON (dict)

5) `find_submissions_by_slot_sequence(slotSequence, onlyLatestSlot=True, onlyDeliveredSlots=True, onlyCompletedSubmissions=True, onlyLatestSubmission=True, expectedAfterUtc=None, expectedBeforeUtc=None)`

    Returns submissions and their slots for a slot sequence

    Args:
    - slotSequence (dict or list of k:v pairs (dicts))
    - onlyLatestSlot (bool)
    - onlyDeliveredSlots (bool)
    - onlyCompletedSubmissions (bool)
    - onlyLatestSubmission (bool)
    - expectedAfterUtc (str) : YYYY-MM-DD or YYYY-MM-DDThh:mm:ss
    - expectedBeforeUtc (str) : YYYY-MM-DD or YYYY-MM-DDThh:mm:ss

    Returns:
    - Response JSON (dict)

6) `find_latest_submission_by_slot_sequence(slotSequence, expectedAfterUtc=None, expectedBeforeUtc=None)`

    Accessory method to find_submissions_by_slot_sequence(). Returns the slot id and submission id of the most recently completed submission on the slot sequence.

    Equivalent to:

    `find_submissions_by_slot_sequence(slotSequence, expectedAfterUtc=expectedAfterUtc, expectedBeforeUtc=expectedBeforeUtc)`

    Where the response JSON is interpreted to only return the slot id and submission id.

    Args:
    - slotSequence (dict or list of k:v pairs (dicts))
    - expectedAfterUtc (str) : YYYY-MM-DD or YYYY-MM-DDThh:mm:ss
    - expectedBeforeUtc (str) : YYYY-MM-DD or YYYY-MM-DDThh:mm:ss

    Returns:
    - slot_id (int), submission_id (int)

7) `submit_slot_sequences(slot_sequences, allow_overwrites=False, allow_archiving=False, ignore_delivery_config=False)`

    Import new or update existing slot sequences.

    Args:
    - slot_sequences (dict (JSON))
    - allow_overwrites (bool) : False
    - allow_archiving (bool) : False
    - ignore_delivery_config (bool) : False

    Retuns:
    - results (dict)

8) `export_slot_sequences(ids=None, names=None)`

    Export slot sequence configuration JSON file for one or more slot sequences.

    Args:
    - ids (int / list of ints) : slot sequence ids of slot sequences to export.
    - Or, names (dict or list) : slot sequence names to export

    Returns:
    - slot_sequences (JSON) : Array of slot sequence config dicts

9) `slot_sequences_overview()`

    Get overview of slot sequences. Use method args to filter and order the results. The available filters and information returned is equivalent to the slot sequence overview page in the Luco web app.

    All args are optional, default behaviour will be applied instead.

    WARNING: The size of the returned dictionary can get very large. Please use the `count` arg and filters to limit this. The method performs paginated requests to prevent timeout errors, this can be controlled with the `pagination_size` argument if necessary.

    Args:
    - count (int) : Number of slot sequences to return. Use `count=None` to return all slot sequences
    - pagination_size (int) : Default=250. Number of slot sequences returned by each API request
    - is_active (bool) : Default=True
    - type (string or list)
    - cadence (string or list)
    - overdue_count_start (int)
    - overdue_count_end (int)
    - failed_count_start (int)
    - failed_count_end (int)
    - slot_sequence_name_values (list of strings)
    - slot_sequence_name_values_filter_operator (string) : `'and'` or `'or'`
    - last_delivery_slot_start (string)
    - last_delivery_slot_end (string)
    - upcoming_slot_start (string)
    - upcoming_slot_end (string)
    - sort_by (string) : `'type'`, `'slotSequence'`, `'cadence'`, `'slots'`, `'overdue'`, `'failed'`, `'lastDelivery'`, `'upcoming'`
    - sort_dir (string) : `'asc'` or `'desc'`

    Returns:
    - slot_sequences (dict) : array of slot sequences and total count

10) `slots_overview()`

    Get overview of slots. Use method args to filter and order the results. The available filters and information returned is equivalent to the slots overview page in the Luco web app.

    All args are optional, default behaviour will be applied instead.

    WARNING: The size of the returned dictionary can get very large. Please use the `count` arg and filters to limit this. The method performs paginated requests to prevent timeout errors, this can be controlled with the `pagination_size` argument if necessary.

    Args:
    - count (int) : Number of slots to return. Use `count=None` to return all slots
    - pagination_size (int) : Default=1000. Number of slots returned by each API request
    - slot_id (int or list)
    - slot_sequence_id (int)
    - type (string or list)
    - cadence (string or list)
    - slot_status (string or list)
    - slot_sequence_name_values (string or list)
    - slot_sequence_name_values_filter_operator (string) : `'and'` or `'or'`
    - expected_by_start (string) : Datetime ISO 8601 in UTC
    - expected_by_end (string) : Datetime ISO 8601 in UTC
    - updated_on_start (string) : Datetime ISO 8601 in UTC
    - updated_on_end (string) : Datetime ISO 8601 in UTC
    - created_on_start (string) : Datetime ISO 8601 in UTC
    - created_on_end (string) : Datetime ISO 8601 in UTC
    - last_submission_status (string or list) : `CompletedWithoutFailures`, `CompletedWithFailures`, `Failed`, `InProgress`
    - sort_by (string) : `'type'`, `'slotSequence'`, `'cadence'`, `'submissions'`, `'status'`, `'slotId'`, `'expectedBy'`, `'updatedOn'`, `'createdOn'`
    - sort_dir (string) : `'asc'` or `'desc'`
    - min_submissions (int)
    - max_submissions (int)

    Returns:
    - slots (dict) : array of slots and total count

11) `slot_sequence_parameters()`

    Get the configuration parameters for a slot sequence.

    Args:
    - slot_sequence_name (dict)
    - group (str) : Optional. Parameter group to return
    - key (str) : Optional. Key within group to return the value of

    Returns:
    - result (dict or str)

### Submission Class

`Submission(slot_id, submission_id, core)`

Much of the functionality is handled at the Submission level. A Submission object is created by the `get_submission` or `create_submission` methods of the LucoApi class. These objects store the definition of the corresponding submission and handle methods relating to it.

1) `params(group=None, key=None)`

    Retrieve slot parameters. The `group` and `key` kwargs can be used to refine the response. Only use `key` in addition to `group`.

    Args:
    - group (str) : Parameter group to return
    - key (str) : Key within group to return the value of

    Returns:
    - result (dict or str)

2) `get_delivery_schedule()`

    Get the currently active delivery schedule. Retuns `None` if there are no active schedules .

    Returns:
    - delivery_schedule (dict)

3) `get_metrics(stages=None, metrics=None, group_by_stage=False)`

    Retrieve metrics from Submission.
    
    Filter by stage and metric by passing strings or lists of strings.
    Three different return formats:
        - list of dicts : Default behaviour. All metrics for filtered stages and metrics
        - dict : Metrics grouped by stage if kwarg group_by_stage=True
        - metric value : The value of the specified metric if stages and metrics are given as strings

    Args:
        - stages (string or list of strings)
        - metrics (string or list of strings)
        - group_by_stage (bool) : Group metrics by stage. Skips metrics which do not have a stage.

    Returns:
        - metrics (array, dict or metric value)

4) `get_quality() --> dict`

    Retrieve quality results

    Returns:
    - quality (dict)

5) `submit_run_environment(stage=None, run_environments=None)`

    Submit run environment details. For each run environment there are some fields which will be recognised by Luco.

    `platform` : The full name of the platform. E.g., `'Azure Data Factory'`, `'Azure Databricks'`.

    `referenceUrl` : A URL to link directly to the run environment. 

    Args:
    - stage (string) : Optional
    - run_environments (dict or list of dicts) : Required

    Returns:
    - response status (Bool) : Boolen success or failure

6) `submit_databricks_run_environment(spark, stage=None, raise_exception=False)`

    Extract databricks run environment details from spark object and submit to Luco.

    Args:
    - spark (pyspark.sql.session.SparkSession)
    - stage (string) : Optional
    - raise_exception (bool) : Raise an exception if method fails to extract and submit run environment details.

    Returns:
    - response status (Bool) : Boolen success or failure

7) `submit_metrics(stage, metric=None, value=None, metrics=None)`

    Submit metrics by passing a dict of metric : value pairs to `metrics`. Option to pass a single metric : value pair using `metric` and `value`. It is recommended to use `metrics`.

    Args:
    - stage (str)
    - metric (str) : Metric key
    - value (str) : Value of metric
    - metrics (dict) : Dictionary of Metric : Value pairs.

    Returns:
    - response status (Bool) : Boolen success or failure

8) `submit_quality(stage, tool=None, results=None, dataset=None, action=None)`

    Submit quality results. Supports 

    Args:
    - results (str)
    - stage (str) : Optional
    - tool (str) : Optional
    - dataset (str) : Optional
    - action (str) : Optional. `'Continued'` or `'Cancelled'`

    Returns:
    - response status (Bool) : Boolen success or failure

9) `submit_status(status, stage=None, type=None, message=None, modified_by=None)`

    Submit the status of the Submission

    Args:
    - status      (str) : `'Completed'`, `'Failed'` or `'In Progress'`
    - stage       (str) : Optional
    - type        (str) : Optional
    - message     (str) : Optional
    - modified_by (str) : Optional

    Returns:
    - response status (Bool) : Boolen success or failure

10) `submit_completed_status()`

    Submit a status for a completed submission. Equivalent to:
    `submit_status('Completed', 'Submission')`

    Returns:
    - response status (Bool) : Boolen success or failure

---

## Data Quality

This data quality module provides functionality to support the handling of data quality results. This module will support the conversion of DQ results from a variety of tools into a consistent format which can be submitted to Luco. This generic format is based around the concepts of **checks** and **collections**.

A **collection** is a dictionary object with the following structure:

```json
{
    "name": "string",
    "tool": "string",
    "toolVersion": "1.2.3",
    "referenceUrl": "<some-url>",
    "checks": [
        {
            "check": "expect $col1 to not be null", // Required
            "checkArgs": {
                "col1": "Id"
            },
            "success": true, // Required
            "onFail": {
                "ignore": true,
                "failedRecordsLink": "<link-to-blob-storage>"
            },
            "observed": {
                "elementCount": 10,
                "failedPercentage": "10.0%"
            },
            "referenceUrl": "<some-url>",
            "tags": [
                "Completeness"
            ],
            "metadata": {}
        }
    ],
    "start": "2022-10-04 10:00:00",
    "end": "2022-10-04 10:10:00",
    "metadata": {}
}
```

Using the `Submission.submit_quality()` method, DQ results can be submitted as either a single **check** or as a **collection** of checks.

### Fail conditions

Checks and Collections can have both a `success` and an `action` associated with them. `success` describes the result of the check i.e. did any records fail the check? Or, was the failure rate within an acceptable threshold? Every check must have a `success` value associated with it. 

`action` is an optional piece of metadata associated with a DQ check or collection. It describes what happens to the ongoing data process as a result of the success or failure of the data qualtity checks. For example, if the data fails some key checks then the `action` may be to cancel the data delivery process rather than continue with bad data.

The `onFail` field can be used to define what the `action` should be as a result of the `success` of DQ checks. This is a flexible field and custom logic can used to determine the `action` based on this field. 

The default behaviour is to ignore failed checks and continue the data delivery unless configured otherwise. If there should be a dependency on a check then this can be defined with:

```JSON
"onFail": {
    "action": "fail"
}
```

The `CheckResult` and `CollectionResult` objects have methods `is_exception_thrown()` which return True if there is a check which has `"success": False` and `"action": "fail"`. This is the method that is used if the kwarg `auto_determine_action` is `True` when `Submission.submit_quality()` is called.

### Great Expectations

The `great_expectations` submodule supports the handling of validation results from running expectations and suites against a dataframe.

Utility functions are provided to convert the validations results into a shape supported by Luco:

```python
import LucoPy.data_quality.great_expectations.utils as ge_utils

check = ge_utils.convert_expectation_to_check(expectation)

collection = ge_utils.convert_suite_to_collection(suite)
```

Where `expectation` and `suite` are the validation results as dict objects.

1) `convert_expectation_to_check(expectation_results, metadata_mappings={})`

    Convert an expectation validation result dict into a `CheckResult` object.

    Args:
    - expectation_results (dict) : Validation result dict
    - metadata_mappings (dict) : Custom mappings of key:value pairs in the `meta` field.

    Returns:
    - CheckResult

2) `convert_suite_to_collection(expectation_suite_results: dict, suite_mappings={}, expectation_mappings={})`

    Convert a suite validation result dict into a `CollectionResult` object.

    Args:
    - expectation_suite_results (dict) : Validation result dict
    - suite_mappings (dict) : Custom mappings of key:value pairs in the suite level `meta` field.
    - expectation_mappings (dict) : Custom mappings of key:value pairs in the expectation level `meta` fields.

    Returns:
    - CollectionResult

Data stored in the `meta` fields of the validation result objects can be mapped and then surfaced in the Luco UI. There are a number of *recognised fields* which Luco will detect and display differently to other metadata. The currently supported fields and their default custom mappings are:

Expectation Meta

| Recognised Field | Default Expected Name | Description |
|----------|----------|----------|
| onFail    | onFail    | Behaviour for when an expectation fails |
| referenceUrl   | referenceUrl    | URL linking to the expectation definition |
| tags   | tags    | Tags linked to the Data Quality Categories defined in Luco |

Expectation Suite Meta

| Recognised Field | Default Expected Name | Description |
|----------|----------|----------|
| toolVersion    | great_expectations_version    | Version of GE used |
| name    | expectation_suite_name    | Name of the expectation suite |
| start    | validation_time    | Datetime of when the validation was performed |
| referenceUrl   | referenceUrl    | URL linking to the expectation suite definition |
| tags   | tags    | Tags linked to the Data Quality Categories defined in Luco |

In order to implement custom mappings for these recognised fields, a dictionary of the custom mappings should be provided. E.g.

```python

# Keys should be the recognised fields
# Values should be the fields present in meta
expectation_mapping = {
    "onFail": "Action",
    "referenceUrl": "reference_url"
}

check = convert_expectation_to_check(expectation_result,
                                     metadata_mappings=expectation_mapping)
```

---

## Version History
LucoPy-1.3.14 : Feature: `include_duplicates` kwarg in `Submission.get_metrics()`. Bug fix: `'https'` validation in `LucoApi`.

LucoPy-1.3.13 : Bug fix: Pagination logic in `slot_sequence_overview` and `slots_overview` methods.

LucoPy-1.3.12 : Option to instantiate LucoApi using environment variables. New `Submission` method: `submit_databricks_run_environment`

LucoPy-1.3.11 : New `LucoApi` method: `slot_sequence_parameters`

LucoPy-1.3.10 : New `LucoApi` methods: `slot_sequence_overview` and `slots_overview`.

LucoPy-1.3.9 : Bug fix: get_quality() method.

LucoPy-1.3.8 : Bug fixes to great_expectations module and export_slot_sequences method.

LucoPy-1.3.7 : DQ module improvements. Define attributes of CheckResult and CollectionResult objects. Add `to_dict()` methods to construct dictionary of required and optional attributes which are not None. New method: LucoApi.export_slot_sequences.

LucoPy-1.3.6 : Refactor `Submission.get_metrics()` to remove breaking change. Added `group_by_stage` kwarg to group metrics.

LucoPy-1.3.5 : DQ module improvements. Add options to auto determine `action` and raise exception.

LucoPy-1.3.4 : Bug fix: Default expectation result format to 'BASIC' so it doesn't need to be explicity defined.

LucoPy-1.3.3 : Update return format of Submission.get_metrics() method. ~~Potential breaking change for users of the method~~ (Resolved in 1.3.6).

LucoPy-1.3.2 : DQ module improvements. Bug fixes around string rendering of expectation configurations and observed values.

LucoPy-1.3.1 : DQ module improvements. New method CollectionResult.is_exception_thrown().

LucoPy-1.3.0 : DQ module improvements. Support expectation results in JSON or Expectation format.

LucoPy-1.2.9 : Improvement to great_expectations handing in DQ module. Remove need to convert validation results to dict.

LucoPy-1.2.8 : Bug fix type checking in Submission.submit_quality() method.

LucoPy-1.2.7 : Introduction of a data_quality module with support for great_expectations. Added support for slot sequences defined as a single dict rather than list of dicts.

LucoPy-1.2.6 : Expose submission start and end times as attributes of the Submission object.

LucoPy-1.2.5 : New method to get submission delivery schedule, improved error handling and Custom exceptions. Expose current submission status.

LucoPy-1.2.4 : Bug fix for Submission.submit_metrics to allow a value of zero and catch incorrectly provided metric: value pairs.

LucoPy-1.2.3 : New method to import slot sequences. Some minor quality of life updates.

LucoPy-1.2.2 : Bug fix around unscheduled slots. More informative error handling.

LucoPy-1.2.1 : Updated `find_slot_id` method to use new POST /slots/ endpoint to create unscheduled slots. No change to user.

LucoPy-1.2.0 : First version hosted on PyPI.

---
