import numpy as np


class RegressionMetrics(object):
    """
    Description:

        MeanAbsoluteError(MAE)
        MeanSquareError(MSE)
        RootMeanSquareError(RMSE)
        RootMeanSquareLogError(RMSLE)
        R-Squared(R2)
        Adjusted_R2

    Evaluation Metrics for Time-Series:

    Args:
        target: list
        list of true numerical values/number that has to be predicted

        predicted: list
        list of values prediction corresponding to the target values

        k:
        integer representing the number of features used for prediction in regression
    """

    def __init__(self, target, prediction, k=1):
        self.target = target
        self.prediction = prediction
        self.k = k
        self._compute_metrics(target, prediction)

    def _compute_metrics(self, target, prediction, k=1):
        self.n = len(prediction)
        target, prediction = np.array(target), np.array(prediction)
        self.mean = np.mean(target)

        self.absolute_diff = np.abs(target - prediction)
        self.TSS = np.sum(np.square(prediction - self.mean))
        self.RSS = np.sum(np.square(prediction - target))

        self.MAE = np.mean(self.absolute_diff)
        self.MSE = np.mean(np.square(self.absolute_diff))
        self.RMSE = np.sqrt(self.MSE)
        self.RMSLE = np.log(self.RMSE)
        self.R2 = 1 - self.RSS / self.TSS
        self.adjusted_R2 = 1 - ((self.n - 1) / self.n - k - 1) * (1 - self.R2)

    def get_MAE(self):
        """
        Returns:
         Mean Absolute Error as float
        """
        return self.MAE

    def get_MSE(self):
        """
        Returns:
         Mean Square Error as float
        """
        return self.MSE

    def get_RSME(self):
        """
        Returns:
         Root Mean Square Error as float
        """
        return self.RSME

    def get_RMSLE(self):
        """
        Returns:
         Root Mean Square Log Error as float
        """
        return self.RMSLE

    def get_R2(self):
        """
        Returns:
         R-Square value as float between optimum (0-1)
        """
        return self.R2

    def get_adjusted_R2(self):
        """
        Returns:
         Adjusted R-Square value as float between (0-1)
        """
        return self.adjusted_R2
