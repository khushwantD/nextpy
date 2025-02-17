import datetime
from typing import Any, List

import pytest

from nextpy.backend.event import EventChain, EventHandler, EventSpec, FrontendEvent
from nextpy.backend.vars import BaseVar, Var
from nextpy.frontend.components.tags.tag import Tag
from nextpy.frontend.style import Style
from nextpy.utils import format
from tests.test_state import (
    ChildState,
    ChildState2,
    DateTimeState,
    GrandchildState,
    TestState,
)


def mock_event(arg):
    pass


@pytest.mark.parametrize(
    "input,output",
    [
        ("{", "}"),
        ("(", ")"),
        ("[", "]"),
        ("<", ">"),
        ('"', '"'),
        ("'", "'"),
    ],
)
def test_get_close_char(input: str, output: str):
    """Test getting the close character for a given open character.

    Args:
        input: The open character.
        output: The expected close character.
    """
    assert format.get_close_char(input) == output


@pytest.mark.parametrize(
    "text,open,expected",
    [
        ("", "{", False),
        ("{wrap}", "{", True),
        ("{wrap", "{", False),
        ("{wrap}", "(", False),
        ("(wrap)", "(", True),
    ],
)
def test_is_wrapped(text: str, open: str, expected: bool):
    """Test checking if a string is wrapped in the given open and close characters.

    Args:
        text: The text to check.
        open: The open character.
        expected: Whether the text is wrapped.
    """
    assert format.is_wrapped(text, open) == expected


@pytest.mark.parametrize(
    "text,open,check_first,num,expected",
    [
        ("", "{", True, 1, "{}"),
        ("wrap", "{", True, 1, "{wrap}"),
        ("wrap", "(", True, 1, "(wrap)"),
        ("wrap", "(", True, 2, "((wrap))"),
        ("(wrap)", "(", True, 1, "(wrap)"),
        ("{wrap}", "{", True, 2, "{wrap}"),
        ("(wrap)", "{", True, 1, "{(wrap)}"),
        ("(wrap)", "(", False, 1, "((wrap))"),
    ],
)
def test_wrap(text: str, open: str, expected: str, check_first: bool, num: int):
    """Test wrapping a string.

    Args:
        text: The text to wrap.
        open: The open character.
        expected: The expected output string.
        check_first: Whether to check if the text is already wrapped.
        num: The number of times to wrap the text.
    """
    assert format.wrap(text, open, check_first=check_first, num=num) == expected


@pytest.mark.parametrize(
    "text,indent_level,expected",
    [
        ("", 2, ""),
        ("hello", 2, "hello"),
        ("hello\nworld", 2, "  hello\n  world\n"),
        ("hello\nworld", 4, "    hello\n    world\n"),
        ("  hello\n  world", 2, "    hello\n    world\n"),
    ],
)
def test_indent(text: str, indent_level: int, expected: str, windows_platform: bool):
    """Test indenting a string.

    Args:
        text: The text to indent.
        indent_level: The number of spaces to indent by.
        expected: The expected output string.
        windows_platform: Whether the system is windows.
    """
    assert format.indent(text, indent_level) == (
        expected.replace("\n", "\r\n") if windows_platform else expected
    )


