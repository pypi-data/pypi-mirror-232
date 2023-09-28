
'''This is the “nester.py" module, and it provides one function called printlist() which prints lists that may or may not include nested lists. 
The printing is done depending on the level'''

def printlist(listitems, level=1):
    '''This function accepts a deeply nested list of primitives and a level that defaults to 0. It prints out the list's content using entered level'''
    for item in listitems:
        if isinstance(item, list):
            printlist(item, level+1)
        else:
            for pos in range(level):
                print(' ' * 4, end='')
            print(item)

