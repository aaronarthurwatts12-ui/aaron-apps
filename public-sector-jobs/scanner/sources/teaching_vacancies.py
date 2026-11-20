"""Teaching Vacancies (DfE official API) - schools and multi-academy trusts in England."""
from ..http import get
from ..models import Job

API = "https://teaching-vacancies.service.gov.uk/api/v1/jobs.json"


def fetch(since, max_pages=120):
    jobs = []
    for page in range(1, max_pages + 1):
        d = get(API, params={"page": page}, pause=0.3).json()
        for j in d.get("data", []):
            posted = (j.get("datePosted") or "")[:10]
            if posted and posted < since:
                continue
            org = (j.get("hiringOrganization") or {}).get("name", "")
            addr = ((j.get("jobLocation") or {}).get("address") or {})
            if isinstance(j.get("jobLocation"), list):
                addr = (j["jobLocation"][0] or {}).get("address", {})
            sal = (((j.get("baseSalary") or {}).get("value") or {}).get("value") or "")
            jobs.append(Job("Teaching Vacancies", j.get("title", ""), org, j.get("url", ""),
                            ", ".join(x for x in [addr.get("addressLocality"), addr.get("addressRegion")] if x),
                            " ".join(str(sal).split())[:80], posted, (j.get("validThrough") or "")[:10]))
        if not d.get("links", {}).get("next"):
            break
    return jobs
