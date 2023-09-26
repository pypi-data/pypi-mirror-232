"""
diff file
"""
from typing import Any
from seldom.logging import log


class AssertInfo:
    warning = []
    error = []


def _list_sorted(data):
    """
    list sorted
    """
    if isinstance(data[0], dict):
        if len(data[0]) == 0:
            log.info("data is [{}]")
        try:
            data = sorted(data, key=lambda x: x[list(data[0].keys())[0]])
        except (TypeError, AttributeError, IndexError):
            data = data
    else:
        data = sorted(data)
    return data


def diff_json(response_data: Any, assert_data: Any, exclude: list = None) -> None:
    """
    Compare the JSON data format
    """
    if exclude is None:
        exclude = []

    if isinstance(response_data, dict) and isinstance(assert_data, dict):
        # dict format
        for key in assert_data:
            # skip check
            if key in exclude:
                continue
            if key not in response_data:
                AssertInfo.error.append(f"❌ Response data has no key: {key}")
        for key in response_data:
            # skip check
            if key in exclude:
                continue
            if key in assert_data:
                # recursion
                diff_json(response_data[key], assert_data[key], exclude)
            else:
                AssertInfo.warning.append(f"💡 Assert data has not key: {key}")
    elif isinstance(response_data, list) and isinstance(assert_data, list):
        # list format
        if len(response_data) == 0:
            log.info("response is []")
        else:
            response_data = _list_sorted(response_data)

        if len(response_data) != len(assert_data):
            log.info(f"list len: '{len(response_data)}' != '{len(assert_data)}'")

        if len(assert_data) > 0:
            assert_data = _list_sorted(assert_data)

        for src_list, dst_list in zip(response_data, assert_data):
            # recursion
            diff_json(src_list, dst_list, exclude)
    else:
        # different format
        if str(response_data) != str(assert_data):
            AssertInfo.error.append(f"❌ Value are not equal: {assert_data} != {response_data}")
