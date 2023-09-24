import ast
from functools import partial
from typing import Iterable

from tokenize_rt import Token

from ..exceptions import ParseException
from ..helpers import (
    ast_to_offset,
    get_annotation_type,
    find_token,
    find_token_after_offset,
    find_token_by_name,
    get_mojo_type,
)
from ..rules import RuleSet


def _replace_annotation(
    tokens: list, i: int, rules: RuleSet, end_offset: int, new_type: str, ann_offset: int | None = None
) -> None:
    if ann_offset:
        ann_idx = find_token_after_offset(tokens, i, ann_offset)
    else:
        ann_idx = find_token(tokens, i, ':')
    type_idx = find_token_by_name(tokens, ann_idx, name='NAME')
    end_type_idx = find_token_after_offset(tokens, ann_idx, end_offset)
    del tokens[type_idx:end_type_idx]
    tokens.insert(type_idx, Token(name='NAME', src=new_type))


def _replace_def_keyword(tokens: list, i: int, rules: RuleSet) -> None:
    idx = find_token(tokens, i, 'def')
    tokens[idx] = Token(name='NAME', src='fn')


def _add_declaration(tokens: list, i: int, rules: RuleSet, declaration: str) -> None:
    tokens.insert(i, Token(name='NAME', src=declaration))
    tokens.insert(i + 1, Token(name='UNIMPORTANT_WS', src=' '))


def convert_functiondef(node: ast.FunctionDef, rules: RuleSet = 0) -> Iterable:
    """Converts the annotation of the given function definition."""
    if rules.convert_def_to_fn > 0:
        offset = ast_to_offset(node)
        yield (
            offset,
            partial(
                _replace_def_keyword,
            ),
        )

    if not node.args.args:
        return

    for arg in node.args.args:
        if arg.arg == 'self':
            yield (
                ast_to_offset(arg),
                partial(
                    _add_declaration,
                    declaration='inout',
                ),
            )
            continue

        if rules.convert_def_to_fn and not arg.annotation:
            raise ParseException(
                node, 'For converting a "def" function to "fn", the declaration needs to be fully type annotated'
            )
        curr_type = get_annotation_type(arg.annotation)
        new_type = get_mojo_type(curr_type, rules)

        if not new_type:
            continue

        yield (
            ast_to_offset(arg),
            partial(
                _replace_annotation,
                end_offset=arg.end_col_offset,
                new_type=new_type,
            ),
        )

    if node.returns:
        curr_type = get_annotation_type(node.returns)
        new_type = get_mojo_type(curr_type, rules)
        if not new_type:
            return

        offset = ast_to_offset(node.returns)
        yield (
            offset,
            partial(
                _replace_annotation,
                end_offset=node.returns.end_col_offset,
                new_type=new_type,
                ann_offset=offset.utf8_byte_offset,
            ),
        )
