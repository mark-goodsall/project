**BIBLE READING APP**

#### Video Demo:  <URL HERE>

DESCRIPTION
This web application is a Bible-reading tool designed to help readers engage with the Bible through bite-size, manageable daily readings. Many earnest believers (myself included) begin a reading plan to complete the Bible but can struggle to stay on track due to the demands of daily life.

This app aims to offer support for maintaining this discipline by providing flexible and structured reading plans.

The app caters to both casual and serious Bible readers:
Casual readers don't need to register. The main page will show the scriptures for that day only.

Registered users can track their progress and be able to catch up if they fall behind.

KEY FEATURES
Flexible reading plans: 
Upon registration the user is asigned the the M'Cheyne one year Bible reading plan. Later updates to include other reading plans and translations (ESV and NKJV).

Daily progress tracking: 
Each day, users are presented with designated chapters to read, which are tracked with the app. Only when a full chapter read has been scrolled through and the user has clicked to confirm completion are the next day's chapters going to be available. 

Catch-up and grace periods: 
Users are given a grace period of 2 months to catch up on any missed readings through the course of the year. If a reading remains incomplete for over 62 days, the user's reading plan is reset, the user's reading plan is reset, providing a fresh start whilst keeping them accountable. Previous subsequent readings become available, provided that the chapter is tracked, and the completion form is confirmed.

Completion tracking and achievements: 
Upon successful completion of a reading plan, users receive a badge, and a record is saved on their profile of the date, reading plan and version to celebrate the achievement.

TECHNICAL OVERVIEW
This app is built with the knowledge and techniques taught in Harvard University's CS50x 2024 course.

Technologies used:
Flask (Python): 
Serves as the backend framework, providing the application's core functionality and managing user sessions.

HTML/CSS: 
Bootstrap is used to make the interface responsive and clean, while layout.html serves as the main page layout.

SQLite: 
SQLite is the database used to store user information, track progress, and record completed readings.

File structure and core components:
app.py: This is the main backend file that controls user routes and session management.

ROUTES
/: Directs users to the homepage (dashboard.html), where logged-in users can view the current day's scripture reading, progress, and access other sections like settings and achievements.

/history: Displays the user's reading history and achievements (history.html). Shows completed readings, with associated completion dates and scripture references.

/login: Allows users to log in using their credentials (login.html). On successful login, users are redirected to the homepage.

/logout: Logs users out and redirects them to the login page.

/progress: Updates the user's daily reading progress (progress.html). Marks scripture readings as complete and updates the progress accordingly.

/nextreadings: Displays the upcoming readings based on the user's start date, reading plan, and current progress.

/reading1, /reading2, /reading3, /reading4: Each route displays the scripture reading for the respective chapter of the day (reading1.html, reading2.html, reading3.html, reading4.html).

/register: Registers a new user (register.html). Users input their username, password, and start date, and upon successful registration, they are redirected to the login page.

/settings: Allows users to set or modify their reading plan preferences (settings.html). Users can update their plan type, translation, and start date for their Bible reading plan.

/dashboard: Displays a specific scripture (e.g., John 1) and other relevant information, such as Bible translation and version settings.

DATABASE STRUCTURE
users: Stores user credentials (email and password), selected Bible version, and start date. Each user has a default reading plan (M'Cheyne).

McheynePlan: Stores the reference reading plan with daily chapters for users to follow.

ReadingProgress: Tracks each user's reading progress, including their start date, days completed, completion status, and calculated completion date.

UI FLOW
Registration/Login: 
New users create an account while returning users log in.

Homepage Display: 
Once logged in, users see the current day’s readings. 

If previous readings have not been completed, the app will display the previous day’s readings until the user marks them as complete.

Once the user marks a previous day’s reading as complete, the next day's scriptures become available to read.

This ensures that users read the plan in sequence and don’t skip ahead without completing prior days.

Daily Tracking: 
Users scroll through the reading and mark it as complete. The app logs the completion, updates the progress, and calculates the completion date based on the user’s start date and days completed.

Achievements: Users can check their progress in the "Achievements" section to see milestones and progress reports.

Reading History: Users can review their previous readings and keep track of their progress over time.

Accountability Reset: 
If a reading is left incomplete beyond 62 days, the user’s progress resets, encouraging discipline while providing flexibility.

FUTURE ENHANCEMENTS
Additional Translations and Language Options: 
Expand the app to support a greater variety of translations and languages.

Customisable Reading Plans: 
Allow users to create their reading plans based on specific books or themes.

Adjustable Grace Period Before Reset: 
Enable users to set a custom grace period in the settings, allowing them to decide how many days they can fall behind before their progress resets. 

