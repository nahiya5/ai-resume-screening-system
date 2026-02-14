**AI-Based Resume Screening and Job Recommendation System**


**Overview**

This project automates resume screening using Python, NLP, and SQL.
It extracts key skills from resumes and compares them with job descriptions stored in a database.



 **The system calculates :**
1. Match Percentage

2. Matched Skills

3. Missing Skills (Skill Gap Analysis)

This helps recruiters screen candidates faster and helps job seekers understand how well they fit a role.



**Features**

1. Resume processing (PDF supported)

2. NLP-based skill extraction

3. SQL database for job storage

4. Match percentage calculation

5. Skill gap identification

6.  resume comparison for  job description

   

***Tech Stack**

1.Python

2.SQLite

3.NLP-based text processing

4.Git & GitHub


 **Project Structure**
  
ai-resume-screening-system/                                                                                                                                                                                          
|                                                                                                                                                                                                                    
│                                                                                                                                                                                                                    
├── resumes.py                                                                                                                                                                                                       
|                                                                                                                                                                                                                    
├── resume_mentor.db (auto-generated locally)                                                                                                                                                                        
|                                                                                                                                                                                                                    
├── requirements.txt                                                                                                                                                                                                 
|                                                                                                                                                                                                                    
└── README.md                                                                                                                                                                                                        


**How to Run**

Install dependencies:

pip install -r requirements.txt


 **Run the script:**

python resumes.py

**Example Job Description Used**

We are hiring a Python Developer.
Required skills: Python, SQL, Django, Git, Linux.
Preferred: AWS, REST API.
