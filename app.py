import streamlit as st
import numpy as np

# Helper: map labels to indices (0-based)
def idx(label, labels_list):
    try:
        return labels_list.index(label)
    except ValueError:
        return 0



st.set_page_config(page_title="Enhanced Course Workload Estimator", layout="wide")

# Lookup arrays (converted from R)
pagesperhour = np.array([
    [[67, 47, 33], [33, 24, 17], [17, 12, 9]],
    [[50, 35, 25], [25, 18, 13], [13, 9, 7]],
    [[40, 28, 20], [20, 14, 10], [10, 7, 5]]
])  # shape (3,3,3)


hoursperwriting = np.array([
    [  # Double-spaced (250 Words)
        [0.75, 1.5, 3.0],   # No Drafting for Reflection, Argument, Research
        [1.0, 2.0, 3.0],   # Minimal Drafting
        [1.25, 2.5, 4.0]     # Extensive Drafting
    ],
    [  # Single-spaced (500 Words)
        [1.5, 3.0, 6.0],    # No Drafting
        [2.0, 4.0, 6.0],    # Minimal Drafting
        [2.5, 5.0, 8.0]    # Extensive Drafting
    ]
    ])  # shape (2,3,3)

#outermost list - first dimension - page density (double spaced or single)
#middle list - genre (reflection, argument, research) 
#inner list - drafting intensity (none, minimal, extensive) 




st.title("Course Workload Estimator")

st.markdown("""
this is broken work in progress
<div style="text-align: center; font-size: 16px; line-height: 1.6; border: 1px solid #cfcfcf">

Course Workload Estimator - [revised by Mel Kenfield](http://linktr.ee/mbkenfield) for needs of TCC-Connect classes  
Based on [Workload Estimator 2.0](https://cat.wfu.edu/resources/workload2/) 
Original Research & Design by [Betsy Barre](https://cat.wfu.edu/about/our-team/), [Allen Brown](https://oe.wfu.edu/about/), and [Justin Esarey](http://www.justinesarey.com)  
[For more details on workload estimation and research see Wake Forest University](https://cat.wfu.edu/resources/workload/estimationdetails/)

  <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank">
    <img src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" alt="CC BY-NC-SA 4.0">
  </a><br>
  <span>Licensed under CC BY-NC-SA 4.0.</span>
</div>
""", unsafe_allow_html=True)




# Layout: 4 columns like the original
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("COURSE INFO") # Do I want to restrict values or make it a drop-down? 
    classweeks = st.number_input("Class Duration (Weeks):", value=15, min_value=1, step=1)

    st.subheader("READING ASSIGNMENTS")
    st.markdown("This section estimates based on common pages")
    st.markdown("How would we calculate for typical freshman work?")
    st.markdown("Do we want a basic word count as well?")
    weeklypages = st.number_input("Pages Per Week:", value=0, min_value=0)
    readingdensity_labels = ["450 Words (Paperback)", "600 Words (Monograph)", "750 Words (Textbook)"]
    readingdensity = st.selectbox("Page Density:", readingdensity_labels, index=0)
    difficulty_labels = ["No New Concepts", "Some New Concepts", "Many New Concepts"]
    difficulty = st.selectbox("Difficulty:", difficulty_labels, index=0)
    readingpurpose_labels = ["Survey", "Learn", "Engage"]
    readingpurpose = st.selectbox("Purpose:", readingpurpose_labels, index=0)
    setreadingrate = st.checkbox("manually adjust reading rate", value=False)
    overridepagesperhour = None
        
    # Determine pages per hour
    if not setreadingrate:
        pph = pagesperhour[idx(difficulty, difficulty_labels), idx(readingpurpose, readingpurpose_labels), idx(readingdensity, readingdensity_labels)]
    else:
        pph = float(overridepagesperhour) if overridepagesperhour is not None else 1.0
    
    st.write("Based on the parameters above, the estimated reading rate is", f"{pph} pages per hour")
    if setreadingrate:
        overridepagesperhour = st.number_input("Pages Read Per Hour:", value=10.0, min_value=0.0, step=1.0)

    st.subheader("VIDEOS / PODCASTS")
    weeklyvideos = st.number_input("Hours Per Week (videos/podcasts):", value=0.0, min_value=0.0, step=0.5)
    
