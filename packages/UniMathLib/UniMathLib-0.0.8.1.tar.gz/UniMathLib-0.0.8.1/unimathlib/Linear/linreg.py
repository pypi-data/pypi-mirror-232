from ..MathFunc import Matrix, Vector
import sys
import io
class LinearRegression:
    """
    Linear Regression Model.

    This class implements a simple linear regression model using the method of least squares.

    Attributes:
        coefficients (Vector): The coefficients of the linear regression model, including the intercept.

    Methods:
        - __init__(self): Initialize an instance of the LinearRegression class.
        - fit(self, X: Matrix, y: Matrix): Fit the linear regression model to the training data.
        - predict(self, X: Matrix): Predict target values for new data.

    Example:
        # Create a LinearRegression instance
        model = LinearRegression()

        # Fit the model to training data
        X_train = Matrix([[1], [2], [3], [4]])
        y_train = Matrix([2, 4, 6, 8])
        model.fit(X_train, y_train)

        # Make predictions
        X_test = Matrix([[5], [6]])
        predictions = model.predict(X_test)
    """
    def __init__(self):
        """
        Initialize an instance of the LinearRegression class.

        The coefficients attribute is set to None initially.
        """
        self.coefficients = None

    def fit(self, X:Matrix, y:Matrix):
        """
        Fit the linear regression model to the training data.

        Args:
            X (Matrix): The feature matrix. Each row represents an observation.
            y (Matrix): The target values.

        Raises:
            ValueError: If the lengths of X and y do not match.

        Returns:
            None
        """
        if not isinstance(X, Matrix) or not isinstance(y, Matrix): 
            X = Matrix(X)
            y = Matrix(y)
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        if len(X) != len(y):
            raise ValueError("len(X) must be equal len(y)")

        X_reg = Matrix(X.shape[0],X.shape[1]+1)
        for i in range(len(X)):
            n_r = Vector(X.shape[1]+1)
            n_r[0], n_r[1:] = 1, X[i]
            X_reg[i] = n_r
        X_transpose = X_reg.transpose()
        XTX = X_transpose*X_reg
        XTY = X_transpose*y
        self.coefficients = XTX.LU_solver(XTY)
        sys.stdout = original_stdout

    def predict(self, X):
        """
        Predict target values for new data.

        Args:
            X (Matrix): The feature matrix for prediction. Each row represents an observation.

        Raises:
            ValueError: If the model has not been trained (fit) yet.

        Returns:
            Vector: Predicted target values.
        """
        if self.coefficients is None:
            raise ValueError("Use fit for model teach.")
        if not isinstance(X, Matrix): 
            X = Matrix(X)
        X_reg = Matrix(X.shape[0],X.shape[1]+1)
        for i in range(len(X)):
            n_r = Vector(X.shape[1]+1)
            n_r[0], n_r[1:] = 1, X[i]
            X_reg[i] = n_r
        return Vector([Vector(x) * Vector([el[0] for el in self.coefficients.matrix]) for x in X_reg])

