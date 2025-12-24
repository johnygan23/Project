"""Text processing utilities."""
import re


def split_sentences(text):
    """
    Splits text into sentences using regex.
    Matches periods/questions/exclamations followed by space or end of line.
    """
    # This regex looks for sentence terminators (.?!) followed by a space or end-of-string
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

