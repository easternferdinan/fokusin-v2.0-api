def three_level_categorize(value: int, low_max: int, medium_max: int, categories: list[str] = ["rendah", "sedang", "tinggi"]):
    '''
    Categorize an integer value into three categories based on a low to medium range.

    Args:
        value (int): Value to categorize
        low_max (int): Maximum value for 'rendah'
        medium_max (int): Maximum value for 'sedang'
        categories (list[str]): List of categories in increasing order (default: ["rendah", "sedang", "tinggi"])

    Returns:
        str: 'rendah', 'sedang', or 'tinggi' or others based on categories input
    '''
    if value <= low_max:
        return categories[0]
    elif value <= medium_max:
        return categories[1]
    return categories[2]