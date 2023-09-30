.. _diffusion-Non_linear_general_poisson_equation:

diffusion/Non_linear_general_poisson_equation.py
================================================

**Description**


Example usage of the non linear diffusion and non linear volume terms.

The example is an adaptation of:
https://sfepy.org/doc-devel/examples/diffusion-poisson_field_dependent_material.html

:ref:`diffusion-poisson_field_dependent_material`

Find :math:`T(t)` for :math:`t \in [0, t_{\rm final}]` such that:

.. math::
   \int_{\Omega} c(T) \nabla s \cdot \nabla T + \int_{\Omega} g(T) \cdot s
    = 0
    \;, \quad \forall s \;.

where :math:`c(T) and g(T)` are the :math:`T` dependent coefficients.




:download:`source code </../sfepy/examples/diffusion/Non_linear_general_poisson_equation.py>`

.. literalinclude:: /../sfepy/examples/diffusion/Non_linear_general_poisson_equation.py