@pytest.mark.parametrize(
    "input,output",
    [
        ("", ""),
        ("hello", "hello"),
        ("Hello", "hello"),
        ("camelCase", "camel_case"),
        ("camelTwoHumps", "camel_two_humps"),
        ("_start_with_underscore", "_start_with_underscore"),
        ("__start_with_double_underscore", "__start_with_double_underscore"),
        ("kebab-case", "kebab_case"),
        ("double-kebab-case", "double_kebab_case"),
        (":start-with-colon", ":start_with_colon"),
        (":-start-with-colon-dash", ":_start_with_colon_dash"),
    ],
)
def test_to_snake_case(input: str, output: str):
    """Test converting strings to snake case.

    Args:
        input: The input string.
        output: The expected output string.
    """
    assert format.to_snake_case(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("", ""),
        ("hello", "hello"),
        ("Hello", "Hello"),
        ("snake_case", "snakeCase"),
        ("snake_case_two", "snakeCaseTwo"),
        ("kebab-case", "kebabCase"),
        ("kebab-case-two", "kebabCaseTwo"),
        ("snake_kebab-case", "snakeKebabCase"),
        ("_hover", "_hover"),
        ("-starts-with-hyphen", "-startsWithHyphen"),
        ("--starts-with-double-hyphen", "--startsWithDoubleHyphen"),
        ("_starts_with_underscore", "_startsWithUnderscore"),
        ("__starts_with_double_underscore", "__startsWithDoubleUnderscore"),
        (":start-with-colon", ":startWithColon"),
        (":-start-with-colon-dash", ":StartWithColonDash"),
    ],
)
def test_to_camel_case(input: str, output: str):
    """Test converting strings to camel case.

    Args:
        input: The input string.
        output: The expected output string.
    """
    assert format.to_camel_case(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("", ""),
        ("hello", "Hello"),
        ("Hello", "Hello"),
        ("snake_case", "SnakeCase"),
        ("snake_case_two", "SnakeCaseTwo"),
    ],
)
def test_to_title_case(input: str, output: str):
    """Test converting strings to title case.

    Args:
        input: The input string.
        output: The expected output string.
    """
    assert format.to_title_case(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("", ""),
        ("hello", "hello"),
        ("Hello", "hello"),
        ("snake_case", "snake-case"),
        ("snake_case_two", "snake-case-two"),
        (":startWithColon", ":start-with-colon"),
        (":StartWithColonDash", ":-start-with-colon-dash"),
        (":start_with_colon", ":start-with-colon"),
        (":_start_with_colon_dash", ":-start-with-colon-dash"),
    ],
)
def test_to_kebab_case(input: str, output: str):
    """Test converting strings to kebab case.

    Args:
        input: the input string.
        output: the output string.
    """
    assert format.to_kebab_case(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("", "{``}"),
        ("hello", "{`hello`}"),
        ("hello world", "{`hello world`}"),
        ("hello=`world`", "{`hello=\\`world\\``}"),
    ],
)
def test_format_string(input: str, output: str):
    """Test formating the input as JS string literal.

    Args:
        input: the input string.
        output: the output string.
    """
    assert format.format_string(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        (Var.create(value="test"), "{`test`}"),
        (Var.create(value="test", _var_is_local=True), "{`test`}"),
        (Var.create(value="test", _var_is_local=False), "{test}"),
        (Var.create(value="test", _var_is_string=True), "{`test`}"),
        (Var.create(value="test", _var_is_string=False), "{`test`}"),
        (Var.create(value="test", _var_is_local=False, _var_is_string=False), "{test}"),
    ],
)
def test_format_var(input: Var, output: str):
    assert format.format_var(input) == output


@pytest.mark.parametrize(
    "route,format_case,expected",
    [
        ("", True, "index"),
        ("/", True, "index"),
        ("custom-route", True, "custom-route"),
        ("custom-route", False, "custom-route"),
        ("custom-route/", True, "custom-route"),
        ("custom-route/", False, "custom-route"),
        ("/custom-route", True, "custom-route"),
        ("/custom-route", False, "custom-route"),
        ("/custom_route", True, "custom-route"),
        ("/custom_route", False, "custom_route"),
        ("/CUSTOM_route", True, "custom-route"),
        ("/CUSTOM_route", False, "CUSTOM_route"),
    ],
)
def test_format_route(route: str, format_case: bool, expected: bool):
    """Test formatting a route.

    Args:
        route: The route to format.
        format_case: Whether to change casing to snake_case.
        expected: The expected formatted route.
    """
    assert format.format_route(route, format_case=format_case) == expected


