def output_layout(self, flexible: bool=True) -> Layout:
    """
        Handle output layout generation for matrix multiplication.

        Args:
            out_dtype: Optional output dtype. If not provided, infer from inputs
            flexible: If True, return FlexibleLayout, otherwise FixedLayout
        """
    (mat1, mat2) = self.mat1mat2()
    out_dtype = self.out_dtype()
    (*b1, m, k1) = mat1.get_size()
    (*b2, k2, n) = mat2.get_size()
    b = [V.graph.sizevars.check_equals_and_simplify(a, b) for (a, b) in zip(b1, b2)]
    size = [*b, m, n]
    if flexible:
        return FlexibleLayout(self.device(), out_dtype, size)
    else:
        return FixedLayout(self.device(), out_dtype, size)