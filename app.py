import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Course Planning Tool", layout="wide")

# Helper: map labels to indices (0-based) (I don't remember what this does)
def idx(label, labels_list):
    try:
        return labels_list.index(label)
    except ValueError:
        return 0

hoursperwriting = np.array([
    [  # Double-spaced (250 Words)
        [0.75, 1.5, 3.0],   # No Drafting for Reflection, Argument, Research
        [1.0, 2.0, 4.0],   # Minimal Drafting for Reflection, Argument, Research
        [1.25, 2.5, 5.0]     # Extensive Drafting for Reflection, Argument, Research
    ],
    [  # Single-spaced (500 Words)
        [1.5, 3.0, 6.0],    # No Drafting for Reflection, Argument, Research
        [2.0, 4.0, 8.0],    # Minimal Drafting for Reflection, Argument, Research
        [2.5, 5.0, 10.0]    # Extensive Drafting for Reflection, Argument, Research
    ]
    ])  # shape (2,3,3)


#outermost list - first dimension - page density (double spaced or single)
#middle list (rows) - genre (reflection, argument, research) 
#inner list (columns) - drafting intensity (none, minimal, extensive) 

st.title("Course Workload Estimator")

#Top block of text 
st.markdown("""
<div style="
    display: flex; 
    gap: 20px; 
    border: 1px solid #cfcfcf; 
    padding: 20px; 
    border-radius: 10px; 
    background-color: #f9f9f9;
    align-items: start;
">

<div style="flex: 3; text-align: left; line-height: 1.6;">
        <strong style="font-size: 16px;">Instructions</strong><br>
        <ol><li>Select your course length.</li>
        <li>Enter the variables for your course design.</li>
        <li>Adjust your course plan to hit key targets.</li>     </ol>
        <strong style="font-size: 16px;">Inputs needed</strong><br>
        <ul>
        <li>Course length</li>
        <li>Modality; if synchronous, estimated time use</li>
        <li>Estimated reading count (words)</li> 
        <li>Number of quizzes, discussion boards, exams, and/or written assignments</li>
                </ul>        
    </div>  
    <div style="flex: 3;  margin: 0 10px;">
    <strong style="font-size: 16px;">Reading inputs based on word count</strong>
    <ul>
    <li>Basic (survey/review)  - 300 words per minute</li>
    <li>Moderate (average readability; some new concepts) - 200 wpm</li>
    <li>Challenging (dense or archaic; many new concepts) - 100 wpm </li>
    </ul>
    <strong style="font-size: 16px;">Writing outputs</strong> 
    <ul>
    <li>Raw</li>
    <li>Minimal drafting</li>
    <li>Mandatory revise/resubmit - 2x multiplier</li>
    </ul>
    <br>
</div>
    <div style="flex: 3; text-align: left; line-height: 1.6;">
   A 3-credit hour course should contain 45-48 contact hours of instruction, depending on the format of the final exam(s). Students are expected to complete a significant amount of non-contact hour time for out-of-class student learning and reflection - <a href="https://www.ecfr.gov/current/title-34/part-600/section-600.2#p-600.2(Credit%20hour)">at a minimum, two additional hours of out-of-class student work.</a> <br><br> Time estimates are split based on input, analysis, output, and administrivia. Classes should be generally balanced with appropriate variation due to major assignments. <br><br> Use of Respondus LockDown Browser + Monitor adds a small amount of time to the "administrivia" category. Major assignments should use proper proctoring. Consider RSI strategies throughout. \n \nThis time estimator focuses on the student workload, not instructor presence or workload.
    </div>
</div>
""", unsafe_allow_html=True)

    
# --- CLASS MEETINGS section ---

st.subheader("Instructional Materials")

#st.header("Course Basics") # not sure where this is
col01, col02, col03 = st.columns([2,3,3], border=True)

