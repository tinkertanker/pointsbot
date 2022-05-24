import numbers


def fmt_pts(usr_mention: str, points_num: numbers.Number) -> str:
    """
    Formats the point result output for printing
    :param points_num: the number of points
    :param usr_mention: the mention
    :return: A formatted string
    """
    if points_num == 1:
        return f"{usr_mention} now has **{points_num:.2f}** point"
    else:
        return f"{usr_mention} now has **{points_num:.2f}** points"
