def allkeys(d: dict) -> list:
    """ネストした要素も含めたdict.keys

    Args:
        d (dict): dict

    Returns:
        list: keys

    Example:
        >>> d = {'name': {'first': 'John', 'last': 'Smith'}, 'age': 36}
        >>> allkeys(d)
        ['name.first', 'name.last', 'age']

    Note:
        https://qiita.com/ainn_lll/items/e898b7bc8bfc4afdb445
    """
    keys = []
    for parent, children in d.items():
        if isinstance(children, dict):
            keys += [parent + "." + child for child in allkeys(children)]
        else:
            keys.append(parent)
    return keys

def find(lst, predicate):
    """
    Listの中から、predicateの条件に合致する最初の要素を返す。
    
    Args:
        lst (list): 検索対象のリスト。
        predicate (Union[dict, str, Callable]): 検索条件。辞書、文字列、または関数（ラムダ式を含む）のいずれか。
    
    Returns:
        dict or None: 条件に合致する最初の要素。合致する要素がない場合はNone.
        
    Example:
        >>> users = [
        ...     { 'user': 'barney',  'age': 36, 'active': True },
        ...     { 'user': 'fred',    'age': 40, 'active': False },
        ...     { 'user': 'pebbles', 'age': 1,  'active': True }
        ... ]
        >>> find(users, {'age': 1, 'active': True})
        {'user': 'pebbles', 'age': 1, 'active': True}
        >>> find(users, 'active')
        {'user': 'barney', 'age': 36, 'active': True}
        >>> find(users, lambda x: x['age'] < 40 or not x['active'])
        {'user': 'barney', 'age': 36, 'active': True}
    """
    if isinstance(predicate, dict):
        for item in lst:
            if all(item[key] == val for key, val in predicate.items()):
                return item
    elif isinstance(predicate, str):
        for item in lst:
            if isinstance(item, dict):
                if item.get(predicate) is True:
                    return item
            else:
                if item == predicate:
                    return item
    else:
        for item in lst:
            if predicate(item):
                return item
    return None
