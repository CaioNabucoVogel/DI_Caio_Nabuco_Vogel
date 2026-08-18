def mat1mat2(self) -> tuple[Any, Any]:
    """
        Get the mat1 and mat2 nodes.

        Returns:
            A tuple of (mat1, mat2) nodes
        """
    nodes = self.nodes()
    return (nodes[self._mat1_idx], nodes[self._mat2_idx])