# nester.py module
def print_lol(the_list):
    # print all nested items
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)