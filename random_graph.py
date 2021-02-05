import random


def wilson(n: int, seed=None) -> tuple[int, list[bool]]:
    """
    Wilson's algorithm for generating random arborescence in complete graph of n nodes

    :param seed: seed
    :param n: number of nodes
    :return: uniform arborescence of graph
    """

    def random_node() -> int:
        return random.randint(0, n - 1)

    if seed:
        random.seed(seed)

    if n <= 0:
        raise ValueError(f'Graph must have al least one node, but {n} was given.')

    visited = [False] * n
    path = [0] * n
    edges = [False] * (n ** 2)

    # graph complete so all nodes are symmetrical (any node could be root)
    root = 0
    visited[root] = True

    remain = n - 1
    while remain > 0:
        # choose random node not in visited
        start_node = random_node()
        while visited[start_node]:
            start_node = random_node()

        # choose random node among all nodes
        # check if that node inside visited nodes
        prev_node = start_node
        node = random_node()
        while not visited[node]:
            path[prev_node] = node
            prev_node = node
            node = random_node()
        path[prev_node] = node
        end_node = node

        # if inside than add current path to tree
        frm = start_node
        to = path[frm]
        while frm != end_node:
            # mark as visited
            visited[frm] = True

            # reverse path (make sure that from root to any node exist path)
            edges[n * to + frm] = True

            frm = to
            to = path[frm]

            remain -= 1

    return root, edges


def random_edges(edges: list[bool], m=1, seed=None) -> list[bool]:
    """
    Add random edge to list of edges currently not presented in edges
    :param edges: list of edges
    :param m: number of added edges
    :param seed: seed
    :returns: modified list of edges
    """
    if seed:
        random.seed(seed)

    if not edges:
        raise ValueError('Empty list of edges.')

    if all(edges):
        return edges

    edges = [*edges]
    for edge in random.sample(range(len(edges)), k=len(edges)):
        if m == 0:
            break
        if not edges[edge]:
            edges[edge] = True
            m -= 1

    return edges


def random_graph(n: int, m: int, seed=None) -> tuple[int, list[bool]]:
    """
    Return random directed graph with root element such that it has path to any other node

    :param seed: seed
    :param n: number of nodes
    :param m: number of edges
    :return: root node, list of edges of created graph
    """
    if m < n - 1:
        raise ValueError(f'Impossible to create arborescence for {n} nodes with number of edges smaller then {n - 1}, '
                         f'but {m} was given.')

    if m > n ** 2:
        raise ValueError(f'Complete directed graph could contain at most {n ** 2} edges, but {m} was given.')

    root, edges = wilson(n, seed=seed)
    m -= (n - 1)
    edges = random_edges(edges, m=m, seed=seed)

    return root, edges
