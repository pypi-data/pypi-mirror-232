import matplotlib.pyplot as plt
def test_add(d, a, b, c):
    (d, a, b, c) = (10, 12, 13, 15)
    assert add_all(d, a, b, c)==(22, 23, 25)
def new_input():
    x = 3
    y = 30
