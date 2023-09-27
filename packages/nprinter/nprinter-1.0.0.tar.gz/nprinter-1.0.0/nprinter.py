
'''This is the “nester.py" module, and it provides one function called print_lol() which prints lists that may or may not include nested lists'''

def printlist(listitems):
    '''This function accepts a deeply nested list of primitives and prints out the list's content'''
    for item in listitems:
        if isinstance(item, list):
            printlist(item)
        else:
            print(item)

