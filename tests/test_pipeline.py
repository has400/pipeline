"""Testing of class Stage."""
# pylint: disable=no-self-use, invalid-name
import unittest
from hamcrest import assert_that, equal_to

from spline.pipeline import Pipeline
from spline.components.hooks import Hooks
from spline.components.config import ApplicationOptions


class TestPipeline(unittest.TestCase):
    """Testing of class Pipeline."""

    def test_simple_valid_pipeline(self):
        """Testing of a simple valid pipeline."""
        definition = [{'stage(test)': [{
            'tasks': [{'shell': {'script': '''echo tasks1:hello1''', 'when': ''}},
                      {'shell': {'script': '''echo tasks1:hello2''', 'when': ''}}]}]}]
        hooks = Hooks()
        hooks.cleanup = '''echo cleanup hello'''
        pipeline = Pipeline(options=ApplicationOptions(definition='fake.yaml'))
        pipeline.hooks = hooks
        result = pipeline.process(definition)
        output = [line for line in result['output'] if line.find("hello") >= 0]

        assert_that(result['success'], equal_to(True))
        assert_that(len(output), equal_to(3))
        assert_that(output[0], equal_to('tasks1:hello1'))
        assert_that(output[1], equal_to('tasks1:hello2'))
        assert_that(output[2], equal_to('cleanup hello'))

    def test_environment_variables(self):
        """Testing of a simple valid pipeline with environment variables."""
        definition = [
            {'env': {'message': 'pipeline hello'}},
            {'stage(test)': [{'tasks': [{'shell': {'script': '''echo $message''', 'when': ''}},
                                        {'shell': {'script': '''echo tasks1:hello''', 'when': ''}}]}]}
        ]
        hooks = Hooks()
        hooks.cleanup = '''echo cleanup hello'''
        pipeline = Pipeline(options=ApplicationOptions(definition='fake.yaml'))
        pipeline.hooks = hooks
        result = pipeline.process(definition)
        output = [line for line in result['output'] if line.find("hello") >= 0]

        assert_that(result['success'], equal_to(True))
        assert_that(len(output), equal_to(3))
        assert_that(output[0], equal_to('pipeline hello'))
        assert_that(output[1], equal_to('tasks1:hello'))
        assert_that(output[2], equal_to('cleanup hello'))

    def test_simple_failed_pipeline(self):
        """Testing of a simple failed pipeline."""
        definition = [{'stage(test)': [{
            'tasks': [{'shell': {'script': '''echo tasks1:hello1''', 'when': ''}},
                      {'shell': {'script': '''exit 123''', 'when': ''}},
                      {'shell': {'script': '''echo tasks1:hello3''', 'when': ''}}]}]}]
        hooks = Hooks()
        hooks.cleanup = '''echo cleanup hello'''
        pipeline = Pipeline(options=ApplicationOptions(definition='fake.yaml'))
        pipeline.hooks = hooks
        result = pipeline.process(definition)
        output = [line for line in result['output'] if line.find("hello") >= 0]

        assert_that(result['success'], equal_to(False))
        assert_that(len(output), equal_to(2))
        assert_that(output[0], equal_to('tasks1:hello1'))
        assert_that(output[1], equal_to('cleanup hello'))
        assert_that(pipeline.hooks, equal_to(hooks))