@pytest.mark.parametrize(
    "condition,true_value,false_value,expected",
    [
        ("cond", "<C1>", '""', '{isTrue(cond) ? <C1> : ""}'),
        ("cond", "<C1>", "<C2>", "{isTrue(cond) ? <C1> : <C2>}"),
    ],
)
def test_format_cond(condition: str, true_value: str, false_value: str, expected: str):
    """Test formatting a cond.

    Args:
        condition: The condition to check.
        true_value: The value to return if the condition is true.
        false_value: The value to return if the condition is false.
        expected: The expected output string.
    """
    assert format.format_cond(condition, true_value, false_value) == expected


@pytest.mark.parametrize(
    "condition, match_cases, default,expected",
    [
        (
            "state__state.value",
            [
                [Var.create(1), Var.create("red", _var_is_string=True)],
                [Var.create(2), Var.create(3), Var.create("blue", _var_is_string=True)],
                [TestState.mapping, TestState.num1],
                [
                    Var.create(f"{TestState.map_key}-key", _var_is_string=True),
                    Var.create("return-key", _var_is_string=True),
                ],
            ],
            Var.create("yellow", _var_is_string=True),
            "(() => { switch (JSON.stringify(state__state.value)) {case JSON.stringify(1):  return (`red`);  break;case JSON.stringify(2): case JSON.stringify(3):  "
            "return (`blue`);  break;case JSON.stringify(test_state.mapping):  return "
            "(test_state.num1);  break;case JSON.stringify(`${test_state.map_key}-key`):  return (`return-key`);"
            "  break;default:  return (`yellow`);  break;};})()",
        )
    ],
)
def test_format_match(
    condition: str, match_cases: List[BaseVar], default: BaseVar, expected: str
):
    """Test formatting a match statement.

    Args:
        condition: The condition to match.
        match_cases: List of match cases to be matched.
        default: Catchall case for the match statement.
        expected: The expected string output.
    """
    assert format.format_match(condition, match_cases, default) == expected


@pytest.mark.parametrize(
    "prop,formatted",
    [
        ("string", '"string"'),
        ("{wrapped_string}", "{wrapped_string}"),
        (True, "{true}"),
        (False, "{false}"),
        (123, "{123}"),
        (3.14, "{3.14}"),
        ([1, 2, 3], "{[1, 2, 3]}"),
        (["a", "b", "c"], '{["a", "b", "c"]}'),
        ({"a": 1, "b": 2, "c": 3}, '{{"a": 1, "b": 2, "c": 3}}'),
        ({"a": 'foo "bar" baz'}, r'{{"a": "foo \"bar\" baz"}}'),
        (
            {
                "a": 'foo "{ "bar" }" baz',
                "b": BaseVar(_var_name="val", _var_type="str"),
            },
            r'{{"a": "foo \"{ \"bar\" }\" baz", "b": val}}',
        ),
        (
            EventChain(
                events=[EventSpec(handler=EventHandler(fn=mock_event))],
                args_spec=lambda: [],
            ),
            '{(_e) => addEvents([Event("mock_event", {})], (_e), {})}',
        ),
        (
            EventChain(
                events=[
                    EventSpec(
                        handler=EventHandler(fn=mock_event),
                        args=(
                            (
                                Var.create_safe("arg"),
                                BaseVar(
                                    _var_name="_e",
                                    _var_type=FrontendEvent,
                                ).target.value,
                            ),
                        ),
                    )
                ],
                args_spec=lambda: [],
            ),
            '{(_e) => addEvents([Event("mock_event", {arg:_e.target.value})], (_e), {})}',
        ),
        (
            EventChain(
                events=[EventSpec(handler=EventHandler(fn=mock_event))],
                args_spec=lambda: [],
                event_actions={"stopPropagation": True},
            ),
            '{(_e) => addEvents([Event("mock_event", {})], (_e), {"stopPropagation": true})}',
        ),
        (
            EventChain(
                events=[EventSpec(handler=EventHandler(fn=mock_event))],
                args_spec=lambda: [],
                event_actions={"preventDefault": True},
            ),
            '{(_e) => addEvents([Event("mock_event", {})], (_e), {"preventDefault": true})}',
        ),
        ({"a": "red", "b": "blue"}, '{{"a": "red", "b": "blue"}}'),
        (BaseVar(_var_name="var", _var_type="int"), "{var}"),
        (
            BaseVar(
                _var_name="_",
                _var_type=Any,
                _var_is_local=True,
                _var_is_string=False,
            ),
            "{_}",
        ),
        (
            BaseVar(_var_name='state.colors["a"]', _var_type="str"),
            '{state.colors["a"]}',
        ),
        ({"a": BaseVar(_var_name="val", _var_type="str")}, '{{"a": val}}'),
        ({"a": BaseVar(_var_name='"val"', _var_type="str")}, '{{"a": "val"}}'),
        (
            {"a": BaseVar(_var_name='state.colors["val"]', _var_type="str")},
            '{{"a": state.colors["val"]}}',
        ),
        # tricky real-world case from markdown component
        (
            {
                "h1": f"{{({{node, ...props}}) => <Heading {{...props}} {''.join(Tag(name='', props=Style({'as_': 'h1'})).format_props())} />}}"
            },
            '{{"h1": ({node, ...props}) => <Heading {...props} as={`h1`} />}}',
        ),
    ],
)
def test_format_prop(prop: Var, formatted: str):
    """Test that the formatted value of an prop is correct.

    Args:
        prop: The prop to test.
        formatted: The expected formatted value.
    """
    assert format.format_prop(prop) == formatted


