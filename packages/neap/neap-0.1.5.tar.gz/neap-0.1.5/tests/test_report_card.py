import unittest

from neap.report_card import ReportCard

class TestReportCard(unittest.TestCase):

    def test_get_adhoc_data(self):
        report_card_api = ReportCard(api_key="YOUR_API_KEY")
        data = report_card_api.get_adhoc_data(assessment_year=2023, subject="Math", grade=8, subscale="NAEP_Math_Achievement")

        self.assertEqual(data[0]["AssessmentYear"], 2023)
        self.assertEqual(data[0]["Subject"], "Math")
        self.assertEqual(data[0]["Grade"], 8)
        self.assertEqual(data[0]["Subscale"], "NAEP_Math_Achievement")

if __name__ == "__main__":
    unittest.main()