with col01:
    st.subheader("Course Length and Modality")    # --- Dropdown for course length/modality ---

    length_option = st.selectbox(
        "Select Course Length and Modality:",
        [
            "8 Week Asynchronous",
            "16 Week Asynchronous",
            "4 Week Asynchronous",
            "7 Week Synchronous (Weekend College)"
        ]
    )

    # --- Automatically assign weeks ---
    if "8 Week" in length_option:
        classweeks = 8
    elif "16 Week" in length_option:
        classweeks = 16
    elif "4 Week" in length_option:
        classweeks = 4
    elif "7 Week" in length_option:
        classweeks = 7
    else:
        classweeks = None

    st.write(f"**Course Length:** {classweeks} weeks")
    
  # --- Option A: SHOW ONLY IF "7 Week" is NOT selected ---
    if "7 Week" not in length_option:
        st.info("For classes with a synchronous element, the instructional balance can be adjusted between pure lecture (input) and activity (study/output) time.")
       
        
    # --- Show slider only for 7-week synchronous option ---
    instruction_pct = None
    activity_pct = None
    if "7 Week" in length_option:
        st.markdown("### Instructional Mix - Synchronous")
        instruction_pct = st.slider(
            "Balance between Student Interaction and Lecture:",
            0, 100, 50, step=10,
            help="100% = entirely lecture, 0% = entirely student interaction/discussion."
        )
        
        activity_pct = 100 - instruction_pct
        st.write(f"**Activity vs. Lecture:** {activity_pct}% activity / {instruction_pct}% lecture")

        # --- Calculate hours ---
        instruction_hours = 3 * instruction_pct / 100
        activity_hours = 3 * activity_pct / 100

        st.write(f"**Lecture/Instruction:** {instruction_hours:.1f} hr/week")
        st.write(f"**Activity/Discussion:** {activity_hours:.1f} hr/week")
    else: 
        instruction_hours = 0
        activity_hours = 0

    
 
with col02: 
    st.subheader("Inputs - Reading")
    st.write("Assumes consistent type of reading. OpenStax Sociology and Psychology typically 12,000-15,000 words per chapter.")
    weeklywords = st.number_input(
        "Words Per Week:",
        value=12000,
        min_value=0,
        step=500
    )

    difficulty_labels = ["Basic", "Moderate", "Challenging"]
    difficulty = st.selectbox("Reading Difficulty:", difficulty_labels, index=1)

    setreadingrate = st.checkbox("Manually adjust reading rate", value=False)

    # Default WPM lookup
    wpm_lookup = {
        "Basic": 300,
        "Moderate": 200,
        "Challenging": 100
    }

    if not setreadingrate:
        wpm = wpm_lookup[difficulty]
    else:
        wpm = st.number_input(
            "Words Per Minute:",
            value=float(wpm_lookup[difficulty]),
            min_value=50.0,
            step=25.0
        )

    # Compute reading time
    if weeklywords > 0 and wpm > 0:
        readminutes = weeklywords / wpm
        readhours = readminutes / 60
        
        st.write(
            f"Estimated reading time: **{readhours:.2f} hours per week** "
            f"at **{int(wpm)} words per minute**"
        )
    else: 
        readhours = 0
    
    st.subheader("Inputs - Video/Podcasts")
    weeklyvideos = st.number_input("Hours Per Week (videos/podcasts):", value=0.0, min_value=0.0, step=0.5)


with col03:
    

    st.subheader("Input Estimator")      
    semesterreading = readhours * classweeks
    semesterviewing = weeklyvideos * classweeks

    st.write(
        f"Estimated **semester** reading time: **{semesterreading:.2f} hours per semester**"             
    )

    st.write(
        f"Estimated **semester** viewing/listening time: **{semesterviewing:.2f} hours per semester**             "
    )


    st.write("Study/review multiplier? Add additional study/review time. \n **Exams/assessments also calculate study/review time.** If using, explain why.")    

    padding = st.number_input("Multiplier", value=1.0, min_value=1.0, step=0.1)      
    paddedinput = (semesterreading + semesterviewing) * padding

    st.write(
        f"Padded viewing/listening time: **{paddedinput:.2f} hours per semester**             "
    )
    
