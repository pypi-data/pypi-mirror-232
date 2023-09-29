import numpy as np


class LogReg:

    def __init__(self, EPOCHS, LEARNING_RATE, X, y):
        self.theta0, self.theta1 = np.random.normal(size=(2,))
        self.EPOCHS = EPOCHS
        self.LEARNING_RATE = LEARNING_RATE
        self.X = X
        self.y = y
        self.predictions = []

    def _cost_function(self):
        """
        Summary
            The _cost_function method calculates the cost function for a linear regression model. It measures the
            average squared difference between the predicted values and the actual values.

        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the _cost_function method
            cost = model._cost_function()

            print(cost)

            Output:
            0.0

        Code Analysis
        Inputs
            self: The instance of the LogReg class.
            theta0: The intercept parameter of the linear regression model.
            theta1: The slope parameter of the linear regression model.
            X: The input features.
            y: The target values.

        Flow
            Initialize the total_cost variable to 0.
            Iterate over each element in the input features X.
            Calculate the predicted value predict using the linear regression equation: predict = theta0 + theta1 * X[i].
            Calculate the squared difference between the predicted value and the corresponding target value:
            (predict - y[i]) ** 2.
            Add the squared difference to the total_cost.
            Return the average cost by dividing the total_cost by the number of input features len(X).

        Outputs
            total_cost / len(X): The average cost, which represents the average squared difference between the predicted
            values and the actual values.
        """
        total_cost = 0
        for i in range(len(self.X)):
            predict = self.theta0 + self.theta1 * self.X[i]
            total_cost += (predict - self.y[i]) ** 2
            self.predictions.append(total_cost)
        return total_cost / len(self.X)

    def get_predictions(self):
        """Summary
            The get_predictions method is a part of the LogReg class and returns the list of predictions made by the linear regression model.
        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the get_predictions method
            predictions = model.get_predictions()

            print(predictions)

            Output:
            [0, 0, 0]
        Code Analysis
        Inputs
            None

        Flow
            The get_predictions method returns the list of predictions made by the linear regression model. This list is stored in the predictions attribute of the LogReg class. The method simply returns this attribute.

        Outputs
            predictions: The list of predictions made by the linear regression model.
        """
        return self.predictions


