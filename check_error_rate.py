import pandas as pd

def analyze_answer_sets():
    # File name referenced verbatim
    file_path = "Llama-3.1-8B-Instruct_piped_strong_negation_results_processed_results.xlsx"
    answer_column = "answer_sets"
    
    # UPDATE THIS to match the column that contains your True/False results
    correctness_column = "correct" 

    try:
        print(f"Loading data from {file_path}...")
        df = pd.read_excel(file_path)

        # 1. Check if the required columns exist
        if answer_column not in df.columns:
            print(f"Error: The column '{answer_column}' was not found.")
            print(f"Available columns are: {', '.join(df.columns)}")
            return
            
        col_data = df[answer_column].astype(str)

        # 2. Identify the malformed rows
        unknown_mask = col_data.str.contains("UNKNOWN", case=False, na=False)
        unsatisfiable_mask = col_data.str.contains("unsatisfiable", case=False, na=False)
        error_mask = col_data.str.contains("error", case=False, na=False)

        print("\n--- Malformed Counts ---")
        print(f"- UNKNOWN: {unknown_mask.sum()}")
        print(f"- unsatisfiable: {unsatisfiable_mask.sum()}")
        print(f"- error: {error_mask.sum()}")

        # 3. Calculate Accuracy Disregarding Malformed Programs
        if correctness_column in df.columns:
            # Combine masks to flag any row that is malformed
            malformed_mask = unknown_mask | unsatisfiable_mask | error_mask
            
            # Filter the dataframe to KEEP only rows that are NOT malformed
            valid_df = df[~malformed_mask]
            
            # Count how many of the valid rows evaluated to True
            # (Converts to lowercase string to safely catch True, true, TRUE)
            correct_mask = valid_df[correctness_column].astype(str).str.lower() == "true"
            
            total_valid = len(valid_df)
            total_correct = correct_mask.sum()
            
            if total_valid > 0:
                accuracy = (total_correct / total_valid) * 100
                print("\n--- Accuracy on Valid Programs ---")
                print(f"Total valid programs: {total_valid} (out of {len(df)})")
                print(f"Correct valid programs: {total_correct}")
                print(f"Accuracy: {accuracy:.2f}%")
            else:
                print("\n--- Accuracy ---")
                print("No valid programs remained after filtering.")
        else:
            print(f"\n--- Accuracy ---")
            print(f"Could not calculate accuracy: Column '{correctness_column}' not found.")
            print(f"Please update the 'correctness_column' variable in the script.")
            print(f"Available columns: {', '.join(df.columns)}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found in the current directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    analyze_answer_sets()