st.header("Activities") 
col01, col02, col03, col04 = st.columns(4, border=True)

with col01:
    st.subheader("Quizzes/formative assessments")
    st.write("Quizzes assume no additional study time beyond other assigned reading.")
    quiznum = st.number_input("Quizzes Per **Semester:**", value=0, min_value=0, step=1)    
    quizmins = st.number_input("Time Estimate Per Quiz(Minutes):", value=20, min_value=0, step=5)
    st.write("If permitting retakes, round up your estimate accordingly.")

    quizweek = ((quizmins/60)*quiznum)/classweeks  # convert to hours for the workload calculation
    quizhours = (quizmins * quiznum)/60
    
    st.write(
    f"Estimated weekly time: **{quizweek:.2f} hours per week**")


with col02:
    st.subheader("Discussions")
    st.markdown("Discussion posts assume 1 hour for a 250 word post or per 2 minutes of video.")

    st.markdown("Replies assume reading/viewing other posts/videos, then writing at 250 words per hour. Video viewing time calculated at face value; text post estimate uses fast/shallow reading speed")
       
    # --- DISCUSSION POSTS (robust, commented) ---
    # Total posts 
    videoposts = st.number_input("Video Posts (per semester):", value=0, min_value=0, step=1)
    videopostlength = st.number_input("Avg. Video Post Length (minutes):", value=3, min_value=0)
    textposts = st.number_input("Text Posts (per semester):", value=1, min_value=0, step=1)
    textpostlength = st.number_input("Avg. Text Post Length (words):", value=350, min_value=0) 
    repliesperpost = st.number_input("Replies per Post:", value=3, min_value=0, step=1)
    replylength = st.number_input("Avg. Reply Length (words):", value=100, min_value=0, step=5)

    # --- CALCULATION: HOURS PER POST -----------------------------------------
    textposthours = textpostlength / 250.0       # Text post hours per post (words → hours at ~250 words/hour)
    videoposthours = videopostlength / 2    # time per video (2 minute = 1hr) 
    tposthours = textposthours * textposts   # multiply by number of posts 
    vposthours = videoposthours * videoposts  # multiply by number of posts 
        
    if repliesperpost > 0:    
        treplyhours = ((textpostlength)/500) + ((repliesperpost * replylength)/250)
        vreplyhours = ((videopostlength)/60) + ((repliesperpost * replylength)/250)        
    else:        
        treplyhours = 0
        vreplyhours = 0
            
    if textposts > 0:      
        timeperposttext =  textposthours + treplyhours
    else:        
        timeperposttext =  0

    if videoposts > 0:    
        timeperpostvideo =   videoposthours +  vreplyhours    
    else:            
        timeperpostvideo = 0


    totalvreplyhours =  vreplyhours * videoposts   
    totaltreplyhours = treplyhours * textposts

    totaltpr = timeperposttext * textposts
    totalvpr = timeperpostvideo * videoposts

    totaldposthours = totalvpr + totaltpr
        
    st.write(f"Estimated time per written post & replies:{timeperposttext:.2f} hours")   
    st.write(f"Estimated time per video post & replies:{timeperpostvideo:.2f} hours")  
               
    #discussionoutput - 50/50 for posts/videos ; replies are 50/25/25

    # Unpack the ratios directly (50%, 25%, 25%)
    vreply_in, vreply_st, vreply_out = totalvreplyhours * 0.5, totalvreplyhours * 0.25, totalvreplyhours * 0.25
    treply_in, treply_st, treply_out = totaltreplyhours * 0.5, totaltreplyhours * 0.25, totaltreplyhours * 0.25

    # Unpack the ratios for study/output (50%, 50%)
    v_st, v_out = vposthours * 0.5, vposthours * 0.5
    t_st, t_out = tposthours * 0.5, tposthours * 0.5

    # Final Sums (Clearer grouping)
    discussioninput  = vreply_in + treply_in + v_st + t_st
    discussionstudy  = vreply_st + treply_st 
    discussionoutput = vreply_out + treply_out + v_out + t_out

