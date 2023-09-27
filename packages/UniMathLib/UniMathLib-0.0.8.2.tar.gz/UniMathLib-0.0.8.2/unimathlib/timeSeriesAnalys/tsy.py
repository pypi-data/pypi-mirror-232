from ..MathFunc import Vector
class TimeSeriesAnalysis:
    """
    Time Series Analysis Class.

    This class provides methods for analyzing time series data, including moving average and exponential smoothing.

    Attributes:
        data Vector: The time series data.

    Methods:
        - __init__(self, data: Vector): Initialize an instance of the TimeSeriesAnalysis class with time series data.
        - moving_average(self, window_size: int) -> Vector: Calculate the moving average of the time series.
        - exponential_smoothing(self, alpha: float) -> Vector: Apply exponential smoothing to the time series.

    Example:
        # Create a TimeSeriesAnalysis instance with time series data
        data = [10, 15, 12, 18, 20, 22, 25]
        analyzer = TimeSeriesAnalysis(data)

        # Calculate a 3-day moving average
        moving_avg = analyzer.moving_average(window_size=3)

        # Apply exponential smoothing with alpha = 0.2
        smoothed_data = analyzer.exponential_smoothing(alpha=0.2)

    """

    def __init__(self, data):
        """
        Initialize an instance of the TimeSeriesAnalysis class with time series data.

        Args:
            data (Vector): The time series data.
        """
        if not isinstance(data, Vector):
            data = Vector(data)
        self.data = data

    def moving_average(self, window_size: int) -> Vector:
        """
        Calculate the moving average of the time series.

        Args:
            window_size (int): The size of the moving average window.

        Returns:
            Vector: A list of moving average values.
        """
        moving_averages = Vector()
        for i in range(len(self.data) - window_size + 1):
            window = self.data[i:i + window_size]
            average = sum(window) / window_size
            moving_averages.append(average)
        return moving_averages

    def exponential_smoothing(self, alpha: float) -> Vector:
        """
        Apply exponential smoothing to the time series.

        Args:
            alpha (float): Smoothing parameter (0 < alpha < 1).

        Returns:
            Vector: A list of smoothed values.
        """
        smoothed_data = Vector([self.data[0]])  # Initial value
        for i in range(1, len(self.data)):
            smoothed_value = alpha * self.data[i] + (1 - alpha) * smoothed_data[-1]
            smoothed_data.append(smoothed_value)
        return smoothed_data