class GD(LogReg):

    def _der_theta0(self):
        """
        Summary
            The _der_theta0 method calculates the derivative of the cost function with respect to the intercept
            parameter (theta0) in a linear regression model.

        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the _der_theta0 method
            derivative = model._der_theta0()

            print(derivative)

            Output:
            0.0

        Code Analysis
        Inputs
            self: The instance of the LogReg class.
            theta0: The intercept parameter of the linear regression model.
            theta1: The slope parameter of the linear regression model.
            X: The input features.
            y: The target values.

        Flow
            Initialize the total_cost variable to 0.
            Iterate over each element in the input features X.
            Calculate the predicted value predict using the linear regression equation: predict = theta0 + theta1 * X[i].
            Calculate the derivative of the cost function with respect to theta0 as 2 * (predict - y[i]).
            Add the derivative to the total_cost.
            Return the average derivative by dividing the total_cost by the number of input features len(X).

        Outputs
            total_cost / len(X): The average derivative, which represents the derivative of the cost function with
            respect to the intercept parameter (theta0) in the linear regression model.
        """
        total_cost = 0
        for i in range(len(self.X)):
            predict = self.theta0 + self.theta1 * self.X[i]
            total_cost += 2 * (predict - self.y[i])
        return total_cost / len(self.X)

    def _der_theta1(self):
        """
        Summary
            The _der_theta1 method calculates the derivative of the cost function with respect to the slope parameter (theta1) in a linear regression model.

        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the _der_theta1 method
            derivative = model._der_theta1()

            print(derivative)

            Output:
            0.0

        Code Analysis
        Inputs
            self: The instance of the LogReg class.
            theta0: The intercept parameter of the linear regression model.
            theta1: The slope parameter of the linear regression model.
            X: The input features.
            y: The target values.

        Flow
            Initialize the total_cost variable to 0.
            Iterate over each element in the input features X.
            Calculate the predicted value predict using the linear regression equation: predict = theta0 + theta1 * X[i].
            Calculate the derivative of the cost function with respect to theta1 as 2 * (predict - y[i]) * X[i].
            Add the derivative to the total_cost.
            Return the average derivative by dividing the total_cost by the number of input features len(X).

        Outputs
            total_cost / len(X): The average derivative, which represents the derivative of the cost function with respect to the slope parameter (theta1) in the linear regression model.
        """
        total_cost = 0
        for i in range(len(self.X)):
            predict = self.theta0 + self.theta1 * self.X[i]
            total_cost += 2 * (predict - self.y[i]) * self.X[i]
        return total_cost / (len(self.X))

    def fit(self):
        """
        Summary
            The fit method in the LogReg class is used to train the linear regression model by updating the values of
            the intercept parameter (theta0) and the slope parameter (theta1) over a specified number of epochs.
        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the fit method to train the model
            model.fit()

            # Get the updated values of theta0 and theta1
            theta0, theta1 = model.get_cofs()

            print(theta0, theta1)

            Output:
            0.0, 2.0
        Code Analysis
        Inputs
            self: The instance of the LogReg class.
            EPOCHS: The number of training iterations.
            LEARNING_RATE: The learning rate, which determines the step size for updating the parameters.
            X: The input features.
            y: The target values.

        Flow
            Iterate over the specified number of epochs.
            Calculate the derivative of the cost function with respect to theta0 using the _der_theta0 method.
            Calculate the derivative of the cost function with respect to theta1 using the _der_theta1 method.
            Update the value of theta0 by subtracting the product of the learning rate and the derivative of theta0 from
            the current value of theta0.
            Update the value of theta1 by subtracting the product of the learning rate and the derivative of theta1 from
            the current value of theta1.

        Outputs
            None. The method updates the values of theta0 and theta1 in the LogReg instance.
        """
        for _ in range(self.EPOCHS):

            self.theta0 = self.theta0 - self.LEARNING_RATE * self._der_theta0()
            self.theta1 -= self.LEARNING_RATE * self._der_theta1()

    def get_coefs(self):
        """
        Summary
            The get_cofs method in the LogReg class returns the values of the intercept parameter (theta0) and the slope
            parameter (theta1) of a linear regression model.

        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the get_cofs method
            theta0, theta1 = model.get_cofs()

            print(theta0, theta1)

            Output:
            0, 0

        Code Analysis
        Inputs
            self: The instance of the LogReg class.

        Flow
            The get_cofs method simply returns the values of the theta0 and theta1 attributes of the LogReg instance.

        Outputs
            theta0: The value of the intercept parameter (theta0) in the linear regression model.
            theta1: The value of the slope parameter (theta1) in the linear regression model.
        """
        return self.theta0, self.theta1

    def get_theta0(self):
        """
        Summary
            The get_theta0 method in the LogReg class returns the value of the intercept parameter (theta0) in a linear regression model.

        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the get_theta0 method
            theta0 = model.get_theta0()

            print(theta0)

            Output:
            0

        Code Analysis
        Inputs
            self: The instance of the LogReg class.

        Flow
            The get_theta0 method simply returns the value of the theta0 attribute of the LogReg instance.

        Outputs
            theta0: The value of the intercept parameter (theta0) in the linear regression model.
        """
        return self.theta0

    def get_theta1(self):
        """
        Summary
            The get_theta1 method in the LogReg class returns the value of the slope parameter (theta1) in a linear regression model.

        Example Usage
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])
            theta1 = model.get_theta1()

            print(theta1)

            Output:
            0

        Code Analysis
        Inputs
            self: The instance of the LogReg class.

        Flow
            The get_theta1 method simply returns the value of the theta1 attribute of the LogReg instance.

        Outputs
            theta1: The value of the slope parameter (theta1) in the linear regression model.
        """
        return self.theta1

    def get_cost(self):
        """
        Summary
            The get_cost method in the LogReg class returns the cost function value for a linear regression model. The cost function measures the average squared difference between the predicted values and the actual values.

        Example Usage
            # Create an instance of the LogReg class
            model = LogReg(theta0=0, theta1=0, EPOCHS=100, LEARNING_RATE=0.01, X=[1, 2, 3], y=[2, 4, 6])

            # Call the get_cost method
            cost = model.get_cost()

            print(cost)

            Output:
            0.0

        Code Analysis
        Inputs
            self: The instance of the LogReg class.

        Flow
            The get_cost method calls the _cost_function method to calculate the cost function value.
            The _cost_function method iterates over each element in the input features X.
            For each element, it calculates the predicted value predict using the linear regression equation: predict = theta0 + theta1 * X[i].
            It calculates the squared difference between the predicted value and the corresponding target value: (predict - y[i]) ** 2.
            It adds the squared difference to the total_cost.
            Finally, it returns the average cost by dividing the total_cost by the number of input features len(X).

        Outputs
            total_cost / len(X): The average cost, which represents the average squared difference between the predicted values and the actual values.
        """
        return self._cost_function()


class SGD(LogReg):
    pass
