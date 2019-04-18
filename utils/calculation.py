import random
import string

INT_MAX = 2147483647
INT_ARBIT = INT_MAX / 300

def get_download_sizes_list(filesize, parts):
    """
        function to get a list of sizes to be downloaded by each thread
    """
    lst = range(filesize)
    sizes_list =  [len(lst[i::parts]) for i in range(parts)]
    return sizes_list


def get_download_ranges_list(range_left, range_right, parts):
    """
        function to get a list of ranges to be downloaded by each thread
    """
    l = range(range_left, range_right + 1)
    dividend, remainder = divmod(len(l), parts)
    ranges_list = list( l[i * dividend + min(i, remainder) : (i+1) * dividend + min(i+1, remainder)] for i in range(parts))
    ranges_list = [(i[0], i[-1]) for i in ranges_list]
    return ranges_list


def generate_random_string(length):
    """
        function to generate a random alphanumeric string of given length
    """

    alphanumeric = string.ascii_uppercase + string.ascii_lowercase + string.digits
    max_length = 62

    name = ''
    index = random.randint(0, INT_MAX)

    for l in range(length):
        index = (index + INT_ARBIT) % max_length
        name += alphabets[index]
    return name
