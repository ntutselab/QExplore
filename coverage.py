import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def _requests_retry_session(retries=3, backoff_factor=0.3, status_force_list=(500, 502, 504), r_session=None):
    r_session = r_session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor,
                  status_forcelist=status_force_list)
    adapter = HTTPAdapter(max_retries=retry)
    r_session.mount('http://', adapter)
    r_session.mount('https://', adapter)
    return r_session


session = _requests_retry_session()
_serverRootUrl = "http://127.0.0.1:3001"


def _convert_code_coverage_value_vector_to_code_coverage_vector(code_coverage_value_vector) -> list:
    code_coverage_vector = []
    for i in code_coverage_value_vector:
        code_coverage_vector.append(i != 0)

    return code_coverage_vector


def _flat_list(origin_list: []):
    flattened_list = []
    for i in origin_list:
        if isinstance(i, list):
            flattened_list = [*flattened_list, *_flat_list(i)]
        else:
            flattened_list.append(i)
    return flattened_list


def _get_code_coverage_vector(coverage_type_indicator) -> list:
    try:
        # return global coverage object on /coverage/object as JSON
        # for more info, consult the istanbul-middleware utils docs
        response = session.get("{}{}".format(_serverRootUrl, "/coverage/object"))
        code_coverage_value_vector_list = [list(v[coverage_type_indicator].values()) for v in response.json().values()]
        code_coverage_value_vector = _flat_list(code_coverage_value_vector_list)
        code_coverage_vector = _convert_code_coverage_value_vector_to_code_coverage_vector(
            code_coverage_value_vector=code_coverage_value_vector)
        return code_coverage_vector
    except Exception as e:
        print("Failed at getting coverage", e.__class__.__name__)


statement_coverage_vector = _get_code_coverage_vector("s")
branch_coverage_vector = _get_code_coverage_vector("b")

statement_coverage_vector_amount = 0
branch_coverage_vector_amount = 0
for i in statement_coverage_vector:
    if i >= 1:
        statement_coverage_vector_amount += 1
for i in branch_coverage_vector:
    if i >= 1:
        branch_coverage_vector_amount += 1
print("Statement coverage:", end=" ")
print(statement_coverage_vector_amount / len(statement_coverage_vector) * 100)
print("Branch coverage:", end=" ")
print(branch_coverage_vector_amount / len(branch_coverage_vector) * 100)
