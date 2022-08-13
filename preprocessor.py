import re


# preprocess action
def preprocess(input_data: str, replacement_tokens):
    for replacement_token in replacement_tokens:
        identifier = replacement_token[0]
        replaced = replacement_token[1]
        input_data = re.sub(r'([^a-zA-Z0-9\"])({})([^a-zA-Z0-9\"])'.format(identifier), r'\g<1>{}\g<3>'.format(replaced), input_data)
        input_data = re.sub(r'([^a-zA-Z0-9\"])({})([^a-zA-Z0-9\"])'.format(identifier), r'\g<1>{}\g<3>'.format(replaced), input_data)
    return input_data


def factorize_preprocess(input_data: str):
    define_regex = r'define (\S*)\s(.*)\W'
    matched_patterns = re.findall(define_regex, input_data)
    return matched_patterns


def run_preprocess(input_data: str):
    replacement_tokens = factorize_preprocess(input_data=input_data)
    return preprocess(
        input_data=input_data,
        replacement_tokens=replacement_tokens
    )
