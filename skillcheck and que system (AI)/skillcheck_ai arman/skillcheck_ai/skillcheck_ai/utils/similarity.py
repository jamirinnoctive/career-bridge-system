def get_similarity(a, b):
    a = a.lower().strip()
    b = b.lower().strip()

    if a == b:
        return 100
    elif a in b or b in a:
        return 75
    else:
        return 30
