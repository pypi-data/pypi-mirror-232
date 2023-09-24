import ast
from functools import partial
from typing import Iterable

from tokenize_rt import Token

from ..helpers import ast_to_offset, get_annotation_type, find_token, find_token_by_name, get_mojo_type
from ..rules import RuleSet


def _replace_assignment(tokens: list[Token], i: int, rules: RuleSet, new_type: str) -> None:
    tokens.insert(i, Token(name='NAME', src='var '))
    ann_idx = find_token(tokens, i, ':')
    type_idx = find_token_by_name(tokens, ann_idx, name='NAME')
    assign_op_idx = find_token(tokens, type_idx, '=') - 1
    newline_idx = find_token_by_name(tokens, type_idx, name='NEWLINE')
    valid_idxs = (idx for idx in (assign_op_idx, newline_idx) if idx >= 0)
    end_type_idx = min(valid_idxs)
    del tokens[type_idx:end_type_idx]
    tokens.insert(type_idx, Token(name='NAME', src=new_type))


def convert_assignment(node: ast.AnnAssign, rules: RuleSet) -> Iterable:
    """Convert an assignment to a mojo assignment."""
    curr_type = get_annotation_type(node.annotation)
    new_type = get_mojo_type(curr_type, rules)
    if not new_type:
        return

    yield (
        ast_to_offset(node),
        partial(
            _replace_assignment,
            new_type=new_type,
        ),
    )
