import unittest
import spacy

from ..stylo_metrix.structures.language import Lang
from ..stylo_metrix.tools.metric_tools import get_all_metrics, get_all_categories, custom_metric
from ..stylo_metrix.stylo_metrix import StyloMetrix


class TestMetrics(unittest.TestCase):
    def test_all_metrics(self):
        test_text = 'You are a very nice person. I like you very much.'
        languages = Lang.get_all_languages()

        for lang_id in languages:
            lang = languages[lang_id]
            lang_name = lang.definitions[0]

            sm = StyloMetrix(lang_name, debug=True)

            values, debug = sm.transform([test_text]*10)

            

            # self.assertTrue()
            
            # for metric in metrics:
            #     metric.set_nlp(nlp)
            #     metric_value, metric_debug = metric(test_doc)
            #     self.assertTrue(metric_value <= 1.0 and metric_value >= 0.0, msg=f'Language: {lang_name}, Metric: {metric.code}, Value: {metric_value}')
            #     self.assertTrue(len(metric_debug) >= 0, msg=f'Language: {lang_name}, Metric: {metric.code}, Debug: {metric_debug}')