with col2:
    st.subheader("WRITING ASSIGNMENTS")
    st.markdown("This section estimates the time students spend writing assignments each week, based on page count, genre, and drafting requirements.")
    semesterpages = st.number_input("Pages Per Semester:", value=0, min_value=0)
    writtendensity_labels = ["250 Words (D-Spaced)", "500 Words (S-Spaced)"]
    writtendensity = st.selectbox("Page Density:", writtendensity_labels, index=0)
    writingpurpose_labels = ["Reflection/Narrative", "Argument", "Research"]
    writingpurpose = st.selectbox("Genre:", writingpurpose_labels, index=0)
    draftrevise_labels = ["No Drafting", "Minimal Drafting", "Extensive Drafting"]
    draftrevise = st.selectbox("Drafting:", draftrevise_labels, index=0)
    setwritingrate = st.checkbox("manually adjust writing rate", value=False)
    overridehoursperwriting = None
    if setwritingrate:
        overridehoursperwriting = st.number_input("Hours Per Written Page:", value=0.5, min_value=0.0, step=0.01)
    
    calculated_hpw = hoursperwriting[
    idx(writtendensity, writtendensity_labels),
    idx(draftrevise, draftrevise_labels),
    idx(writingpurpose, writingpurpose_labels)
    ]
    
    
    # Determine hours per writing page
    if not setwritingrate:
        hpw = hoursperwriting[idx(writtendensity, writtendensity_labels), idx(draftrevise, draftrevise_labels), idx(writingpurpose, writingpurpose_labels)]
    else:
        hpw = calculated_hpw + (float(overridehoursperwriting) if overridehoursperwriting is not None else 0.0)

        # hpw = float(overridehoursperwriting) if overridehoursperwriting is not None else 0.5

    # --- WRITING RATE OUTPUT ---
    col_writing_rate, col_override = st.columns([3, 1])

    with col_writing_rate:
        st.markdown(f"**Estimated Writing Rate:** {hpw} hours per page")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.container()
        


    # Recalculate total hours per week using hpw (already done later in your code)
    # (No other changes needed; hpw is now updated based on manual override if selected)



    
    st.subheader("DISCUSSION POSTS")
    
#    MATH IS BROKEN
## Continue working on discussions
    
    
    st.markdown("Check the research - how are they calculating the workload for these? ")
    calc_method = st.radio(
    "Calculate Discussion Posts By:",
    ["Total Posts (Semester)", "Posts Per Week"],
    index=1  # default to "Posts Per Week"
    )

    if calc_method == "Posts Per Week":
        postsperweek = st.number_input("Posts Per Week:", value=0, min_value=0, step=1)
        totalposts = 0  # placeholder
    else:
        totalposts = st.number_input("Total Posts (for semester):", value=0, min_value=0, step=1)
        postsperweek = 0  # placeholder
    
    postformat_options = ["Text", "Audio/Video"]
    postformat = st.selectbox("Format:", postformat_options, index=0)
    postlength_text = st.number_input("Avg. Length (Words) for text posts:", value=350, min_value=0)
    postlength_av = st.number_input("Avg. Length (Minutes) for audio/video posts:", value=0, min_value=0)

    setdiscussion = st.checkbox("Manually adjust discussion hours", value=False)
    overridediscussion = None
    if setdiscussion:
        overridediscussion = st.number_input("Hours Per Week (override):", value=1.0, min_value=0.0, step=0.1)
    
    if not setdiscussion:
        if calc_method == "Total Posts (Semester)":
            if postformat == "Text":
                posthours = (postlength_text * totalposts) / 250.0
            else:
                posthours = 0.18 * (postlength_av * totalposts) + ((postlength_av * totalposts) / 6.0)
            posthours_for_other = (postlength_av * totalposts) / 3.0 if postformat != "Text" else (postlength_text * totalposts) / 250.0

        else:  # Posts Per Week
            if postformat == "Text":
                posthours = (postlength_text * postsperweek) / 250.0
            else:
                posthours_for_total = 0.18 * (postlength_av * postsperweek) + ((postlength_av * postsperweek) / 6.0)
                posthours_for_other = (postlength_av * postsperweek) / 3.0
                posthours = posthours_for_total
    else:
        posthours = float(overridediscussion) if overridediscussion is not None else 0.0
        posthours_for_other = posthours

    # --- Display ---
    st.write(f"Estimated Discussion Hours: {posthours:.2f} hrs")
         
    
