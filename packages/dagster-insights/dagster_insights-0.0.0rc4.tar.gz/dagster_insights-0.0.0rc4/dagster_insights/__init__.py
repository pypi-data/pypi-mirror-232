from typing import Any, Dict, Generator, List, NamedTuple, Optional

import dagster._check as check
from dagster import AssetObservation, OpExecutionContext
from dagster_cloud import DagsterCloudAgentInstance
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .exceptions import DagsterInsightsError
from .query import PUT_CLOUD_METRICS_MUTATION


def chunks(chunk_list: List[Any], length: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(chunk_list), length):
        yield chunk_list[i : i + length]


class DagsterMetric(NamedTuple):
    """This class gives information about a Metric.

    Args:
        metric_name (str): name of the metric
        metric_value (float): value of the metric
    """

    metric_name: str
    metric_value: float


def put_asset_metrics(
    url: str,
    token: str,
    run_id: str,
    step_key: str,
    code_location_name: str,
    repository_name: str,
    asset_key: str,
    metrics: List[DagsterMetric],
    asset_group: Optional[str] = None,
) -> None:
    """Store metrics in the dagster cloud metrics store. This method is useful when you would like to
    store run, asset or asset group materialization metric data to view in the insights UI.

    Currently only supported in Dagster Cloud

    Args:
        metrics (List[DagsterMetric]): metrics to store in the dagster metrics store
    """
    check.list_param(metrics, "metrics", of_type=DagsterMetric)
    check.str_param(url, "url", url)
    check.str_param(token, "token", token)
    check.str_param(run_id, "run_id", run_id)
    check.str_param(step_key, "step_key", step_key)
    check.str_param(asset_key, "run_id", asset_key)
    check.str_param(code_location_name, "code_location_name", code_location_name)
    check.str_param(repository_name, "repository_name", repository_name)
    check.opt_str_param(asset_group, "asset_group", asset_group)

    transport = RequestsHTTPTransport(
        url=url,
        use_json=True,
        timeout=300,
        headers={"Dagster-Cloud-Api-Token": token},
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    metric_graphql_inputs = []

    metric_graphql_inputs.append(
        {
            "runId": run_id,
            "stepKey": step_key,
            "codeLocationName": code_location_name,
            "repositoryName": repository_name,
            "assetMetricDefinitions": [
                {
                    "assetKey": asset_key,
                    "assetGroup": asset_group,
                    "metricValues": [
                        {
                            "metricValue": metric_def.metric_value,
                            "metricName": metric_def.metric_name,
                        }
                        for metric_def in metrics
                    ],
                }
            ],
        }
    )
    client.execute(
        gql(PUT_CLOUD_METRICS_MUTATION), variable_values={"metrics": metric_graphql_inputs}
    )


def put_context_metrics(
    context: OpExecutionContext,
    metrics: List[DagsterMetric],
) -> None:
    """Store metrics in the dagster cloud metrics store. This method is useful when you would like to
    store run, asset or asset group materialization metric data to view in the insights UI.

    Currently only supported in Dagster Cloud

    Args:
        metrics (List[DagsterMetric]): metrics to store in the dagster metrics store
    """
    check.list_param(metrics, "metrics", of_type=DagsterMetric)
    check.inst_param(context, "context", OpExecutionContext)
    if not isinstance(context.instance, DagsterCloudAgentInstance):
        context.log.info("dagster instance is not a DagsterCloudAgentInstance, skipping metrics")
        return

    if context.instance.organization_name != "test":
        transport = RequestsHTTPTransport(
            url=f"{context.instance.dagit_url}graphql",
            use_json=True,
            timeout=300,
            headers={"Dagster-Cloud-Api-Token": context.instance.dagster_cloud_agent_token},
        )
    else:
        transport = RequestsHTTPTransport(
            url=f"http://127.0.0.1:3000/{context.instance.organization_name}/staging/graphql",
            use_json=True,
            timeout=300,
            headers={"Dagster-Cloud-Api-Token": context.instance.dagster_cloud_agent_token},
        )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    metric_graphql_inputs = []

    if context.dagster_run.external_job_origin is None:
        raise DagsterInsightsError("dagster run for this context has not started yet")

    context.log.info(
        {
            "codeLocationName": context.dagster_run.external_job_origin.location_name,
            "repositoryName": (
                context.dagster_run.external_job_origin.external_repository_origin.repository_name
            ),
        }
    )

    if context.has_assets_def:
        for selected_asset_keys in chunks(list(context.selected_asset_keys), 5):
            context.log.info(selected_asset_keys[0].to_python_identifier())
            metric_graphql_inputs.append(
                {
                    "runId": context.run_id,
                    "stepKey": context.get_step_execution_context().step.key,
                    "codeLocationName": context.dagster_run.external_job_origin.location_name,
                    "repositoryName": (
                        context.dagster_run.external_job_origin.external_repository_origin.repository_name
                    ),
                    "assetMetricDefinitions": [
                        {
                            "assetKey": selected_asset_key.to_python_identifier(),
                            "assetGroup": context.assets_def.group_names_by_key.get(
                                selected_asset_key, None
                            ),
                            "metricValues": [
                                {
                                    "metricValue": metric_def.metric_value,
                                    "metricName": metric_def.metric_name,
                                }
                                for metric_def in metrics
                            ],
                        }
                        for selected_asset_key in selected_asset_keys
                    ],
                }
            )
    else:
        metric_graphql_inputs.append(
            {
                "runId": context.run_id,
                "stepKey": context.get_step_execution_context().step.key,
                "codeLocationName": context.dagster_run.external_job_origin.location_name,
                "repositoryName": (
                    context.dagster_run.external_job_origin.external_repository_origin.repository_name
                ),
                "jobMetricDefinitions": [
                    {
                        "metricValues": [
                            {
                                "metricValue": metric_def.metric_value,
                                "metricName": metric_def.metric_name,
                            }
                            for metric_def in metrics
                        ],
                    }
                ],
            }
        )
    for metric_graphql_inputs in chunks(metric_graphql_inputs, 5):
        try:
            result = client.execute(
                gql(PUT_CLOUD_METRICS_MUTATION), variable_values={"metrics": metric_graphql_inputs}
            )
        except Exception as exc:
            context.log.error(f"failed to store metrics with error {exc}")
            return
        if (
            result["CreateOrUpdateExtenalMetrics"]["__typename"]
            != "CreateOrUpdateExternalMetricsSuccess"
        ):
            context.log.error(
                "failed to store metrics with error"
                f" {result['CreateOrUpdateExtenalMetrics']['message']}"
            )

    context.log.info("successfully stored metrics")


def store_dbt_adapter_metrics(
    context: OpExecutionContext,
    manifest: Dict[Any, Any],
    run_results: Dict[Any, Any],
) -> Generator[AssetObservation, Any, Any]:
    check.inst_param(context, "context", OpExecutionContext)
    check.dict_param(manifest, "manifest")
    check.dict_param(run_results, "run_results")

    if not isinstance(context.instance, DagsterCloudAgentInstance):
        context.log.info("dagster instance is not a DagsterCloudAgentInstance, skipping metrics")
        return

    if context.instance.organization_name != "test":
        transport = RequestsHTTPTransport(
            url=f"{context.instance.dagit_url}graphql",
            use_json=True,
            timeout=300,
            headers={"Dagster-Cloud-Api-Token": context.instance.dagster_cloud_agent_token},
        )
    else:
        transport = RequestsHTTPTransport(
            url=f"http://127.0.0.1:3000/{context.instance.organization_name}/staging/graphql",
            use_json=True,
            timeout=300,
            headers={"Dagster-Cloud-Api-Token": context.instance.dagster_cloud_agent_token},
        )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    if context.dagster_run.external_job_origin is None:
        raise DagsterInsightsError("dagster run for this context has not started yet")
    assetMetricDefinitions = []
    for result in run_results["results"]:
        node = manifest["nodes"][result["unique_id"]]
        metric_values = []
        assetKey = next(
            iter(
                filter(
                    lambda asset_key: asset_key.path[-1] == node["name"],
                    context.selected_asset_keys,
                )
            )
        )
        for adapter_response_key in result["adapter_response"]:
            if adapter_response_key in ["_message", "code"]:
                continue
            if adapter_response_key == "query_id":
                yield AssetObservation(
                    asset_key=assetKey,
                    metadata={"query_id": result["adapter_response"][adapter_response_key]},
                )
            metric_values.append(
                {
                    "metricValue": result["adapter_response"][adapter_response_key],
                    "metricName": adapter_response_key,
                }
            )

        assetMetricDefinitions.append(
            {
                "assetKey": assetKey.to_python_identifier(),
                "assetGroup": context.assets_def.group_names_by_key.get(assetKey, None),
                "metricValues": metric_values,
            }
        )
    metric_graphql_inputs = []
    for assetMetricDefinitions in chunks(assetMetricDefinitions, 5):
        metric_graphql_inputs.append(
            {
                "runId": context.run_id,
                "stepKey": context.get_step_execution_context().step.key,
                "codeLocationName": context.dagster_run.external_job_origin.location_name,
                "repositoryName": (
                    context.dagster_run.external_job_origin.external_repository_origin.repository_name
                ),
                "assetMetricDefinitions": assetMetricDefinitions,
            }
        )
    for metric_graphql_inputs in chunks(metric_graphql_inputs, 5):
        try:
            result = client.execute(
                gql(PUT_CLOUD_METRICS_MUTATION), variable_values={"metrics": metric_graphql_inputs}
            )
        except Exception as exc:
            context.log.error(f"failed to store metrics with error {exc}")
            return
        if (
            result["CreateOrUpdateExtenalMetrics"]["__typename"]
            != "CreateOrUpdateExternalMetricsSuccess"
        ):
            context.log.error(
                "failed to store metrics with error"
                f" {result['CreateOrUpdateExtenalMetrics']['message']}"
            )

    context.log.info("successfully stored metrics")
