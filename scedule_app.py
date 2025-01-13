import streamlit as st
import pandas as pd
import numpy as np

def calculate_clash_matrix(student_data):
    subjects = student_data.columns[1:]
    clash_matrix = pd.DataFrame(0, index=subjects, columns=subjects)

    for subject_1 in subjects:
        for subject_2 in subjects:
            common_students = (
                (student_data[subject_1].notnull()) & (student_data[subject_2].notnull())
            ).sum()
            clash_matrix.at[subject_1, subject_2] = common_students
            if subject_1 == subject_2:
                clash_matrix.at[subject_1, subject_2] = 0

    return clash_matrix

def get_possible_slots(subject, clash_matrix, subject_data):
    available_slots = []

    for day, row in subject_data.iterrows():
        for time in row.index[1:]:
            running_classes = []
            for classroom, subjects in subject_data.loc[day, time].items():
                if pd.notna(subjects):
                    running_classes.extend(subjects.split()) 
            
            no_conflict = all(
                clash_matrix.at[subject, running_class] == 0
                for running_class in running_classes
                if running_class in clash_matrix.index
            )

            if no_conflict :
                available_slots.append((day, time))

    return list(set(available_slots))

def highlight_slots(possible_slots, subject_data):
    
    styled_schedule = pd.DataFrame(index= subject_data.index.unique(),columns=subject_data.columns[1:])

    for day, time in possible_slots:
        if day in subject_data.index and time in subject_data.columns[1:]:
            styled_schedule.loc[day, time] = "Available"

    def apply_highlight(val):
        if "Available" in str(val):  # Check if the cell is marked
            return "background-color: yellow; font-weight: bold;"
        return ""

    return styled_schedule.reset_index().style.applymap(apply_highlight)

st.title("Student Scheduling and Clash Analysis")

st.sidebar.header("Upload Student Data")
student_file = st.sidebar.file_uploader("Upload an Excel file for student data", type=["xlsx"])
if student_file:
    student_data = pd.read_excel(student_file)

    subjects_in_student_data = list(student_data.columns[1:])
    with st.expander("Student Data"):
        st.dataframe(student_data, use_container_width=True)

st.sidebar.header("Upload Subject Data")
subject_file = st.sidebar.file_uploader("Upload an Excel file for subject schedule", type=["xlsx"])
if subject_file:
    subject_data = pd.read_excel(subject_file, index_col=0)
    
    st.session_state["subject_data"] = subject_data.copy()
    with st.expander("Subject Schedule"):

        editable_subject_data = st.data_editor(subject_data, key="editable_subject_data", num_rows="dynamic", 
            column_config = {
                t:st.column_config.SelectboxColumn(options = subjects_in_student_data+[None],default = None) for t in subject_data.columns[1:]
            }
        )

        subjects_in_time_table = editable_subject_data.iloc[:,1:].stack().values

        if st.button("Save Changes to Schedule"):
            
            st.session_state["subject_data"] = editable_subject_data.copy()
            st.success("Schedule updated successfully!")

if student_file and subject_file:
    clash_matrix = calculate_clash_matrix(student_data)
    with st.expander("Clash Matrix"):
        st.dataframe(clash_matrix, use_container_width=True)
    st.session_state["clash_matrix"] = clash_matrix

st.sidebar.header("Reschedule")
if "clash_matrix" in st.session_state and "subject_data" in st.session_state:
    subject_to_reschedule = st.sidebar.selectbox("Select a subject to reschedule", st.session_state["clash_matrix"].index)
    if subject_to_reschedule:
        possible_slots = get_possible_slots(
            subject_to_reschedule,
            st.session_state["clash_matrix"],
            st.session_state["subject_data"],
        )
        
        st.subheader(f"Possible Reschedule Slots for {subject_to_reschedule}")
        if possible_slots:
            st.write("Highlighted table of available slots:")

            if len(set(subjects_in_time_table).difference(subjects_in_student_data))>0:

                error_list = list(set(subjects_in_time_table).difference(subjects_in_student_data))
                st.text(f"error in subject names {','.join(error_list)}")


            styled_table = highlight_slots(possible_slots, st.session_state["subject_data"])
            st.dataframe(styled_table)
        else:
            st.write("No available slots found with zero conflicts.")