with col03:   
    st.subheader("Learning Commons")
    st.info("Workshops; required scholarly sources for activities; others?")
       
with col04:       
    st.subheader("Other Activities")
    st.markdown("Catch-all for other activities such as proctored short answers; adds listed time to both study and output ")
    other_count = st.number_input("# Per Semester:", value=0, min_value=0, step=1, key="other_count")
    other_minutes = st.number_input("Time Estimate Per Activity (Minutes):", value=20, min_value=0, step=5)
    
    # 2. Handle Proctored Overhead
    proctored_check_other = st.checkbox("Proctored Activity - Add 10 minutes for VDI/Respondus", value=False)
    other_overhead = 10 if proctored_check_other else 0
    
    other_total_semester_hours = ((other_minutes+other_overhead) / 60) * other_count
    other_weekly_hours = other_total_semester_hours / classweeks
    
    
    # 4. Display Results
    st.write(f"Estimated weekly time: **{other_weekly_hours:.2f} hours per week**")
    st.write(f"Estimated **semester** time: **{other_total_semester_hours:.2f} hours per semester**")

    # 5. Categorization (to be used in your final summary)
    # We add the 'overhead' strictly to output, and split the rest between study and output
    
    other_output = (other_count * other_minutes)/60
    other_study =  (other_count * other_minutes)/60
    other_administrivia = (other_overhead * other_count)/60

    st.info("what other activities (like problem sets) fit here?")


st.header("Assessments")
col01, col02, col03, = st.columns(3, border=True)

with col01:   
    st.subheader("Exams")
    st.write("Exams are calculated as follows: ")   
    
    examnumb = st.number_input("Exams Per Semester:", value=0, min_value=0, step=1) # Number of exams
    
    if examnumb > 0:      
        exam_length = st.number_input("Exam Time (Minutes):", value=60, min_value=0, step=5)    # Exam time in minutes
        exam_length_hrs = exam_length/60
    
        exam_study = st.slider(
            "Expected study per exam hour",
            1, 10, 5, step=1,  
            help="1 = 1 additional hour of study expected per hour of exam time"
        )
       
          # Proctored checkbox adds 10 minutes to the exam
        examproctored = st.checkbox("Proctored Exam - Add 10 minutes for VDI/Respondus", value=True)
        
        examadministriviatotal = ((10 if examproctored else 0)/60)*examnumb
                
        examstudytotal = (exam_study * examnumb)    # Convert total exam study minutes to hours
        examoutputtotal = (exam_length_hrs * examnumb)  # Convert total exam time 

        examtotal = (exam_study * exam_length_hrs) + exam_length_hrs + ((10 if examproctored else 0)/60)

        st.write(f"Estimated time per exam: **{examtotal:.2f} hours per exam**")
              
    else: 
        st.write("no exams planned; review for sufficient Respondus use on medium-stakes activities")
        examstudytotal = 0
        examoutputtotal = 0
        examadministriviatotal = 0

