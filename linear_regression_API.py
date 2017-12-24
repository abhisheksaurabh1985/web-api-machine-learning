from flask import Flask, jsonify, request
import pandas as pd
import os
from sklearn.externals import joblib
from sklearn.linear_model import LinearRegression


app = Flask(__name__)


@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # If request method is POST, get the JSON of the request body so that we can access data.
            data = request.get_json()
            # With the variable obtained in the previous step, access the key of the data we want and
            # convert it into a float.
            years_of_experience = float(data["yearsOfExperience"])
            # Load the data into memory from the persisted file.
            lin_reg = joblib.load("./pickled_files/linear_regression_model.pkl")
        except ValueError:
            return jsonify("Please enter a number.")
        # Parse the  variable into the predict method of the linear regression model.
        # The variable was pulled into memory when the when  we loaded our flask app at start-up.
        # Change the output of the predict method to a list as object of type 'ndarray' isn't JSON serializable.
        # Finally, call 'jsonify' method of Flask to send the response data as JSON.
        return jsonify(lin_reg.predict(years_of_experience).tolist())


@app.route("/retrain", methods=['POST'])
def retrain():
    if request.method == 'POST':
        data = request.get_json()

        try:
            training_set = joblib.load("./pickled_files/training_data.pkl")
            training_labels = joblib.load("./pickled_files/training_labels.pkl")

            df = pd.read_json(data)

            df_training_set = df.drop(["Salary"], axis=1)
            df_training_labels = df["Salary"]

            df_training_set = pd.concat([training_set, df_training_set])
            df_training_labels = pd.concat([training_labels, df_training_labels])

            new_lin_reg = LinearRegression()
            new_lin_reg.fit(df_training_set, df_training_labels)

            os.remove("./pickled_files/linear_regression_model.pkl")
            os.remove("./pickled_files/training_data.pkl")
            os.remove("./pickled_files/training_labels.pkl")

            joblib.dump(new_lin_reg, "./pickled_files/linear_regression_model.pkl")
            joblib.dump(df_training_set, "./pickled_files/training_data.pkl")
            joblib.dump(df_training_labels, "./pickled_files/training_labels.pkl")

            lin_reg = joblib.load("./pickled_files/linear_regression_model.pkl")
        except ValueError as e:
            return jsonify("Error when retraining - {}".format(e))

        return jsonify("Retrained model successfully.")


@app.route("/currentDetails", methods=['GET'])
def current_details():
    if request.method == 'GET':
        try:
            lr = joblib.load("./pickled_files/linear_regression_model.pkl")
            training_set = joblib.load("./pickled_files/training_data.pkl")
            labels = joblib.load("./pickled_files/training_labels.pkl")

            return jsonify({"score": lr.score(training_set, labels),
                            "coefficients": lr.coef_.tolist(), "intercepts": lr.intercept_})
        except (ValueError, TypeError) as e:
            return jsonify("Error when getting details - {}".format(e))


if __name__ == '__main__':
    app.run(debug=True)

