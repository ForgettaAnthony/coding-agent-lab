def is_balanced(text):
    """Return whether parentheses, brackets, and braces are properly nested."""
    opening = "([{"
    closing = ")]}"
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []

    for character in text:
        if character in opening:
            stack.append(character)
        elif character in closing:
            if not stack:
                return False
            stack.pop()

    return not stack