@pytest.mark.parametrize(
    "single_props,key_value_props,output",
    [
        (["string"], {"key": 42}, ["key={42}", "string"]),
    ],
)
def test_format_props(single_props, key_value_props, output):
    """Test the result of formatting a set of props (both single and keyvalue).

    Args:
        single_props: the list of single props
        key_value_props: the dict of key value props
        output: the expected output
    """
    assert format.format_props(*single_props, **key_value_props) == output


@pytest.mark.parametrize(
    "input,output",
    [
        (EventHandler(fn=mock_event), ("", "mock_event")),
    ],
)
def test_get_handler_parts(input, output):
    assert format.get_event_handler_parts(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        (TestState.do_something, "test_state.do_something"),
        (ChildState.change_both, "test_state.child_state.change_both"),
        (
            GrandchildState.do_nothing,
            "test_state.child_state.grandchild_state.do_nothing",
        ),
    ],
)
def test_format_event_handler(input, output):
    """Test formatting an event handler.

    Args:
        input: The event handler input.
        output: The expected output.
    """
    assert format.format_event_handler(input) == output  # type: ignore


@pytest.mark.parametrize(
    "input,output",
    [
        (EventSpec(handler=EventHandler(fn=mock_event)), 'Event("mock_event", {})'),
    ],
)
def test_format_event(input, output):
    assert format.format_event(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        (
            EventChain(
                events=[
                    EventSpec(handler=EventHandler(fn=mock_event)),
                    EventSpec(handler=EventHandler(fn=mock_event)),
                ],
                args_spec=None,
            ),
            'addEvents([Event("mock_event", {}),Event("mock_event", {})])',
        ),
        (
            EventChain(
                events=[
                    EventSpec(handler=EventHandler(fn=mock_event)),
                    EventSpec(handler=EventHandler(fn=mock_event)),
                ],
                args_spec=lambda e0: [e0],
            ),
            'addEvents([Event("mock_event", {}),Event("mock_event", {})])',
        ),
    ],
)
def test_format_event_chain(input, output):
    assert format.format_event_chain(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ({"query": {"k1": 1, "k2": 2}}, {"k1": 1, "k2": 2}),
        ({"query": {"k1": 1, "k-2": 2}}, {"k1": 1, "k_2": 2}),
    ],
)
def test_format_query_params(input, output):
    assert format.format_query_params(input) == output


formatted_router = {
    "session": {"client_token": "", "client_ip": "", "session_id": ""},
    "headers": {
        "host": "",
        "origin": "",
        "upgrade": "",
        "connection": "",
        "pragma": "",
        "cache_control": "",
        "user_agent": "",
        "sec_websocket_version": "",
        "sec_websocket_key": "",
        "sec_websocket_extensions": "",
        "accept_encoding": "",
        "accept_language": "",
    },
    "page": {
        "host": "",
        "path": "",
        "raw_path": "",
        "full_path": "",
        "full_raw_path": "",
        "params": {},
    },
}