with col3:

    st.subheader("QUIZZES")
    st.write("Quizzes assume no additional study time beyond other assigned reading.")
    st.write("Quizzes add 1:1 to active/output time.")
    quizzes = st.number_input("Quizzes Per Semester:", value=0, min_value=0, step=1)    
    quizminutes = st.number_input("Time Estimate Per Quiz(Minutes):", value=20, min_value=0, step=5)
    quizhours = quizminutes / 60  # convert to hours for the workload calculation
    
    
    st.subheader("EXAMS")
    st.write("Exams are calculated as follows: ")
    st.write("Exam time added to output time; additional study/prep time added to processing/prep time")
    # Number of exams
    exams = st.number_input("Exams Per Semester:", value=0, min_value=0, step=1)
    # Exam time in minutes
    exam_length = st.number_input("Exam Time Limit (Minutes):", value=60, min_value=0, step=5)    
    examstudyhours = st.number_input("Additional Study Hours Per Exam:", value=5.0, min_value=0.0, step=0.5)
    # Proctored checkbox adds 15 minutes to the exam
    proctored = st.checkbox("Proctored Exam - Add 15 minutes for VDI/Respondus", value=False)
    if proctored:
        exam_length += 15
    # Convert total exam minutes to hours and add study hours
    examhours = (exam_length / 60) + examstudyhours


with col4:
    st.subheader("OTHER ASSIGNMENTS")
    otherassign = st.number_input("# Per Semester:", value=0, min_value=0, step=1)
    otherhours = st.slider("Hours Per Assignment:", min_value=0, max_value=50, value=0)
    other_engage = st.checkbox("Independent", value=False)

    st.subheader("CLASS MEETINGS")
    syncsessions = st.number_input("Live Meetings Per Week:", value=0, min_value=0, step=1)
    synclength = st.number_input("Meeting Length (Hours):", value=0.0, min_value=0.0, step=0.25)

    st.markdown("---")
    st.subheader("WORKLOAD ESTIMATES")







# Discussion post hours calculation
#if not setdiscussion:
#    if postformat == "Text":
#        posthours = (postlength_text * postsperweek) / 250.0
#    else:  # Audio/Video - use same formulas as R for different outputs later
#        # For the total workload R used: 0.18*(len*posts) + ((len*posts)/6)
#        posthours_for_total = 0.18 * (postlength_av * postsperweek) + ((postlength_av * postsperweek) / 6.0)
#        # For out-of-class and engaged calculations R used (len*posts)/3
#        posthours_for_other = (postlength_av * postsperweek) / 3.0
#        # Choose which to use in each context below
#        posthours = posthours_for_total
#else:
#    posthours = float(overridediscussion) if overridediscussion is not None else 0.0
#    posthours_for_other = posthours

# Ensure posthours_for_other exists for later use
if 'posthours_for_other' not in locals():
    if postformat == "Text":
        posthours_for_other = (postlength_text * postsperweek) / 250.0
    else:
        posthours_for_other = (postlength_av * postsperweek) / 3.0


# Other assignments inclusion
if not other_engage:
    other_total_hours = otherassign * otherhours
else:
    other_total_hours = 0.0

# Calculations (mirroring the R app)
total_hours_per_week = round(
    (weeklypages / max(pph, 1e-6)) +
    ((hpw * semesterpages) / classweeks) +
    ((quizzes * quizhours) / classweeks) +
    ((exams * examhours) / classweeks) +
    ((otherassign * otherhours) / classweeks) +
    (posthours) +
    (weeklyvideos) +
    ((syncsessions * synclength))
, 2)

sync_hours_per_week = round(
    ((syncsessions * synclength))
, 2)


# input_hours_per_week = round(
 #   (weeklypages / max(pph, 1e-6)) +
 #   ((hpw * semesterpages) / classweeks) +
 #   ((quizzes * quizhours) / classweeks) +
 #   ((exams * examhours) / classweeks) +
 #   (weeklyvideos) +
 #   (other_total_hours / classweeks) +
 #   ((takehome_min / 60.0) * exams / classweeks)
#, 2)

# output_hours_per_week = round(
 #   (weeklypages / max(pph, 1e-6)) +
 #   ((hpw * semesterpages) / classweeks) +
 #   ((quizzes * quizhours) / classweeks) +
 #   ((exams * examhours) / classweeks) +
 #   (weeklyvideos) +
 #   (other_total_hours / classweeks) +
 #   ((takehome_min / 60.0) * exams / classweeks)
#, 2)




# Display results in the right-hand column area
with col4:
    st.markdown(f"**Total:** {total_hours_per_week} hrs/wk")
    st.markdown(f"**Synchronous:** {sync_hours_per_week} hrs/wk")
#    st.markdown(f"**Input (reading, viewing):** {input_hours_per_week} hrs/wk")
#    st.markdown(f"**Processing and Output:** {output_hours_per_week} hrs/wk")


# Additional small outputs
st.markdown("---")


