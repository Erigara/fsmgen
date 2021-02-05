import pytest
from hypothesis import given, strategies as st

from random_graph import wilson, random_graph, random_edges


class TestRandomEdges:

    @given(edges=st.lists(st.booleans(), min_size=1), m=st.integers(min_value=0))
    def test_random_edges(self, edges, m):
        modified_edges = random_edges(edges, m=m)
        # only adding edges
        assert all([((edge == modified_edge) or ((not edge) and modified_edge))
                    for edge, modified_edge in zip(edges, modified_edges)])
        # add m new edges or reach maximum number of edges
        assert (sum(edges) + m == sum(modified_edges)) or all(modified_edges)

    def test_random_edges_empty(self):
        with pytest.raises(ValueError, match="Empty list of edges"):
            random_edges([])


class TestWilson:
    nodes = st.integers(min_value=1, max_value=1000)

    @given(nodes=nodes)
    def test_number_of_nodes(self, nodes):
        _, edges = wilson(nodes)
        assert len(edges) == nodes ** 2

    @given(nodes=nodes)
    def test_number_of_edges(self, nodes):
        _, edges = wilson(nodes)
        assert sum(edges) == nodes - 1

    @given(nodes=nodes)
    def test_connectivity(self, nodes):
        root, edges = wilson(nodes)
        visited = []
        stack = [root]
        while stack:
            current_node = stack.pop()
            visited.append(current_node)
            current_node_edges = edges[current_node * nodes: (current_node + 1) * nodes]
            for i, edge in enumerate(current_node_edges):
                if edge and i not in visited:
                    stack.append(i)
        assert len(visited) == nodes

    @given(nodes=st.integers(max_value=0))
    def test_wilson_wrong_number_of_nodes(self, nodes):
        with pytest.raises(ValueError, match=r".*Graph must have al least one node.*"):
            wilson(nodes)


class TestRandomGraph:
    nodes = st.integers(min_value=1, max_value=100)

    @given(data=st.data())
    def test_number_of_nodes(self, data):
        n = data.draw(self.nodes, label="Number of nodes")
        m = data.draw(st.integers(min_value=(n - 1), max_value=(n ** 2)), label="Number of edges")
        _, edges = random_graph(n, m)
        assert len(edges) == n ** 2

    @given(data=st.data())
    def test_number_of_edges(self, data):
        n = data.draw(self.nodes, label="Number of nodes")
        m = data.draw(st.integers(min_value=(n - 1), max_value=(n ** 2)), label="Number of edges")
        _, edges = random_graph(n, m)
        assert sum(edges) == m

    @given(data=st.data())
    def test_edges_at_least(self, data):
        n = data.draw(self.nodes, label="Number of nodes")
        m = data.draw(st.integers(max_value=(n - 2)), label="Number of edges")
        with pytest.raises(ValueError, match=r".*number of edges smaller then.*"):
            random_graph(n, m)

    @given(data=st.data())
    def test_edges_at_most(self, data):
        n = data.draw(self.nodes, label="Number of nodes")
        m = data.draw(st.integers(min_value=(n ** 2 + 1)), label="Number of edges")
        with pytest.raises(ValueError, match=r".*at most.*"):
            random_graph(n, m)