with col02:   
    st.subheader("Writing Assignments")
    st.markdown("This section estimates the time students spend writing assignments each week, based on page count, genre, and drafting requirements. ")
    semesterpages = st.number_input("Pages Per Semester:", value=0, min_value=0)
    writtendensity_labels = ["250 Words (Double-Spaced)", "500 Words (Single-Spaced)"]
    writtendensity = st.selectbox("Page Density:", writtendensity_labels, index=0)
    writingpurpose_labels = ["Reflection/Narrative", "Argument", "Research"]
    writingpurpose = st.selectbox("Genre:", writingpurpose_labels, index=0)
    draftrevise_labels = ["No Drafting", "Minimal Drafting", "Extensive Drafting"]
    draftrevise = st.selectbox("Drafting:", draftrevise_labels, index=0)
      
    calculated_hpw = hoursperwriting[
    idx(writtendensity, writtendensity_labels),
    idx(draftrevise, draftrevise_labels),
    idx(writingpurpose, writingpurpose_labels)
    ]

    st.markdown(f"**Estimated Writing Rate Per Page:** {calculated_hpw} hours per page")
    st.info("Review writing rates above for genre and drafting expectations. If desired, manually adjust the rate after initial estimate. Study/output ratios set by genre/purpose.")

    setwritingrate = st.checkbox("manually alter writing rate (add time only)", value=False)
    overridehoursperwriting = None
    if setwritingrate:
        overridehoursperwriting = st.number_input("Hours Per Written Page:", value=0.5, min_value=0.0, step=0.01)
        
    # Determine hours per writing page
    if not setwritingrate:
        hpw = calculated_hpw
    else:
        hpw = calculated_hpw + (float(overridehoursperwriting) if overridehoursperwriting is not None else 0.0)

    st.markdown(f"**Adjusted Writing Rate:** {hpw} hours per page")
    
    totalwriting = semesterpages * hpw 
    
    st.markdown(f"**Semester Estimate** {totalwriting} hours total")



with col03:   
    st.subheader("Incidentals")
    st.markdown("Announcements, grading comments, other instructor inputs")
    st.info("Incidentals adding to input time; what else would go here? ")

st.markdown("---")

st.subheader("Workload Estimates")  # GRAND CALCULATION AT THE END WITH CSV OUTPUT 
# ensure all variables are defined - commented out if fully defined earlier 

    #Synchronous Workload    
if "7 Week" in length_option: 
    syncin = instruction_hours * 7
    syncstudy = activity_hours * 3.5
    syncout =  activity_hours * 3.5
else: 
    syncin = 0
    syncstudy = 0 
    syncout = 0

    #Reading Workload
    #Viewing / Listening Workload
#semesterreading
#semesterviewing
semesterreadingstudy = (semesterreading * padding) - semesterreading
semesterviewingstudy = (semesterviewing * padding) - semesterviewing
#padding

    #Quizzes Workload
#quizhours (semester) - output

    #Discussions Workload
#discussioninput
#discussionstudy
#discussionoutput
discussionadministrivia = 0

#Library Tools Workload

    #Other Activities Workload 
#other_output
#other_study
#other_administrivia


    #Exams Workload
#examstudytotal
#examoutputtotal
#examadministriviatotal

#Writing Assignments Workload 

# 2. YOUR NEW DICTIONARY (TOTALLY SEPARATE)
# This lives in its own variable and won't interfere with the array
writing_purpose_ratios = {
    "Reflection/Narrative": (1/3, 2/3),
    "Argument": (1/2, 1/2),
    "Research": (2/3, 1/3)
}
writing_study_ratio, writing_output_ratio = writing_purpose_ratios[writingpurpose]

writingstudy =  totalwriting * writing_study_ratio
writingoutput = totalwriting * writing_output_ratio


#Incidentals Workload 
incidentalinput = 0
incidentalstudy = 0
incidentaloutput = 0
incidentaladministrivia = 0


workload = {
    "Synchronous": {
        "Input": syncin,
        "Study": syncstudy,
        "Output": syncout,
        "Administrivia": 0,
    },
    "Reading": {
        "Input": semesterreading,
        "Study": semesterreadingstudy,
        "Output": 0,
        "Administrivia": 0
    },
    "Viewing / Listening": {
        "Input": semesterviewing,
        "Study": semesterviewingstudy,
        "Output": 0,
        "Administrivia": 0
    },
    "Quizzes": {
        "Input": 0,
        "Study": 0,
        "Output": quizhours,
        "Administrivia": 0
    },
    "Discussions": {
        "Input": discussioninput,
        "Study": discussionstudy,
        "Output": discussionoutput,
        "Administrivia": discussionadministrivia,
    },
    "Learning Commons INCOMPLETE": {
        "Input": 0,
        "Study": 0,
        "Output": 0,
        "Administrivia": 0,
    },  
    "Other Activities": {
        "Input": 0,
        "Study": other_study,
        "Output": other_output,
        "Administrivia": other_administrivia,
    },
    "Exams": {
        "Input": 0,
        "Study": examstudytotal,
        "Output": examoutputtotal,
        "Administrivia": examadministriviatotal,
    },    
    "Writing Assignments": {
        "Input": 0,
        "Study": writingstudy,
        "Output": writingoutput,
        "Administrivia": 0,
    },
    "Incidentals": {
        "Input": incidentalinput,
        "Study": incidentalstudy,
        "Output": incidentaloutput,
        "Administrivia": incidentaladministrivia,
    },
}

