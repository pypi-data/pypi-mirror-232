from ..MathFunc import Vector

class FinancialAnalysis:
    """
    Financial Analysis Class.

    This class provides methods for financial analysis, including NPV and IRR calculations.

    Methods:
        - __init__(self): Initialize an instance of the FinancialAnalysis class.
        - npv(self, cash_flows: Vector), discount_rate: float) -> float: Calculate the Net Present Value (NPV) of cash flows.
        - irr(self, cash_flows: Vector) -> float: Calculate the Internal Rate of Return (IRR) of cash flows.

    Example:
        # Create a FinancialAnalysis instance
        analyzer = FinancialAnalysis()

        # Calculate NPV for cash flows with a discount rate of 0.1
        cash_flows = [-100, 50, 60, 70]
        discount_rate = 0.1
        npv_result = analyzer.npv(cash_flows, discount_rate)

        # Calculate IRR for cash flows
        irr_result = analyzer.irr(cash_flows)
    """

    def __init__(self):
        """
        Initialize an instance of the FinancialAnalysis class.
        """
        pass

    def npv(self, cash_flows, discount_rate: float) -> float:
        """
        Calculate the Net Present Value (NPV) of cash flows.

        Args:
            cash_flows (List[float]): List of cash flows over time.
            discount_rate (float): The discount rate.

        Returns:
            float: The NPV value.
        """
        if not isinstance(cash_flows, Vector):
            cash_flows = Vector(cash_flows)
        npv_value = 0
        for i, cash_flow in enumerate(cash_flows):
            npv_value += cash_flow / (1 + discount_rate) ** i
        return npv_value

    def irr(self, cash_flows, max_iterations:int=1000, irr_guess:float = 0.1, tolerance:float=1e-6) -> float:
        """
        Calculate the Internal Rate of Return (IRR) of cash flows.

        Args:
            cash_flows (Vector): List of cash flows over time.
            max_iterations (int, optional): Maximum number of iterations for IRR calculation. Defaults to 1000.
            irr_guess (float, optional): Initial guess for IRR. Defaults to 0.1.
            tolerance (float, optional): Tolerance level for convergence. Defaults to 1e-6.

        Raises:
            ValueError: Raised if the IRR calculation does not converge within the specified parameters.

        Returns:
            float: The calculated IRR value.
        """
        if not isinstance(cash_flows, Vector):
            cash_flows = Vector(cash_flows)
        for _ in range(max_iterations):
            npv = self.npv(cash_flows, irr_guess)
            npv_derivative = 0
            for t, cash_flow in enumerate(cash_flows):
                npv_derivative -= t * cash_flow / ((1 + irr_guess) ** (t + 1))
            
            # Newton-Raphson step
            irr_guess -= npv / npv_derivative

            # Check for convergence
            if abs(npv) < tolerance:
                return irr_guess

        # If no convergence is reached, return None or raise an exception
        raise ValueError("IRR calculation did not converge")