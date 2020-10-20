import json


class Metric:
    @classmethod
    def from_json(cls, dct):
        return cls(dct["x_axis"], dct["x_value"], dct["metric"], dct["value"])

    def __init__(self, x_axis, x_value, metric, value):
        """

        :param x_axis:
        :type x_axis str
        :param x_value:
        :type x_value float
        :param metric:
        :type metric str
        :param value:
        :type value float
        """
        self.x_axis = x_axis
        self.x_value = x_value
        self.metric = metric
        self.value = value


class MetricSummary:
    @classmethod
    def from_json(cls, dct):
        metrics = [Metric.from_json(raw_metric) for raw_metric in json.loads(dct["summaryData"])]
        summary = cls(dct["metric"], dct["displayOrder"], dct["xAxis"], dct["xStartValue"], dct["xFinalValue"],
                      dct["metricStartValue"], dct["metricFinalValue"], dct["dataUrl"], metrics)

        return summary

    def __init__(self, metric, display_order, x_axis, x_start_value,
                 x_final_value, metrics_start_value, metrics_final_value,
                 data_url, summary_data):
        """

        :param metric:
        :type metric str
        :param display_order:
        :type display_order int
        :param x_axis:
        :type x_axis str
        :param x_start_value:
        :type x_start_value float
        :param x_final_value:
        :type x_final_value float
        :param metrics_start_value:
        :type metrics_start_value float
        :param metrics_final_value:
        :type metrics_final_value float
        :param data_url:
        :type data_url str
        :param summary_data:
        :type summary_data list[Metric]
        """
        self.metric = metric
        self.display_order = display_order
        self.x_axis = x_axis
        self.x_start_value = x_start_value
        self.x_final_value = x_final_value
        self.metric_start_value = metrics_start_value
        self.metric_final_value = metrics_final_value
        self.data_url = data_url
        self.summary_data = summary_data

