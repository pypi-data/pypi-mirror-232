PUT_CLOUD_METRICS_MUTATION = """
mutation CreateOrUpdateExtenalMetrics(
  $metrics: [ExternalMetricInputs]!) {
  createOrUpdateExternalMetrics(metrics: $metrics) {
    __typename
    ... on CreateOrUpdateExternalMetricsSuccess {
      status
      __typename
    }
    ...MetricsFailedFragment
    ...UnauthorizedErrorFragment
    ...PythonErrorFragment
  }
}
fragment PythonErrorFragment on PythonError {
  __typename
  message
  stack
  causes {
    message
    stack
    __typename
  }
}
fragment MetricsFailedFragment on CreateOrUpdateExternalMetricsFailed {
  __typename
  message
}
fragment UnauthorizedErrorFragment on UnauthorizedError {
  __typename
  message
}
"""
