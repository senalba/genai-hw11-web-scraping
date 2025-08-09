# utils.py


def save_to_txt(headlines, filename):
    """
    Saves a list of headlines to a text file, one per line.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for headline in headlines:
            f.write(headline + "\n")
