from google.cloud import run_v2
from google.cloud import monitoring_v3
from . import mslarkin_utils
from . import gcp_utils
import statistics, time

def get_run_service(service, project_id, region):
    service_id = f"projects/{project_id}/locations/{region}/services/{service}"
    run_client = run_v2.ServicesClient()
    run_service = run_client.get_service(name=service_id)
    return run_service

def get_latest_revision(service, project_id, region):
    run_service = get_run_service(service=service, project_id=project_id, region=region)
    service_revision = gcp_utils.get_resource_from_path(run_service.latest_ready_revision)
    return service_revision

def get_service_url(service, project_id, region):
    run_service = get_run_service(service=service, project_id=project_id, region=region)
    return run_service.uri

def get_last_update_ts(service, project_id, region):
    run_service = get_run_service(service=service, project_id=project_id, region=region)
    return mslarkin_utils.get_pacific_timestamp(run_service.update_time)

def get_instance_count(service, project_id, region):
    if project_id == None:
        project_id = gcp_utils.get_project_id()
    
    if region == None:
        region = gcp_utils.get_gcp_region()

    monitoring_metric = "run.googleapis.com/container/instance_count"
    aggregation_s = 60
    interval_s = 180 # Instance count reporting delay up to 180s

    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10**9)

    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": seconds, "nanos": nanos},
            "start_time": {"seconds": (seconds - interval_s), "nanos": nanos},
        }
    )

    aggregation = monitoring_v3.Aggregation(
        {
            "alignment_period": {"seconds": aggregation_s},
            "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            "cross_series_reducer": monitoring_v3.Aggregation.Reducer.REDUCE_MAX,
            "group_by_fields": ["resource.labels.service_name"],
        }
    )

    metric_request = monitoring_v3.ListTimeSeriesRequest(
    name=project_name,
    filter=f'metric.type = "{monitoring_metric}" AND resource.labels.service_name = "{service}"',
    interval=interval,
    view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
    aggregation=aggregation,
)

    results = client.list_time_series(request=metric_request)
    metric_data = []

    for data_point in results.time_series[0].points:
        metric_value = data_point.value.double_value
        metric_data_point = metric_value
        metric_data.append(metric_data_point)
        
    return_val = round(statistics.fmean(metric_data))
    return return_val

    