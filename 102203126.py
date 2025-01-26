import pandas as pd
import numpy as np
import sys
import os


class Topsis:
    def __init__(self, filename):
        # Check if the file exists
        if not os.path.isfile(filename):
            raise FileNotFoundError("Error: File not found.")

        # Load the file based on the file extension
        if filename.endswith('.csv'):
            self.data = pd.read_csv(filename)
        elif filename.endswith('.xlsx'):
            self.data = pd.read_excel(filename)
        else:
            raise ValueError("Error: Unsupported file format. Please provide a CSV or XLSX file.")

        # Validate that the file has at least three columns
        if self.data.shape[1] < 3:
            raise ValueError("Error: Input file must contain three or more columns.")

        # Extract the decision matrix (from the 2nd column onwards)
        self.decision_matrix = self.data.iloc[:, 1:].values

        # Check if all values in the decision matrix are numeric
        if not np.issubdtype(self.decision_matrix.dtype, np.number):
            raise ValueError("Error: From 2nd to last columns must contain numeric values only.")

        self.features = self.decision_matrix.shape[1]  # Number of criteria (columns)
        self.samples = self.decision_matrix.shape[0]  # Number of alternatives (rows)

    def evaluate(self, weights, impacts):
        # Validate that weights and impacts have the correct lengths
        if len(weights) != self.features or len(impacts) != self.features:
            raise ValueError(
                "Error: Number of weights, impacts, and columns (from 2nd to last) must be the same."
            )

        # Validate that all impacts are either '+' or '-'
        if not all(impact in ["+", "-"] for impact in impacts):
            raise ValueError("Error: Impacts must be either '+' or '-'.")

        # Step 1: Normalize the decision matrix using the Euclidean norm
        norm_matrix = self.decision_matrix / np.sqrt((self.decision_matrix**2).sum(axis=0))

        # Step 2: Apply weights to the normalized decision matrix
        weighted_matrix = norm_matrix * weights

        # Step 3: Determine the ideal best and worst values
        ideal_best = np.where(
            np.array(impacts) == "+",
            weighted_matrix.max(axis=0),  # Maximize benefit criteria
            weighted_matrix.min(axis=0)  # Minimize cost criteria
        )
        ideal_worst = np.where(
            np.array(impacts) == "+",
            weighted_matrix.min(axis=0),  # Minimize benefit criteria
            weighted_matrix.max(axis=0)  # Maximize cost criteria
        )

        # Step 4: Calculate the distances to the ideal best and worst values
        distance_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
        distance_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))

        # Step 5: Calculate the TOPSIS score
        scores = distance_worst / (distance_best + distance_worst)

        # Add scores and ranks to the original dataset
        self.data["Topsis Score"] = scores
        self.data["Rank"] = self.data["Topsis Score"].rank(ascending=False).astype(int)

        return self.data


def main():
    # Validate the number of command-line arguments
    if len(sys.argv) != 5:
        print("Usage: python <script_name.py> <input_file> <weights> <impacts> <output_file>")
        sys.exit(1)

    # Read command-line arguments
    input_file = sys.argv[1]
    try:
        weights = list(map(float, sys.argv[2].split(',')))  # Parse weights as floats
        impacts = sys.argv[3].split(',')  # Parse impacts as strings
        output_file = sys.argv[4]

        # Validate that the output file has a supported extension
        if not (output_file.endswith('.csv') or output_file.endswith('.xlsx')):
            raise ValueError("Error: Unsupported output file format. Please use CSV or XLSX.")

        # Create a Topsis instance and evaluate
        topsis = Topsis(input_file)
        result = topsis.evaluate(weights, impacts)

        # Save the result to the specified output file
        if output_file.endswith('.csv'):
            result.to_csv(output_file, index=False)
        elif output_file.endswith('.xlsx'):
            result.to_excel(output_file, index=False)

        print(f"Output saved to {output_file}")

    except ValueError as e:
        print(e)
        sys.exit(1)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
