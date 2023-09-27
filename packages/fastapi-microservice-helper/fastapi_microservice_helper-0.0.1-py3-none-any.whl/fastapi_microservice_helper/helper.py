from types import GenericAlias


def oneline(value: str):
    return value + '\r\n'


def tab(content: str, tabLength=1):
    tabContent = '    ' * tabLength
    newContent = ''
    for line in content.split('\r\n'):
        newContent += oneline(tabContent + line)

    return newContent


def get_generic_type(ref_type: type(GenericAlias)):
    alias_params = map(lambda ref: ref.__name__, ref_type.__args__)
    return f'{ref_type.__name__}[{",".join(alias_params)}]'
