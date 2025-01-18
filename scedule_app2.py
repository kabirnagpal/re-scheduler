import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
def main():
    st.title("Subject Common Students Matrix")

    st.write("Upload a file containing student names and their enrolled subjects.")

    # File uploader
    uploaded_file = st.file_uploader("Upload your excel file", type=["xlsx"])

    if uploaded_file:
        # Load the uploaded file
        data = pd.read_excel(uploaded_file)

        # Display the uploaded data
        st.write("Uploaded Data:")
        st.dataframe(data)

        # Ensure the data contains the required format
        if len(data.columns) < 2:
            st.error("The file must contain at least two columns: one for student names and one for subjects.")
            return

        # Reshape the data to a binary matrix (students as rows, subjects as columns)
        student_subject_matrix = data.set_index(data.columns[0])
        student_subject_matrix = student_subject_matrix.replace({0:np.nan})

        values = student_subject_matrix.sum(axis=0)
        columns = values[values>15].index
        student_subject_matrix = student_subject_matrix[columns]
        # Replace all non-None values with 1, and None values with 0
        binary_matrix = student_subject_matrix.notnull().astype(int)

        # Transpose and dot product to get the subject co-occurrence matrix
        subject_co_occurrence_matrix = binary_matrix.T.dot(binary_matrix)

        # Fill diagonal with 0 since a subject can't have common students with itself
        np.fill_diagonal(subject_co_occurrence_matrix.values, 0)

        # Display the co-occurrence matrix
        st.write("Common Students Matrix Between Subjects:")
        st.dataframe(subject_co_occurrence_matrix)

        sns.heatmap(subject_co_occurrence_matrix,annot=True)
        fig = plt.plot()
        st.pyplot(fig)

        # Option to download the matrix
        csv = subject_co_occurrence_matrix.to_csv().encode('utf-8')
        st.download_button(
            label="Download Common Students Matrix as CSV",
            data=csv,
            file_name="common_students_matrix.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
