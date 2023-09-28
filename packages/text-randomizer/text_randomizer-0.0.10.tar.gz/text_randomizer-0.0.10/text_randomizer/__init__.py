import json
from .config import DEBUG
from .tokenizer import Tokenizer
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler


class Template:
    def __init__(self, source: str) -> None:
        self.__source = source

    def render(self) -> str:
        tokenizer = Tokenizer(self.__source)
        tokens = tokenizer.get_tokens()

        if DEBUG:
            print(f'{tokens=}')

        lexer = Lexer(tokens)
        lexemes = lexer.get_lexems()

        if DEBUG:
            print(f'{lexemes=}')

        parser = Parser(lexemes)
        ast = parser.get_ast()

        if DEBUG:
            print(json.dumps(ast, ensure_ascii=False, indent=2))

        compiler = Compiler(ast)
        render = compiler.render_ast()
        return render
