import hpcflow.app as hf


def test_in_pytest_if_not_frozen():
    """This is to check we can get the correct invocation command when running non-frozen
    tests (when frozen the invocation command is just the executable file)."""
    if not hf.run_time_info.is_frozen:
        assert hf.run_time_info.in_pytest