@pytest.mark.parametrize(
    "input, output",
    [
        (
            TestState().dict(),  # type: ignore
            {
                TestState.get_full_name(): {
                    "array": [1, 2, 3.14],
                    "complex": {
                        1: {"prop1": 42, "prop2": "hello"},
                        2: {"prop1": 42, "prop2": "hello"},
                    },
                    "dt": "1989-11-09 18:53:00+01:00",
                    "fig": [],
                    "key": "",
                    "map_key": "a",
                    "mapping": {"a": [1, 2, 3], "b": [4, 5, 6]},
                    "num1": 0,
                    "num2": 3.14,
                    "obj": {"prop1": 42, "prop2": "hello"},
                    "sum": 3.14,
                    "upper": "",
                    "router": formatted_router,
                },
                ChildState.get_full_name(): {
                    "count": 23,
                    "value": "",
                },
                ChildState2.get_full_name(): {"value": ""},
                GrandchildState.get_full_name(): {"value2": ""},
            },
        ),
        (
            DateTimeState().dict(),
            {
                DateTimeState.get_full_name(): {
                    "d": "1989-11-09",
                    "dt": "1989-11-09 18:53:00+01:00",
                    "t": "18:53:00+01:00",
                    "td": "11 days, 0:11:00",
                    "router": formatted_router,
                },
            },
        ),
    ],
)
def test_format_state(input, output):
    """Test that the format state is correct.

    Args:
        input: The state to format.
        output: The expected formatted state.
    """
    assert format.format_state(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("input1", "ref_input1"),
        ("input 1", "ref_input_1"),
        ("input-1", "ref_input_1"),
        ("input_1", "ref_input_1"),
        ("a long test?1! name", "ref_a_long_test_1_name"),
    ],
)
def test_format_ref(input, output):
    """Test formatting a ref.

    Args:
        input: The name to format.
        output: The expected formatted name.
    """
    assert format.format_ref(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        (("my_array", None), "refs_my_array"),
        (("my_array", Var.create(0)), "refs_my_array[0]"),
        (("my_array", Var.create(1)), "refs_my_array[1]"),
    ],
)
def test_format_array_ref(input, output):
    assert format.format_array_ref(input[0], input[1]) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("/foo", [("foo", "/foo")]),
        ("/foo/bar", [("foo", "/foo"), ("bar", "/foo/bar")]),
        (
            "/foo/bar/baz",
            [("foo", "/foo"), ("bar", "/foo/bar"), ("baz", "/foo/bar/baz")],
        ),
    ],
)
def test_format_breadcrumbs(input, output):
    assert format.format_breadcrumbs(input) == output


@pytest.mark.parametrize(
    "input, output",
    [
        ("library@^0.1.2", "library"),
        ("library", "library"),
        ("@library@^0.1.2", "@library"),
        ("@library", "@library"),
    ],
)
def test_format_library_name(input: str, output: str):
    """Test formating a library name to remove the @version part.

    Args:
        input: the input string.
        output: the output string.
    """
    assert format.format_library_name(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        (None, "null"),
        (True, "true"),
        (1, "1"),
        (1.0, "1.0"),
        ([], "[]"),
        ([1, 2, 3], "[1, 2, 3]"),
        ({}, "{}"),
        ({"k1": False, "k2": True}, '{"k1": false, "k2": true}'),
        (
            [datetime.timedelta(1, 1, 1), datetime.timedelta(1, 1, 2)],
            '["1 day, 0:00:01.000001", "1 day, 0:00:01.000002"]',
        ),
        (
            {"key1": datetime.timedelta(1, 1, 1), "key2": datetime.timedelta(1, 1, 2)},
            '{"key1": "1 day, 0:00:01.000001", "key2": "1 day, 0:00:01.000002"}',
        ),
    ],
)
def test_json_dumps(input, output):
    assert format.json_dumps(input) == output
