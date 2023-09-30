import numpy as np


class TimeSeriesMetrics(object):
    """
    Description:

        Four different categories of Error Metrics for Time-Series:

          Scale-Dependent Metrics:(+Regression)
              MeanAbsoluteError(MAE), MeanSquareError(MSE), RootMeanSquareError(RMSE), RootMeanSquareLogError(RMSLE), R-Squared(R2)

          Percentage-Error Metrics:
              MeanAbsolutePercentageError(MAPE), SymmetricMeanAbsolutePrecentageError(sMAPE)

          Relative-Error Metrics:(benchmark required)
              MedianRelativeAbsoluteError(MdRAE), GeometricMeanAbsoluteError(GMRAE)

          Scale-Free Error Metrics:
              MeanAbsoluteScaleError(MASE)
    

    Evaluation Metrics for Time-Series:

    Args:
        target: list
        list of true numerical values/number that has to be forecasted 
            --> y_test

        forecast: list
        list of values forecasted corresponding to the target values

        k:
        integer representing the number of features used for prediction in regression

        train:
        list of numerical values/number used for training 
            --> y_train

        bncmrk:
        list of benchmark forecast results for M seasonal period
            --> y_t-M or y_t-1

    """

    def __init__(self, target, forecast, k=1, train=None, bnchmrk=None):
        self.target = target
        self.forecast = forecast
        self.train = train
        self.bnchmrk = bnchmrk
        self.k = k
        self._compute_metrics(target, forecast)

    def _compute_metrics(self, target, forecast, k=1, train=None, bnchmrk=None):
        self.n = len(forecast)
        target, forecast = np.array(target), np.array(forecast)
        self.mean = np.mean(target)

        # Operations used for Scale-Dependent Metrics:
        self.absolute_diff = np.abs(target - forecast)
        self.TSS = np.sum(np.square(forecast - self.mean))
        self.RSS = np.sum(np.square(forecast - target))

        # Operations used for Percentage-Error Metrics
        self.absolute_precentage_diff = np.abs((target - forecast) / target * 100)
        self.absolute_symmetric_diff = np.abs(target - forecast) / (
            (np.abs(target) + np.abs(forecast))
        )

        # Operations used for Relative-Error Metrics
        self.absolute_bnchmrk_diff = np.abs(target - bnchmrk)
        self.absolute_scaled_diff = self.absolute_diff / self.absolute_bnchmrk_diff

        # Operations used for Scale-Free Error Metrics
        self.MAE_in_sample = self.train[:-1] - self.train[1:]

        # Metrics
        # Scale-Dependent Metrics:
        self.MAE = np.mean(self.absolute_diff)
        self.MSE = np.mean(np.square(self.absolute_diff))
        self.RMSE = np.sqrt(self.MSE)
        self.RMSLE = np.log(self.RMSE)
        self.R2 = 1 - self.RSS / self.TSS
        self.adjusted_R2 = 1 - ((self.n - 1) / self.n - k - 1) * (1 - self.R2)

        # Percentage-Error Metrics:
        self.MAPE = np.mean(self.absolute_precentage_diff)
        self.sMAPE = np.mean(self.absolute_symmetric_diff * 100)

        # Relative-Error Metrics:
        self.MdRAE = np.median(self.absolute_scaled_diff)
        self.GMRAE = np.exp(np.mean(np.log(self.absolute_scaled_diff)))

        # Scale-Free Error Metrics:
        self.MASE = self.MAE / self.MAE_in_sample

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

    def get_MAPE(self):
        """
        Returns:
         Mean Absolute Percentage Error a percentage as float >0 and optimum <5%
        """
        return self.MAPE

    def get_sMAPE(self):
        """
        Returns:
         Symmetric Mean Absolute Percentage Error a percentage as float in range(0-100)
        """
        return self.sMAPE

    def get_MdRAE(self):
        """
        Returns:
         Median Relative Absolute Error as float, and should be <1
        """
        return self.MdRAE

    def get_GMRAE(self):
        """
        Returns:
         Geoemetric Mean Relative Absolute Error as float, and should be <1
        """
        return self.GMRAE

    def get_MASE(self):
        """
        Returns:
         Mean Absolute Scaled Error as a float, and should be <1
        """
        return self.MASE
