import { createResourceApi } from "./http";

export const analyticsApi = {
  metrics: createResourceApi("/analytics/metrics/")
  dashboards: createResourceApi("/analytics/dashboards/"),
  widgets: createResourceApi("/analytics/widgets/"),
  reports: createResourceApi("/analytics/reporting/"),
  schedules: createResourceApi("/analytics/report-schedules/"),
  snapshots: createResourceApi("/analytics/snapshots/"),
  spendCubes: createResourceApi("/analytics/spend-cubes/"),
  supplierPerformance: createResourceApi("/analytics/supplier-performance/"),
  cycleTimes: createResourceApi("/analytics/order-cycle-times/"),
  rfqConversion: createResourceApi("/analytics/rfq-conversions/"),
  cohorts: createResourceApi("/analytics/cohorts/"),
  alerts: createResourceApi("/analytics/anomaly-alerts/"),
  exports: createResourceApi("/analytics/export-subscriptions/"),
  scorecards: createResourceApi("/analytics/executive-scorecards/"),
};