def style_totals(row):
    # Colors for the cells
    total_style = 'background-color: #f9f9ca; font-weight: bold;'
    default_style = ''
    
    styles = []
    for col in row.index:
        # Check if the row is "TOTAL" OR if the specific column is "TOTAL"
        if row.name == "TOTAL" or col == "TOTAL":
            styles.append(total_style)
        else:
            styles.append(default_style)
    return styles

df = pd.DataFrame.from_dict(workload, orient="index")
df = df[["Input", "Study", "Output", "Administrivia"]]
df["TOTAL"] = df.sum(axis=1)
df.loc["TOTAL"] = df.sum(axis=0)
st.dataframe(
    df.style.format("{:.2f}").apply(style_totals, axis=1), 
    use_container_width=True, 
    height=int(35.2 * (len(df) + 1)) # This math helps it fit exactly to the row count
)

csv = df.round(2).to_csv()

st.download_button(
    label="🚀 Download workload table (CSV)",
    data=csv,
    file_name="workload_summary.csv",
    mime="text/csv"
)


# Additional small outputs
st.markdown("---")

st.markdown("""
<div style="
    display: flex; 
    gap: 20px; 
    border: 1px solid #cfcfcf; 
    padding: 20px; 
    border-radius: 10px; 
    background-color: #f9f9f9;
    align-items: start;
">
    <div style="flex: 3; text-align: left; font-size: 14px; line-height: 1.6;">
     Additional definitions/clarifications:
     <ul>
     <li>     Formative assessments are assumed to be non-proctored; open book, open notes. </li>
     <li> other notes? </li> 
     </ul>
    </div>    
    <div style="flex: 3; text-align: left; font-size: 14px; line-height: 1.6;">
    Additional calculation notes: 
    <ul>
     <li>Study/output calculations for writing assignments calculate 1/3 study, 2/3 output for reflective writing; 1/2 study, 1/2 output for argumentative writing; and 2/3 study, 1/3 output for research. </li>      
     <li>Discussion posts seem inflated compared to typical student work? Difficult to assess due to lack of proctoring tools.</li> 
     </ul>    
    </div>
    <div style="flex: 3; text-align: left; font-size: 14px; line-height: 1.6;">
        Course Workload Estimator - <a href="http://linktr.ee/mbkenfield" target="_blank">revised by Mel Kenfield</a> for TCC-Connect<br>
        Based on <a href="https://cat.wfu.edu/resources/workload2/" target="_blank">Workload Estimator 2.0</a><br>
        Research by <a href="https://cat.wfu.edu/about/our-team/" target="_blank">Betsy Barre</a>, <a href="https://orcid.org/0000-0002-7241-2288" target="_blank">Allen Brown</a>, and <a href="https://www.justinesarey.com/" target="_blank">Justin Esarey</a><br><br>
        <a href="https://cat.wfu.edu/resources/workload/estimationdetails/" target="_blank">Details from Wake Forest University</a><br>    
        <a href="https://cte.rice.edu/resources/workload-estimator" target="_blank">Additional information available from Rice University</a><br><br>
        <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank">
            <img src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" alt="CC BY-NC-SA 4.0" style="width: 88px;">
        </a><br>
        <span style="font-size: 12px;">Licensed under CC BY-NC-SA 4.0.</span>
    </div>
</div>
""", unsafe_allow_html=True)


