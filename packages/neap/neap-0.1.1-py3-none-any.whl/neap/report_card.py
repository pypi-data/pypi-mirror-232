import requests

class ReportCard:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_adhoc_data(self, assessment_year, subject, grade, subscale):
        url = "https://api.neap.gov/api/GetAdhocData"
        params = {
            "assessmentYear": assessment_year,
            "subject": subject,
            "grade": grade,
            "subscale": subscale,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_overall(self, assessment_year, subject, grade):
        url = "https://api.neap.gov/api/GetOverall"
        params = {
            "assessmentYear": assessment_year,
            "subject": subject,
            "grade": grade,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_trends(self, subject, grade, subscales=None):
        url = "https://api.neap.gov/api/GetTrends"
        params = {
            "subject": subject,
            "grade": grade,
        }
        if subscales:
            params["subscales"] = ",".join(subscales)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_gaps(self, subject, grade, gap_type, groups=None, jurisdictions=None, assessment_years=None):
        url = "https://api.neap.gov/api/GetGaps"
        params = {
            "subject": subject,
            "grade": grade,
            "gapType": gap_type,
        }
        if groups:
            params["groups"] = ",".join(groups)
        if jurisdictions:
            params["jurisdictions"] = ",".join(jurisdictions)
        if assessment_years:
            params["assessmentYears"] = ",".join(assessment_years)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        return response.json()