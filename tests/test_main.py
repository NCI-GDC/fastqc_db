##an example unit test. Add more tests in the future updates


def test_get_total_deduplicated_percentage():
    import logging

    from fastqc_db.fastqc_db import get_total_deduplicated_percentage

    logger = logging.getLogger("fastqc_db/tests")

    with open("tests/mock_data/test.txt", "r") as f:
        splited_results = get_total_deduplicated_percentage(f, logger)
        assert splited_results[1] == "test successful"
