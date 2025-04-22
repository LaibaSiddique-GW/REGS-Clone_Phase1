# Phase I Report

## Entity-Relation Diagram

![ER Diagram](static/images/Updated_ER_Diagram_Phase1_Final_Project.png)
![SQL Schema Diagram](static/images/Updated_SQL_Schema_Diagram_Phase1_Final_Project.png)

## Normal Form

BCNF (or at least 3NF). All tables have atamic values and columns, no value in the tables is dependent on just part of the key, no non-prime value can be determined by another non-prime value in the same table, and if you want to get the values of the primary key without using the primary key, then you either cannot do so or must use all the non-prime values of the table combined (depending on the table.). (For example, you can only get course title and credit hours using the course number and department, and title and/or credits cannot tell you the course number and department, so the course table is in BCNF. However, for the course section table, the course registration number (CRN) gives you the section number, course number, course department, semester, and year (and the course number and department can join with the course table to give table an credit hours), and **all** these values from the course section table *combined*, excluding the CRN, can give you the CRN, and no non-prime value can tell the another non-value, which makes the course section table at least 3NF, and possibly BCNF.)

## Design Justification

- The design was justified using the registration project requirements document and database phase 1 demo requirements document that were given to us, basic intuition about how some things may work, and by how things work in real life. 
<!-- I dont actually unserstand what this section is asking. -->

## Testing


- Each person tests their code individually before sending the pull request, and others review the code for any bugs. Any merging the request, the code is run from main and if any bugs arise, then a new branch is created to fix the bugs and then is merged back into main. All people test the code from their end after pulling. 
- The code is tested in parts and then as a whole. 


## Assumptions Made By Our Group


- Username format is `UserID@user_type.edu`. 
- A user is either an administrator, instructor, graduate secretary, or graduate student and cannot be more than 1 type. (**At least for now. May change later**.). 
- Each user can belong to only 1 department. A department can have 0 or more users. 
- A course is unique in its department and number. A course section can be determined by the course department, number, section number, semester and year, OR it can be determined more easily using the course registration number (CRN). A course can have more then 1 section. Courses may not be offered yet or anymore, so they are not required to always have a section. However, each section required a course. A course section may be taught by more than 1 professor (i.e. co-teaching is allowed), and a proffesor can teach more than 1 section and more than 1 course. 
- **We assumed Graduate Secretary was/is a Graduate Teaching Assistant. We did not know it was not until the Phase 1 Presentation. We are in the process of fixing this, so some code here in the most recent commit(s) may not reflect this anymore, but at the time of the Phase 1 presentation, this was the case.** 
- Graduate secretaries can teach more than 1 course and more than 1 section. They are often assigned to specifially assist 1 specific instructor in that instructor's sections and courses. Instructors can teach more than 1 course and more than 1 section. More than 1 graduate secretary may be assigned to a course section. Both grad secretaries and instructors "teach". 
- Graduate secretaries do not have their own offices, while instructors and administrators do. 
- Graduate year depends on admit year (masters grad year = 2 + admit year; PhD and doctoral grad years = 2 + admit year).
- Graduate Secretaries and instructors can only change (and see) the grades of the students they are teaching for the specific course(s) they are teaching student. (For example, the professor and secretary for MATH 6210 can only grade students in (i.e. taking) MATH 6210 with that professor and secretary and only change their grade for MATH 6210, and grade no other students and not other courses of those students (unless that student is taking another class with them in which case the same rules apply).)
- Students can see only their own grades and transcripts.
- Each building has X floors associated with it. When a new floor is added, a new floor has been built or opened up, and when deleted, it is broken down/removed or shut down.
- You can can use first digit of the room number to determine the floor number. 
- Assume 2 class sections with the same professor and the same time, but different rooms is because the room is large and has dividers that have been raised up (like the 1300, 1400, 1450 room in SEH), the professor is in person for 1 class, but online or zoom for the other (like SEAS 1001 was), or 1 section is a lab or section being lead by the secretary instead.
- It is possible for 2 courses to have the same title (but different course numbers and/or departments). 
- All departments are located in 1 specific floor of 1 specific building, but not all floors and all buildings need to have their own department. 
- All classrooms (and offices) are located in 1 specific floor of 1 specific building, but not all floors and all buildings need to have classrooms or offices. 
- All instructors and administrators have offices. Many instructors have their office in 1 floor and 1 building, but only 1 office for each instructor. Many administrators have their office in 1 floor and 1 building, but only 1 office for each administrator. 
- Course catalogue displays classes for Fall 2025 semester. Students have have taken (or may still be taking or awaiting the grades of) classes from semesters before Fall 2025.
- Not all instructors need to have ratings. Not all students need to have rated an instructor. An instructor can have more than 1 rating given, and all ratings are averaged together to get the instructor's main average rating. A student can rate multiple professors, but can only rate a professor 1 time. 
- Professors and graduate secretaries can only teach classes within their department. (For example, CSCI professor can only teach CSCI courses.). 
- Users do not have middle names (or even if they do, middle names are not important enough to be stored.). 


<!-- Are there any other asumptions I am missing? I feel like there are.  -->


## Things We Are Missing


- The ability to add new courses to the course catalogue. 
- MySQL ansd AWS for database. We are instead using SQLite for now since we do not have access to AWS accounts. 


## Work Breakdown


- Kate: ER diagram, Course catalogue page, course registration page(s), adding and dropping courses, and code review. 
- Tabitha: Login page, user registration page, transcript page(s), user account page(s), and grade and rating changing, and code reviews. 
- Laiba: ER diagram, SQL Schema diagram, SQL Schema (setting up all tables in SQL), Adding all values to SQL/database, code reviews, additional debugging and error handling round(s) after intial debugging, styling, report writing, and linking all pages together. 


## REGS Starting State Info


- *We already have 2 admins, 9 graduate students, 17 graduate secretaries, and 17 instructors to start with.*
- **We can run the [registration_schema.sql](registration_schema.sql) file to reset the database back to its starting state.**
- Billie Holiday's login is: `88888888@student.edu` for username, and `student7` for password. 
- Diana Krall's login is: `99999999@student.edu` for username and `student8` for password. 
- Professors Choi and Youssef co-teach 1 section of CSCI 6212. Proffesor Choi Co-teaches 1 section of CSCI 6212 with Professor Abdou Youssef and teaches other sections of the class herself. 
- Professor Narahari's username is `00000005@instructor.edu` and password is `prof2`. 
- Professor Choi's username is `00000009@instructor.edu` and password is `prof6`. 
- The grad secretary for Professor Narahari's classes is: Amaranth Nihari, username `00000022@gradSec.edu` and password `sec2`. 
- The grad secretary for Professor Choi's classes is: Hyah Choo (Prounouced HyACHOO when saying it together), username `00000026@gradSec.edu` and password `sec6`. 
