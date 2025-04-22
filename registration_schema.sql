-- Laiba Siddique
PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  UID                       char(8) not null PRIMARY KEY,
  password                  varchar(50) not null,
  first_name                varchar(50) not null,
  last_name                 varchar(50) not null, 
  address                   varchar(100) not null, 
  user_type                 varchar(50) not null, 
  department                varchar(4) not null,
  FOREIGN KEY (department) REFERENCES department(dep_name)
);

DROP TABLE IF EXISTS building;
CREATE TABLE building (
  b_name                    varchar(50) not null, 
  PRIMARY KEY (b_name)
);

-- Each building has X floors associated with it. 
-- Assume when a new floor is added, a new floor has been built or opened up, and when deleted, it is broken down/removed or shut down. 
-- Use count on the times a building is associated with floors or the Max floor num associated with a building to find number of floors. 
DROP TABLE IF EXISTS floors_available; -- used to determined the floors available in a building. 
CREATE TABLE floors_available (
  b_name                    varchar(50) not null, 
  floor_num                 int(2) not null, -- tells the floor number
  CHECK (floor_num > 0),
  PRIMARY KEY (b_name, floor_num)
);

DROP TABLE IF EXISTS department;
CREATE TABLE department (
  dep_name                  varchar(4) not null PRIMARY KEY,
  building                  varchar(50) not null, 
  floor                     int(2) not null, -- should be less than or equal to the number of floors in the building. Similar to capcity determines max-register.
  FOREIGN KEY (building) REFERENCES building(b_name)
  FOREIGN KEY (building, floor) REFERENCES floors_available(b_name, floor_num)
);

DROP TABLE IF EXISTS classroom;
CREATE TABLE classroom (
  building                  varchar(50) not null, 
  room                      int(4) not null, -- can use first digit to determine floor, so not including floor else 3NF violation.
  capacity                  int(4) not null, 
  PRIMARY KEY (building, room), 
  FOREIGN KEY (building) REFERENCES building(b_name)
);

DROP TABLE IF EXISTS time_slot;
CREATE TABLE time_slot (
  TSID                      int(4) not null PRIMARY KEY, 
  start_time                TIME not null, 
  end_time                  TIME not null, 
  day                       varchar(1) not null
);

DROP TABLE IF EXISTS instructor;
CREATE TABLE instructor (
  IID                       char(8) not null PRIMARY KEY, 
  OH_time                   int(4) not null,
  office_building           varchar(50) not null, 
  office_room               int(4) not null, 
  FOREIGN KEY (IID) REFERENCES users(UID), 
  FOREIGN KEY (OH_time) REFERENCES time_slot(TSID),
  FOREIGN KEY (office_building, office_room) REFERENCES classroom(building, room), 
  FOREIGN KEY (office_building) REFERENCES building(b_name)
);

DROP TABLE IF EXISTS administrator;
CREATE TABLE administrator (
  AID                       char(8) not null PRIMARY KEY, 
  office_building           varchar(50) not null, 
  office_room               int(4) not null, 
  FOREIGN KEY (AID) REFERENCES users(UID), 
  FOREIGN KEY (office_building, office_room) REFERENCES classroom(building, room), 
  FOREIGN KEY (office_building) REFERENCES building(b_name)
);

DROP TABLE IF EXISTS grad_secretary;
CREATE TABLE grad_secretary (
  GID                       char(8) not null PRIMARY KEY, 
  OH_time                   int(4) not null,
  FOREIGN KEY (OH_time) REFERENCES time_slot(TSID),
  FOREIGN KEY (GID) REFERENCES users(UID)
);

DROP TABLE IF EXISTS grad_student;
CREATE TABLE grad_student (
  SID                       char(8) not null PRIMARY KEY, 
  degree_program            varchar(50) not null, 
  grad_year                 int(4) not null, 
  FOREIGN KEY (SID) REFERENCES users(UID)
);

DROP TABLE IF EXISTS course;
CREATE TABLE course (
  dept                      varchar(4) not null, 
  cnum                      int(4) not null, 
  title                     varchar(50) not null, 
  credit_hours              int(2) not null, 
  PRIMARY KEY (dept, cnum), 
  FOREIGN KEY (dept) REFERENCES department(dep_name)
);

DROP TABLE IF EXISTS prerequisites;
CREATE TABLE prerequisites (
-- c: course; p: prereq
  cdept                     char(4) not null, 
  cnum                      int(4) not null, 
  pdept                     char(4) not null, 
  pnum                      int(4) not null, 
  PRIMARY KEY (cdept, cnum, pdept, pnum), 
  FOREIGN KEY (cdept) REFERENCES department(dep_name), 
  FOREIGN KEY (pdept) REFERENCES department(dep_name), 
  FOREIGN KEY (cdept, cnum) REFERENCES course(dept, cnum), 
  FOREIGN KEY (pdept, pnum) REFERENCES course(dept, cnum)
);

DROP TABLE IF EXISTS course_section;
CREATE TABLE course_section (
  CRN                       int(5) not null PRIMARY KEY, 
  dept                      char(4) not null, 
  cnum                      int(4) not null, 
  sec_num                   int(2) not null, 
  semester                  varchar(10) not null, 
  year                      int(4) not null, 
  FOREIGN KEY (dept) REFERENCES department(dep_name), 
  FOREIGN KEY (dept, cnum) REFERENCES course(dept, cnum)
);

DROP TABLE IF EXISTS sec_room;
CREATE TABLE sec_room (
  CRN                       int(5) not null, 
  building                  varchar(50) not null, 
  room                      int(4) not null, -- room and building have tells capacity, which determines max_register for the section. num_reg <= capacity. 
  PRIMARY KEY (CRN, building, room), 
  FOREIGN KEY (CRN) REFERENCES course_section(CRN), 
  FOREIGN KEY (building, room) REFERENCES classroom(building, room), 
  FOREIGN KEY (building) REFERENCES building(b_name)
);

DROP TABLE IF EXISTS sec_time;
CREATE TABLE sec_time (
  CRN                       int(5) not null, 
  TSID                      int(4) not null, 
  PRIMARY KEY (CRN, TSID), 
  FOREIGN KEY (CRN) REFERENCES course_section(CRN), 
  FOREIGN KEY (TSID) REFERENCES time_slot(TSID)
);

-- DROP TABLE IF EXISTS sec_reg; -- How many students are registered for a section. I will keep this here just in case because do not want accidental NF violations. 
-- CREATE TABLE sec_reg (
--   CRN                       int(5) not null, 
--   num_reg                   int(4) not null, -- number of students registered. 
--   PRIMARY KEY (CRN), 
--   FOREIGN KEY (CRN) REFERENCES course_section(CRN)
-- );

DROP TABLE IF EXISTS teaches;
CREATE TABLE teaches (
  UID                       char(8) not null, 
  CRN                       int(5) not null, 
  PRIMARY KEY (UID, CRN), 
  FOREIGN KEY (UID) REFERENCES users(UID), 
--   FOREIGN KEY (IID) REFERENCES instructor(IID), 
-- Both grad secretaries and instructors "teach"
  FOREIGN KEY (CRN) REFERENCES course_section(CRN)
);

DROP TABLE IF EXISTS takes; -- We could count number of SID's per section to find the number of students registered for a section. 
CREATE TABLE takes (
  SID                       char(8) not null, 
  CRN                       int(5) not null, 
  grade                     varchar(2) not null,
  PRIMARY KEY (SID, CRN), 
  FOREIGN KEY (SID) REFERENCES users(UID), 
  FOREIGN KEY (SID) REFERENCES grad_student(SID), 
  FOREIGN KEY (CRN) REFERENCES course_section(CRN)
);

DROP TABLE IF EXISTS ratings; -- Holds all the ratings for professors/secretaries. AVG function and grouping can help find overall avg for each professor/secretary. 
CREATE TABLE ratings (
  UID                       char(8) not null, -- Instructor/secretary. (Make sure in python actally only Instructor/secretary). 
  SID                       char(8) not null, -- Student
  rating                    decimal(2,1) not null, 
  CHECK (rating >= 0), 
  PRIMARY KEY (UID, SID), 
  FOREIGN KEY (UID) REFERENCES users(UID), 
  FOREIGN KEY (SID) REFERENCES users(UID), 
  FOREIGN KEY (SID) REFERENCES grad_student(SID)
);

PRAGMA foreign_keys=on;

-- Add buildings
INSERT INTO building VALUES ('SEH');
INSERT INTO building VALUES ('USC');
INSERT INTO building VALUES ('PHIL');

-- Add floors to buildings
INSERT INTO floors_available VALUES ('SEH', 1);
INSERT INTO floors_available VALUES ('SEH', 2);
INSERT INTO floors_available VALUES ('SEH', 3);
INSERT INTO floors_available VALUES ('SEH', 4);
INSERT INTO floors_available VALUES ('SEH', 5);
INSERT INTO floors_available VALUES ('SEH', 6);
INSERT INTO floors_available VALUES ('SEH', 7);
INSERT INTO floors_available VALUES ('SEH', 8);

INSERT INTO floors_available VALUES ('USC', 1);
INSERT INTO floors_available VALUES ('USC', 2);
INSERT INTO floors_available VALUES ('USC', 3);
INSERT INTO floors_available VALUES ('USC', 4);
INSERT INTO floors_available VALUES ('USC', 5);
INSERT INTO floors_available VALUES ('USC', 6);
INSERT INTO floors_available VALUES ('USC', 7);
INSERT INTO floors_available VALUES ('USC', 8);

INSERT INTO floors_available VALUES ('PHIL', 1);
INSERT INTO floors_available VALUES ('PHIL', 2);
INSERT INTO floors_available VALUES ('PHIL', 3);
INSERT INTO floors_available VALUES ('PHIL', 4);
INSERT INTO floors_available VALUES ('PHIL', 5);
INSERT INTO floors_available VALUES ('PHIL', 6);
INSERT INTO floors_available VALUES ('PHIL', 7);
INSERT INTO floors_available VALUES ('PHIL', 8);

-- Add departments
-- INSERT INTO department VALUES ('CSCI');
-- INSERT INTO department VALUES ('ECE');
-- INSERT INTO department VALUES ('MATH');
-- INSERT INTO department VALUES ('ADMN'); -- ADMN short for administration
INSERT INTO department VALUES ('CSCI', 'SEH', 4);
INSERT INTO department VALUES ('ECE', 'SEH', 5);
INSERT INTO department VALUES ('MATH', 'PHIL', 1);
INSERT INTO department VALUES ('ADMN', 'USC', 1); -- ADMN short for administration

-- SELECT * FROM department;


-- Add Classrooms

INSERT INTO classroom VALUES ('SEH', 1300, 30);
INSERT INTO classroom VALUES ('SEH', 1400, 30);
INSERT INTO classroom VALUES ('SEH', 1450, 30);

INSERT INTO classroom VALUES ('SEH', 4001, 5); -- for testing room capacity max preventing registration
INSERT INTO classroom VALUES ('SEH', 4002, 25);
INSERT INTO classroom VALUES ('SEH', 4003, 20);
INSERT INTO classroom VALUES ('SEH', 4004, 10);
INSERT INTO classroom VALUES ('SEH', 4005, 15);
INSERT INTO classroom VALUES ('SEH', 4006, 25);
INSERT INTO classroom VALUES ('SEH', 4007, 10);
INSERT INTO classroom VALUES ('SEH', 4008, 21);

INSERT INTO classroom VALUES ('SEH', 5001, 25);

INSERT INTO classroom VALUES ('PHIL', 1120, 30);

INSERT INTO classroom VALUES ('SEH', 4101, 4); -- for offices
INSERT INTO classroom VALUES ('SEH', 4102, 4);
INSERT INTO classroom VALUES ('SEH', 4103, 4);
INSERT INTO classroom VALUES ('SEH', 4104, 4);
INSERT INTO classroom VALUES ('SEH', 4105, 4);
INSERT INTO classroom VALUES ('SEH', 4106, 4);
INSERT INTO classroom VALUES ('SEH', 4107, 4);
INSERT INTO classroom VALUES ('SEH', 4108, 4);
INSERT INTO classroom VALUES ('SEH', 4109, 4);
INSERT INTO classroom VALUES ('SEH', 4110, 4);
INSERT INTO classroom VALUES ('SEH', 4111, 4);
INSERT INTO classroom VALUES ('SEH', 4112, 4);
INSERT INTO classroom VALUES ('SEH', 4113, 4);
INSERT INTO classroom VALUES ('SEH', 4114, 4);

INSERT INTO classroom VALUES ('SEH', 5101, 4); 
INSERT INTO classroom VALUES ('SEH', 5102, 4);

INSERT INTO classroom VALUES ('PHIL', 1201, 4); 

INSERT INTO classroom VALUES ('USC', 101, 4); -- for admin offices
INSERT INTO classroom VALUES ('USC', 102, 4);
INSERT INTO classroom VALUES ('USC', 103, 4);
INSERT INTO classroom VALUES ('USC', 104, 4);

-- SELECT * FROM classroom;


-- Add Timeslots

INSERT INTO time_slot VALUES (1, '15:00:00', '17:30:00', 'M'); -- 3:00 to 5:30
INSERT INTO time_slot VALUES (2, '15:00:00', '17:30:00', 'T');
INSERT INTO time_slot VALUES (3, '15:00:00', '17:30:00', 'W');
INSERT INTO time_slot VALUES (4, '15:00:00', '17:30:00', 'R');
INSERT INTO time_slot VALUES (5, '15:00:00', '17:30:00', 'F');

INSERT INTO time_slot VALUES (6, '16:00:00', '18:30:00', 'M'); -- 4:00 to 6:30
INSERT INTO time_slot VALUES (7, '16:00:00', '18:30:00', 'T');
INSERT INTO time_slot VALUES (8, '16:00:00', '18:30:00', 'W');
INSERT INTO time_slot VALUES (9, '16:00:00', '18:30:00', 'R');
INSERT INTO time_slot VALUES (10, '16:00:00', '18:30:00', 'F');

INSERT INTO time_slot VALUES (11, '18:00:00', '20:30:00', 'M'); -- 6:00 to 8:30
INSERT INTO time_slot VALUES (12, '18:00:00', '20:30:00', 'T');
INSERT INTO time_slot VALUES (13, '18:00:00', '20:30:00', 'W');
INSERT INTO time_slot VALUES (14, '18:00:00', '20:30:00', 'R');
INSERT INTO time_slot VALUES (15, '18:00:00', '20:30:00', 'F');

INSERT INTO time_slot VALUES (26, '15:30:00', '18:00:00', 'M'); -- 3:30 to 6:00
INSERT INTO time_slot VALUES (27, '15:30:00', '18:00:00', 'T');
INSERT INTO time_slot VALUES (28, '15:30:00', '18:00:00', 'W');
INSERT INTO time_slot VALUES (29, '15:30:00', '18:00:00', 'R');
INSERT INTO time_slot VALUES (30, '15:30:00', '18:00:00', 'F');

INSERT INTO time_slot VALUES (16, '13:00:00', '14:00:00', 'F'); -- Default instructor office hours. 
INSERT INTO time_slot VALUES (17, '13:00:00', '14:00:00', 'M');
INSERT INTO time_slot VALUES (18, '13:00:00', '14:00:00', 'T');
INSERT INTO time_slot VALUES (19, '13:00:00', '14:00:00', 'W');
INSERT INTO time_slot VALUES (20, '13:00:00', '14:00:00', 'R');

INSERT INTO time_slot VALUES (21, '12:00:00', '13:00:00', 'F'); -- Default secretary office hours. 
INSERT INTO time_slot VALUES (22, '12:00:00', '13:00:00', 'M');
INSERT INTO time_slot VALUES (23, '12:00:00', '13:00:00', 'T');
INSERT INTO time_slot VALUES (24, '12:00:00', '13:00:00', 'W');
INSERT INTO time_slot VALUES (25, '12:00:00', '13:00:00', 'R');

-- SELECT * FROM time_slot;


--  Add users (first admin, then student, instructors, and secretaries.).  
INSERT INTO users VALUES ('00000000', 'admin1', 'admin', '1', 'GW', 'admin', 'ADMN');
INSERT INTO users VALUES ('11111111', 'admin2', 'admin', '2', 'GW', 'admin', 'ADMN');

INSERT INTO users VALUES ('00000001', 'student1', 'Bob', 'Bobby', 'Thurston', 'student', 'CSCI');
INSERT INTO users VALUES ('00000002', 'student2', 'Billy', 'Bobby', 'Shenkman', 'student', 'ECE');
INSERT INTO users VALUES ('00000003', 'student3', 'Bobby', 'Brown', 'Munson', 'student', 'MATH');
INSERT INTO users VALUES ('00000038', 'student4', 'Laiba', 'Siddique', 'VA', 'student', 'CSCI'); -- Feel Free to change this (out of ideas)
INSERT INTO users VALUES ('00000039', 'student5', 'Tabitha', 'Shaw', 'Shenkman', 'student', 'CSCI'); -- Feel free to change this
INSERT INTO users VALUES ('00000040', 'student6', 'Kate', 'Peterson', 'Munson', 'student', 'CSCI'); -- Feel free to change this
INSERT INTO users VALUES ('88888888', 'student7', 'Billie', 'Holiday', 'MD', 'student', 'CSCI'); -- REQUIRED
INSERT INTO users VALUES ('99999999', 'student8', 'Diana', 'Krall', 'DC', 'student', 'CSCI'); -- REQUIRED
INSERT INTO users VALUES ('00000041', 'student9', 'Billy', 'Bobby', '12345 DC Street, DC, DC, 12345', 'student', 'CSCI'); -- Student of matching name to test transript functionality


INSERT INTO users VALUES ('00000004', 'prof1', 'Walcelio', 'Melo', 'GWU', 'instructor', 'CSCI'); -- CSCI 6221
INSERT INTO users VALUES ('00000005', 'prof2', 'Bhagirath', 'Narahari', 'GWU', 'instructor', 'CSCI'); -- CSCI 6461
INSERT INTO users VALUES ('00000006', 'prof3', 'Abdou', 'Youssef', 'GWU', 'instructor', 'CSCI'); -- CSCI 6212 (Prof Hyeong-Ah Choi teaches other sections) and 6246, and 6325
INSERT INTO users VALUES ('00000007', 'prof4', 'John', 'Sipple', 'GWU', 'instructor', 'CSCI'); -- CSCI 6220 (unavailable) so 6364: Machine Learning
INSERT INTO users VALUES ('00000008', 'prof5', 'James', 'Taylor', 'GWU', 'instructor', 'CSCI'); -- CSCI 6232 (unavailable), so using CSCI 6431: Cmputer Networks instead
INSERT INTO users VALUES ('00000009', 'prof6', 'Hyeong-Ah', 'Choi', 'GWU', 'instructor', 'CSCI'); -- Teaches CSCI 6212 along Abdou Youssef to test out having more than 1 instructor for a class
INSERT INTO users VALUES ('00000010', 'prof7', 'Rolando', 'Fernandez', 'GWU', 'instructor', 'CSCI'); -- CSCI 6241 and 6242 (unavailable), so using 6441: Database Management Systems and 6442: Database Systems 2, and 6251: Cloud computing (unavailable), so using 6907: Cloud Computing
INSERT INTO users VALUES ('00000011', 'prof8', 'Gabriel', 'Parmer', 'GWU', 'instructor', 'CSCI'); -- CSCI 6246 (unavailable) so using 6411: Advanced Operating Systems, and 6339
INSERT INTO users VALUES ('00000012', 'prof9', 'Elyse', 'Nicolas', 'GWU', 'instructor', 'CSCI'); -- CSCI 6260 (unavailable) so using 6562: Design of Interactive Multimedia
INSERT INTO users VALUES ('00000013', 'prof10', 'Jon', 'McKeeby', 'GWU', 'instructor', 'CSCI'); -- CSCI 6254 (unavailable) so using 6231: Software Engineering
INSERT INTO users VALUES ('00000014', 'prof11', 'James', 'Hahn', 'GWU', 'instructor', 'CSCI'); -- CSCI 6262 (unavailable) so using 6554: Computer Graphics 2
INSERT INTO users VALUES ('00000015', 'prof12', 'Adam', 'Aviv', 'GWU', 'instructor', 'CSCI'); -- CSCI 6283 (unavailable) so using 6531: Computer Security
INSERT INTO users VALUES ('00000016', 'prof13', 'Arkady', 'Yerukhimovich', 'GWU', 'instructor', 'CSCI'); -- CSCI 6284 (unavailable) so using 6331: Cryptography, and 6384
INSERT INTO users VALUES ('00000017', 'prof14', 'Mohamed', 'Refaei', 'GWU', 'instructor', 'MATH'); -- CSCI 6286 (unavailable) so using 6541: Network Security
INSERT INTO users VALUES ('00000018', 'prof15', 'Sean', 'Yun', 'GWU', 'instructor', 'ECE'); -- ECE 6241 (unavailable) so using 6510: Communications Theory
INSERT INTO users VALUES ('00000019', 'prof16', 'Shahrokh', 'Ahmadi', 'GWU', 'instructor', 'ECE'); -- ECE 6242 (unavailable) so using 6010: Linear Systems Theory
INSERT INTO users VALUES ('00000020', 'prof17', 'Valentina', 'Harizanov', 'GWU', 'instructor', 'MATH'); -- MATH 6210 (unavailable) so using 3710: Intro to Mathematical Logic

INSERT INTO users VALUES ('00000021', 'sec1', 'Wally', 'Melbourne', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6221
INSERT INTO users VALUES ('00000022', 'sec2', 'Amaranth', 'Nihari', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6461
INSERT INTO users VALUES ('00000023', 'sec3', 'Abdul', 'Yusuf', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6212 (Prof.s Poorvi Vora and Hyeong-Ah Choi teach other sections) and 6246, and 6325
INSERT INTO users VALUES ('00000024', 'sec4', 'Johny', 'Sip', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6220 (unavailable) so 6364: Machine Learning
INSERT INTO users VALUES ('00000025', 'sec5', 'Jimmy', 'Tay', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6232 (unavailable), so using CSCI 6431: Cmputer Networks instead
INSERT INTO users VALUES ('00000026', 'sec6', 'Hyah', 'Choo', 'GWU', 'gradSec', 'CSCI'); -- Assists CSCI 6212 along sec3 to test out having more than 1 grad sec for a class. Name prounouced "HyACHOO". 
INSERT INTO users VALUES ('00000027', 'sec7', 'Christiano', 'Rolando', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6241 and 6242 (unavailable), so using 6441: Database Management Systems and 6442: Database Systems 2, and 6251: Cloud computing (unavailable), so using 6907: Cloud Computing
INSERT INTO users VALUES ('00000028', 'sec8', 'Gabby', 'Palmer', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6246 (unavailable) so using 6411: Advanced Operating Systems, and 6339
INSERT INTO users VALUES ('00000029', 'sec9', 'Ellie', 'Nick', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6260 (unavailable) so using 6562: Design of Interactive Multimedia
INSERT INTO users VALUES ('00000030', 'sec10', 'John', 'Cena', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6254 (unavailable) so using 6231: Software Engineering
INSERT INTO users VALUES ('00000031', 'sec11', 'Jimmy', 'Hannah', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6262 (unavailable) so using 6554: Computer Graphics 2
INSERT INTO users VALUES ('00000032', 'sec12', 'Adam', 'Aveeno', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6283 (unavailable) so using 6531: Computer Security
INSERT INTO users VALUES ('00000033', 'sec13', 'Ark', 'Noah', 'GWU', 'gradSec', 'CSCI'); -- CSCI 6284 (unavailable) so using 6331: Cryptography, and 6384
INSERT INTO users VALUES ('00000034', 'sec14', 'Michelangelo', 'Raphael', 'GWU', 'gradSec', 'MATH'); -- CSCI 6286 (unavailable) so using 6541: Network Security
INSERT INTO users VALUES ('00000035', 'sec15', 'Seannie', 'You', 'GWU', 'gradSec', 'ECE'); -- ECE 6241 (unavailable) so using 6510: Communications Theory
INSERT INTO users VALUES ('00000036', 'sec16', 'Shah-Rukh', 'Kahn', 'GWU', 'gradSec', 'ECE'); -- ECE 6242 (unavailable) so using 6010: Linear Systems Theory
INSERT INTO users VALUES ('00000037', 'sec17', 'Valentine', 'Connie', 'GWU', 'gradSec', 'MATH'); -- MATH 6210 (unavailable) so using 3710: Intro to Mathematical Logic

-- SELECT * FROM users;

-- Add admins to their table. 
INSERT INTO administrator VALUES ('00000000', 'USC', 101); 
INSERT INTO administrator VALUES ('11111111', 'USC', 102); 

-- SELECT * FROM administrator;


-- Add instructors to their table. 
INSERT INTO instructor VALUES ('00000004', 16, 'SEH', 4101); -- Feel free to change instructor office hour timeslots (and any other info for them)
INSERT INTO instructor VALUES ('00000005', 17, 'SEH', 4102); 
INSERT INTO instructor VALUES ('00000006', 18, 'SEH', 4103); 
INSERT INTO instructor VALUES ('00000007', 19, 'SEH', 4104); 
INSERT INTO instructor VALUES ('00000008', 20, 'SEH', 4105); 
INSERT INTO instructor VALUES ('00000009', 16, 'SEH', 4106); 
INSERT INTO instructor VALUES ('00000010', 17, 'SEH', 4107); 
INSERT INTO instructor VALUES ('00000011', 18, 'SEH', 4108); 
INSERT INTO instructor VALUES ('00000012', 19, 'SEH', 4109); 
INSERT INTO instructor VALUES ('00000013', 20, 'SEH', 4110); 
INSERT INTO instructor VALUES ('00000014', 16, 'SEH', 4111); 
INSERT INTO instructor VALUES ('00000015', 17, 'SEH', 4112); 
INSERT INTO instructor VALUES ('00000016', 18, 'SEH', 4113); 
INSERT INTO instructor VALUES ('00000017', 19, 'SEH', 4114); 

INSERT INTO instructor VALUES ('00000018', 20, 'SEH', 5101); 
INSERT INTO instructor VALUES ('00000019', 16, 'SEH', 5102); 

INSERT INTO instructor VALUES ('00000020', 17, 'PHIL', 1201); 

-- SELECT * FROM instructor;


-- Add secretaries to their table. 
INSERT INTO grad_secretary VALUES ('00000021', 21); -- Feel free to change instructor office hour timeslots (and any other info for them)
INSERT INTO grad_secretary VALUES ('00000022', 22);
INSERT INTO grad_secretary VALUES ('00000023', 23);
INSERT INTO grad_secretary VALUES ('00000024', 24);
INSERT INTO grad_secretary VALUES ('00000025', 25);
INSERT INTO grad_secretary VALUES ('00000026', 21);
INSERT INTO grad_secretary VALUES ('00000027', 22);
INSERT INTO grad_secretary VALUES ('00000028', 23);
INSERT INTO grad_secretary VALUES ('00000029', 24);
INSERT INTO grad_secretary VALUES ('00000030', 25);
INSERT INTO grad_secretary VALUES ('00000031', 21);
INSERT INTO grad_secretary VALUES ('00000032', 22);
INSERT INTO grad_secretary VALUES ('00000033', 23);
INSERT INTO grad_secretary VALUES ('00000034', 24);
INSERT INTO grad_secretary VALUES ('00000035', 25);
INSERT INTO grad_secretary VALUES ('00000036', 21);
INSERT INTO grad_secretary VALUES ('00000037', 22);

-- SELECT * FROM grad_secretary;


--  Add students to their table. 
INSERT INTO grad_student VALUES ('00000001', 'Masters', 2026);
INSERT INTO grad_student VALUES ('00000002', 'Masters', 2026);
INSERT INTO grad_student VALUES ('00000003', 'Masters', 2026);
INSERT INTO grad_student VALUES ('00000038', 'PhD', 2026);
INSERT INTO grad_student VALUES ('00000039', 'PhD', 2026);
INSERT INTO grad_student VALUES ('00000040', 'PhD', 2026);
INSERT INTO grad_student VALUES ('00000041', 'PhD', 2027);

INSERT INTO grad_student VALUES ('88888888', 'Masters', 2027); -- REQUIRED
INSERT INTO grad_student VALUES ('99999999', 'Masters', 2027); -- REQUIRED


-- SELECT * FROM grad_student;


-- Add courses
INSERT INTO course VALUES ('CSCI', 6221, 'SW Paradigms', 3);
INSERT INTO course VALUES ('CSCI', 6461, 'Computer Architecture', 3);
INSERT INTO course VALUES ('CSCI', 6212, 'Algorithms', 3);
INSERT INTO course VALUES ('CSCI', 6220, 'Machine Learning', 3);

INSERT INTO course VALUES ('CSCI', 6232, 'Networks 1', 3);
INSERT INTO course VALUES ('CSCI', 6233, 'Networks 2', 3);
INSERT INTO course VALUES ('CSCI', 6241, 'Database 1', 3);
INSERT INTO course VALUES ('CSCI', 6242, 'Database 2', 3);

INSERT INTO course VALUES ('CSCI', 6246, 'Compilers', 3);
INSERT INTO course VALUES ('CSCI', 6260, 'Multimedia', 3);
INSERT INTO course VALUES ('CSCI', 6251, 'Cloud Computing', 3);
INSERT INTO course VALUES ('CSCI', 6254, 'SW Engineering', 3);

INSERT INTO course VALUES ('CSCI', 6262, 'Graphics 1', 3);
INSERT INTO course VALUES ('CSCI', 6283, 'Security 1', 3);
INSERT INTO course VALUES ('CSCI', 6284, 'Cryptography', 3);
INSERT INTO course VALUES ('CSCI', 6286, 'Network Security', 3);

INSERT INTO course VALUES ('CSCI', 6325, 'Algorithms 2', 3);
INSERT INTO course VALUES ('CSCI', 6339, 'Embedded Systems', 3);
INSERT INTO course VALUES ('CSCI', 6384, 'Cryptography 2', 3);

INSERT INTO course VALUES ('ECE', 6241, 'Communication Theory', 3);
INSERT INTO course VALUES ('ECE', 6242, 'Information Theory', 2);

INSERT INTO course VALUES ('MATH', 6210, 'Logic', 2);

-- SELECT * FROM course;


-- Add Prerequisites
INSERT INTO prerequisites VALUES ('CSCI', 6233, 'CSCI', 6232); -- Networks 2, Networks 1
INSERT INTO prerequisites VALUES ('CSCI', 6242, 'CSCI', 6241); -- DB 2, DB 1
INSERT INTO prerequisites VALUES ('CSCI', 6246, 'CSCI', 6461); -- Compilers, Computer Architecture
INSERT INTO prerequisites VALUES ('CSCI', 6246, 'CSCI', 6212); -- Compilers, Algorithms
INSERT INTO prerequisites VALUES ('CSCI', 6251, 'CSCI', 6461); -- Cloud Computing, Computer Architecture
INSERT INTO prerequisites VALUES ('CSCI', 6254, 'CSCI', 6221); -- SW Engineering, SW Paradigms
INSERT INTO prerequisites VALUES ('CSCI', 6283, 'CSCI', 6212); -- Security 1, Algorithms
INSERT INTO prerequisites VALUES ('CSCI', 6284, 'CSCI', 6212); -- Cryptography, Algorithms
INSERT INTO prerequisites VALUES ('CSCI', 6286, 'CSCI', 6283); -- Network Security, Security 1
INSERT INTO prerequisites VALUES ('CSCI', 6286, 'CSCI', 6232); -- Network Security, Networks 1
INSERT INTO prerequisites VALUES ('CSCI', 6325, 'CSCI', 6212); -- Algorithms 2, Algorithms
INSERT INTO prerequisites VALUES ('CSCI', 6339, 'CSCI', 6461); -- Embedded Systems, Computer Architecture
INSERT INTO prerequisites VALUES ('CSCI', 6339, 'CSCI', 6212); -- Embedded Systems, Algorithms
INSERT INTO prerequisites VALUES ('CSCI', 6384, 'CSCI', 6284); -- Cryptography 2, Cryptography

-- SELECT * FROM prerequisites;


-- Add course sections. 
INSERT INTO course_section VALUES (1, 'CSCI', 6221, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (2, 'CSCI', 6461, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (3, 'CSCI', 6212, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (4, 'CSCI', 6232, 1, 'Fall', 2025);

INSERT INTO course_section VALUES (5, 'CSCI', 6233, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (6, 'CSCI', 6241, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (7, 'CSCI', 6242, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (8, 'CSCI', 6246, 1, 'Fall', 2025);

INSERT INTO course_section VALUES (9, 'CSCI', 6251, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (10, 'CSCI', 6254, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (11, 'CSCI', 6260, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (12, 'CSCI', 6262, 1, 'Fall', 2025);

INSERT INTO course_section VALUES (13, 'CSCI', 6283, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (14, 'CSCI', 6284, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (15, 'CSCI', 6286, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (16, 'CSCI', 6384, 1, 'Fall', 2025);

INSERT INTO course_section VALUES (17, 'ECE', 6241, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (18, 'ECE', 6242, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (44, 'ECE', 6242, 2, 'Fall', 2025); -- 4/8 addition by Kate
INSERT INTO course_section VALUES (19, 'MATH', 6210, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (20, 'CSCI', 6339, 1, 'Fall', 2025);

INSERT INTO course_section VALUES (42, 'CSCI', 6325, 1, 'Fall', 2025);
INSERT INTO course_section VALUES (43, 'CSCI', 6220, 1, 'Fall', 2025);

-- -- 2nd section of cources plus courses with some time variety. Should we comment these out for now while working on the basics?
INSERT INTO course_section VALUES (21, 'CSCI', 6221, 2, 'Fall', 2025); -- Setup
INSERT INTO course_section VALUES (22, 'CSCI', 6461, 2, 'Fall', 2025);
INSERT INTO course_section VALUES (23, 'CSCI', 6212, 2, 'Fall', 2025);
INSERT INTO course_section VALUES (24, 'CSCI', 6232, 2, 'Fall', 2025);

-- -- INSERT INTO course_section VALUES (25, 'CSCI', 6233, 2, 'Fall', 2025); -- Not setup
-- -- INSERT INTO course_section VALUES (26, 'CSCI', 6241, 2, 'Fall', 2025);
-- -- INSERT INTO course_section VALUES (27, 'CSCI', 6242, 2, 'Fall', 2025);
-- -- INSERT INTO course_section VALUES (28, 'CSCI', 6246, 2, 'Fall', 2025);

-- -- INSERT INTO course_section VALUES (29, 'CSCI', 6251, 2, 'Fall', 2025); -- too much work to deal with this many classes for now. later problem. 
-- -- INSERT INTO course_section VALUES (30, 'CSCI', 6254, 2, 'Fall', 2025);
-- -- INSERT INTO course_section VALUES (31, 'CSCI', 6260, 2, 'Fall', 2025);
-- -- INSERT INTO course_section VALUES (32, 'CSCI', 6262, 2, 'Fall', 2025);

-- -- INSERT INTO course_section VALUES (33, 'CSCI', 6283, 2, 'Fall', 2025);
-- -- INSERT INTO course_section VALUES (34, 'CSCI', 6284, 2, 'Fall', 2025);
-- -- INSERT INTO course_section VALUES (35, 'CSCI', 6286, 2, 'Fall', 2025);
-- -- INSERT INTO course_section VALUES (36, 'CSCI', 6384, 2, 'Fall', 2025);

INSERT INTO course_section VALUES (37, 'ECE', 6241, 1, 'Spring', 2024); -- Useful for transcript -- Setup
INSERT INTO course_section VALUES (38, 'ECE', 6242, 1, 'Fall', 2024); -- Useful for transcript
INSERT INTO course_section VALUES (39, 'MATH', 6210, 1, 'Spring', 2025); -- Useful for in progress courses
INSERT INTO course_section VALUES (40, 'CSCI', 6339, 1, 'Spring', 2025); -- Useful for in progress courses
INSERT INTO course_section VALUES (41, 'CSCI', 6339, 2, 'Spring', 2025); -- Useful for in progress courses

-- SELECT * FROM course_section;


-- Add section rooms. (Tried my best to make sure no 2 classes in the same room at the same time, but this may need extra review.). 
-- (Assume 2 class sections with the same professor and the same time, but different rooms is because the room is large and has dividers that have been raised up, 
-- the professor is in person for 1 class, but online or zoom for the other, or 1 section is a lab or section being lead by the secretary instead.). 
INSERT INTO sec_room VALUES (1, 'SEH', 4002);
INSERT INTO sec_room VALUES (2, 'SEH', 1300);
INSERT INTO sec_room VALUES (3, 'SEH', 1450);
INSERT INTO sec_room VALUES (4, 'SEH', 4003);

INSERT INTO sec_room VALUES (5, 'SEH', 4004);
INSERT INTO sec_room VALUES (6, 'SEH', 4006);
INSERT INTO sec_room VALUES (7, 'SEH', 4005);
INSERT INTO sec_room VALUES (8, 'SEH', 4007);

INSERT INTO sec_room VALUES (9, 'SEH', 4008);
INSERT INTO sec_room VALUES (10, 'SEH', 1400);
INSERT INTO sec_room VALUES (11, 'SEH', 4004);
INSERT INTO sec_room VALUES (12, 'SEH', 4007);

INSERT INTO sec_room VALUES (13, 'SEH', 4001); -- Testing capicity limit is easiest with this class. 
INSERT INTO sec_room VALUES (14, 'SEH', 4005);
INSERT INTO sec_room VALUES (15, 'SEH', 4003);
INSERT INTO sec_room VALUES (16, 'SEH', 4004);

INSERT INTO sec_room VALUES (17, 'SEH', 5001);
INSERT INTO sec_room VALUES (18, 'SEH', 5001);
INSERT INTO sec_room VALUES (19, 'PHIL', 1120); -- 4/8 addition by Kate
INSERT INTO sec_room VALUES (44, 'PHIL', 1120); -- 4/8 addition by Kate
INSERT INTO sec_room VALUES (20, 'SEH', 4006);

INSERT INTO sec_room VALUES (42, 'SEH', 1400);
INSERT INTO sec_room VALUES (43, 'SEH', 4003);


-- Alternate sections
INSERT INTO sec_room VALUES (21, 'SEH', 4002); -- Use diff time for this -- Setup
INSERT INTO sec_room VALUES (22, 'SEH', 1400);
INSERT INTO sec_room VALUES (23, 'SEH', 1450); -- diff time
INSERT INTO sec_room VALUES (24, 'SEH', 4001); -- Testing capicity limit is easiest with this class. 

-- -- INSERT INTO sec_room VALUES (25, 'SEH', 4001); -- Testing capicity limit is easiest with this class. 
-- -- INSERT INTO sec_room VALUES (26, 'SEH', 4004);
-- -- INSERT INTO sec_room VALUES (27, 'SEH', 4007);
-- -- INSERT INTO sec_room VALUES (28, 'SEH', 4006); -- time right after

-- -- INSERT INTO sec_room VALUES (29, 'SEH', 4008); -- time right before -- too much work to deal with right now. Later problem. 
-- -- INSERT INTO sec_room VALUES (30, 'SEH', 4006);
-- -- INSERT INTO sec_room VALUES (31, 'SEH', 4006);
-- -- INSERT INTO sec_room VALUES (32, 'SEH', 4006);

-- -- INSERT INTO sec_room VALUES (33, 'SEH', 4006);
-- -- INSERT INTO sec_room VALUES (34, 'SEH', 4006);
-- -- INSERT INTO sec_room VALUES (35, 'SEH', 4006);
-- -- INSERT INTO sec_room VALUES (36, 'SEH', 4006);

INSERT INTO sec_room VALUES (37, 'SEH', 5001); -- Setup
INSERT INTO sec_room VALUES (38, 'SEH', 5001);
INSERT INTO sec_room VALUES (39, 'PHIL', 1120);
INSERT INTO sec_room VALUES (40, 'SEH', 4006);
INSERT INTO sec_room VALUES (41, 'SEH', 1300);

-- SELECT * FROM sec_room;


-- Add timeslots to sections. 
INSERT INTO sec_time VALUES (1, 1);
INSERT INTO sec_time VALUES (2, 2);
INSERT INTO sec_time VALUES (3, 3);
INSERT INTO sec_time VALUES (4, 11);

INSERT INTO sec_time VALUES (5, 12);
INSERT INTO sec_time VALUES (6, 13);
INSERT INTO sec_time VALUES (7, 14);
INSERT INTO sec_time VALUES (8, 2);

INSERT INTO sec_time VALUES (9, 11);
INSERT INTO sec_time VALUES (10, 26);
INSERT INTO sec_time VALUES (11, 14);
INSERT INTO sec_time VALUES (12, 13);

INSERT INTO sec_time VALUES (13, 12);
INSERT INTO sec_time VALUES (14, 11);
INSERT INTO sec_time VALUES (15, 13);
INSERT INTO sec_time VALUES (16, 3);

INSERT INTO sec_time VALUES (17, 11);
INSERT INTO sec_time VALUES (18, 12);
INSERT INTO sec_time VALUES (44, 12); -- 4/8 addition by Kate
INSERT INTO sec_time VALUES (19, 13);
INSERT INTO sec_time VALUES (20, 9);

INSERT INTO sec_time VALUES (42, 14);
INSERT INTO sec_time VALUES (43, 14);

--Alternate Sections
INSERT INTO sec_time VALUES (21, 5); -- Setup
INSERT INTO sec_time VALUES (22, 2);
INSERT INTO sec_time VALUES (23, 15);
INSERT INTO sec_time VALUES (24, 10);

INSERT INTO sec_time VALUES (37, 11);
INSERT INTO sec_time VALUES (38, 12);
INSERT INTO sec_time VALUES (39, 13);
INSERT INTO sec_time VALUES (40, 9);
INSERT INTO sec_time VALUES (41, 10);

-- SELECT * FROM sec_time;


-- Assign professors and secretaries to the courses they are teaching. 
-- Instructors
INSERT INTO teaches VALUES ('00000004', 1); 
INSERT INTO teaches VALUES ('00000004', 21); 

INSERT INTO teaches VALUES ('00000005', 2); -- CSCI 6461
INSERT INTO teaches VALUES ('00000005', 22); -- CSCI 6461

INSERT INTO teaches VALUES ('00000006', 3); -- CSCI 6212 (Prof.s Choi teaches other sections) and 6246, and 6325
INSERT INTO teaches VALUES ('00000009', 23); -- CSCI 6212 (Prof. Choi)
INSERT INTO teaches VALUES ('00000006', 8); -- CSCI 6246
INSERT INTO teaches VALUES ('00000006', 42); -- CSCI 6325

INSERT INTO teaches VALUES ('00000007', 43); -- CSCI 6364

INSERT INTO teaches VALUES ('00000008', 4); -- CSCI 6232 (unavailable), so using CSCI 6431: Computer Networks instead
INSERT INTO teaches VALUES ('00000008', 24); -- CSCI 6232 
INSERT INTO teaches VALUES ('00000008', 5); -- CSCI 6233: Networks 2

INSERT INTO teaches VALUES ('00000009', 3); -- Teaches CSCI 6212 along Abdou Youssef to test out having more than 1 instructor for a class

INSERT INTO teaches VALUES ('00000010', 6); -- CSCI 6241 and 6242 (unavailable), so using 6441: Database Management Systems and 6442: Database Systems 2, and 6251: Cloud computing (unavailable), so using 6907: Cloud Computing
INSERT INTO teaches VALUES ('00000010', 7); -- CSCI 6242 
INSERT INTO teaches VALUES ('00000010', 9); -- CSCI 6251

INSERT INTO teaches VALUES ('00000011', 8); -- CSCI 6246 (unavailable) so using 6411: Advanced Operating Systems, and 6339
INSERT INTO teaches VALUES ('00000011', 20); -- CSCI 6339
INSERT INTO teaches VALUES ('00000011', 40); -- CSCI 6339
INSERT INTO teaches VALUES ('00000011', 41); -- CSCI 6339

INSERT INTO teaches VALUES ('00000012', 11); -- CSCI 6260 (unavailable) so using 6562: Design of Interactive Multimedia

INSERT INTO teaches VALUES ('00000013', 10); -- CSCI 6254 (unavailable) so using 6231: Software Engineering

INSERT INTO teaches VALUES ('00000014', 12); -- CSCI 6262 (unavailable) so using 6554: Computer Graphics 2

INSERT INTO teaches VALUES ('00000015', 13); -- CSCI 6283 (unavailable) so using 6531: Computer Security

INSERT INTO teaches VALUES ('00000016', 14); -- CSCI 6284 (unavailable) so using 6331: Cryptography, and 6384
INSERT INTO teaches VALUES ('00000016', 16); -- CSCI 6384

INSERT INTO teaches VALUES ('00000017', 15); -- CSCI 6286 (unavailable) so using 6541: Network Security

INSERT INTO teaches VALUES ('00000018', 17); -- ECE 6241 (unavailable) so using 6510: Communications Theory
INSERT INTO teaches VALUES ('00000018', 37); -- ECE 6241 

INSERT INTO teaches VALUES ('00000019', 18); -- ECE 6242 (unavailable) so using 6010: Linear Systems Theory
INSERT INTO teaches VALUES ('00000018', 44); -- ECE 6242, 4/8 addition by Kate
INSERT INTO teaches VALUES ('00000019', 38); -- ECE 6242, previous semester

INSERT INTO teaches VALUES ('00000020', 19); -- MATH 6210 (unavailable) so using 3710: Intro to Mathematical Logic
INSERT INTO teaches VALUES ('00000020', 39); -- MATH 6210 


-- Secretaries. 
INSERT INTO teaches VALUES ('00000021', 1); 
INSERT INTO teaches VALUES ('00000021', 21); 

INSERT INTO teaches VALUES ('00000022', 2); -- CSCI 6461
INSERT INTO teaches VALUES ('00000022', 22); -- CSCI 6461

INSERT INTO teaches VALUES ('00000023', 3); -- CSCI 6212 (Prof Choi teaches other sections) and 6246, and 6325
INSERT INTO teaches VALUES ('00000026', 23); -- CSCI 6212 (Prof. Choi)
INSERT INTO teaches VALUES ('00000023', 8); -- CSCI 6246
INSERT INTO teaches VALUES ('00000023', 42); -- CSCI 6325

INSERT INTO teaches VALUES ('00000024', 43); -- CSCI 6364

INSERT INTO teaches VALUES ('00000025', 4); -- CSCI 6232 (unavailable), so using CSCI 6431: Computer Networks instead
INSERT INTO teaches VALUES ('00000025', 24); -- CSCI 6232 
INSERT INTO teaches VALUES ('00000025', 5); -- CSCI 6233: Networks 2

INSERT INTO teaches VALUES ('00000026', 3); -- Teaches CSCI 6212 along Abdou Youssef to test out having more than 1 instructor for a class

INSERT INTO teaches VALUES ('00000027', 6); -- CSCI 6241 and 6242 (unavailable), so using 6441: Database Management Systems and 6442: Database Systems 2, and 6251: Cloud computing (unavailable), so using 6907: Cloud Computing
INSERT INTO teaches VALUES ('00000027', 7); -- CSCI 6242 
INSERT INTO teaches VALUES ('00000027', 9); -- CSCI 6251

INSERT INTO teaches VALUES ('00000028', 8); -- CSCI 6246 (unavailable) so using 6411: Advanced Operating Systems, and 6339
INSERT INTO teaches VALUES ('00000028', 20); -- CSCI 6339
INSERT INTO teaches VALUES ('00000028', 40); -- CSCI 6339
INSERT INTO teaches VALUES ('00000028', 41); -- CSCI 6339

INSERT INTO teaches VALUES ('00000029', 11); -- CSCI 6260 (unavailable) so using 6562: Design of Interactive Multimedia

INSERT INTO teaches VALUES ('00000030', 10); -- CSCI 6254 (unavailable) so using 6231: Software Engineering

INSERT INTO teaches VALUES ('00000031', 12); -- CSCI 6262 (unavailable) so using 6554: Computer Graphics 2

INSERT INTO teaches VALUES ('00000032', 13); -- CSCI 6283 (unavailable) so using 6531: Computer Security

INSERT INTO teaches VALUES ('00000033', 14); -- CSCI 6284 (unavailable) so using 6331: Cryptography, and 6384
INSERT INTO teaches VALUES ('00000033', 16); -- CSCI 6384

INSERT INTO teaches VALUES ('00000034', 15); -- CSCI 6286 (unavailable) so using 6541: Network Security

INSERT INTO teaches VALUES ('00000035', 17); -- ECE 6241 (unavailable) so using 6510: Communications Theory
INSERT INTO teaches VALUES ('00000035', 37); -- ECE 6241 

INSERT INTO teaches VALUES ('00000036', 18); -- ECE 6242 (unavailable) so using 6010: Linear Systems Theory
INSERT INTO teaches VALUES ('00000036', 38); -- ECE 6242 

INSERT INTO teaches VALUES ('00000037', 19); -- MATH 6210 (unavailable) so using 3710: Intro to Mathematical Logic
INSERT INTO teaches VALUES ('00000037', 39); -- MATH 6210 

-- SELECT * FROM teaches;


-- Assign students to the courses they are taking. 
INSERT INTO takes VALUES ('00000001', 37, 'A'); -- If taking, sections of current and past courses
INSERT INTO takes VALUES ('00000001', 39, 'IP');

INSERT INTO takes VALUES ('00000002', 37, 'A-');
INSERT INTO takes VALUES ('00000002', 40, 'IP');

INSERT INTO takes VALUES ('00000003', 37, 'A');
INSERT INTO takes VALUES ('00000003', 41, 'IP');

INSERT INTO takes VALUES ('00000038', 38, 'A');
INSERT INTO takes VALUES ('00000038', 39, 'IP'); 

INSERT INTO takes VALUES ('00000039', 38, 'A'); 
INSERT INTO takes VALUES ('00000039', 40, 'IP'); 

INSERT INTO takes VALUES ('00000040', 38, 'A'); 
INSERT INTO takes VALUES ('00000040', 41, 'IP'); 

INSERT INTO takes VALUES ('00000041', 2, 'IP'); 
INSERT INTO takes VALUES ('00000041', 23, 'IP'); 

INSERT INTO takes VALUES ('88888888', 2, 'IP'); -- REQUIRED
INSERT INTO takes VALUES ('88888888', 23, 'IP'); -- REQUIRED

-- Student `99999999` has not yet taken or registered for any classes. 

-- INSERT INTO takes VALUES ('00000001', 1, 'A'); -- For next semester.
-- INSERT INTO takes VALUES ('00000001', 2, 'IP');

-- INSERT INTO takes VALUES ('00000002', 1, 'A-'); 
-- INSERT INTO takes VALUES ('00000002', 3, 'IP');

-- INSERT INTO takes VALUES ('00000003', 1, 'A');
-- INSERT INTO takes VALUES ('00000003', 4, 'IP');

-- INSERT INTO takes VALUES ('00000038', 2, 'A');
-- INSERT INTO takes VALUES ('00000038', 3, 'IP'); 

-- INSERT INTO takes VALUES ('00000039', 2, 'A'); 
-- INSERT INTO takes VALUES ('00000039', 4, 'IP'); 

-- INSERT INTO takes VALUES ('00000040', 4, 'A'); 
-- INSERT INTO takes VALUES ('00000040', 6, 'IP');

-- SELECT * FROM takes;

-- Give some ratings to some professors
INSERT INTO ratings VALUES ('00000035', '00000001', 5.0); 
INSERT INTO ratings VALUES ('00000020', '00000001', 5.0); 
INSERT INTO ratings VALUES ('00000035', '00000002', 5.0); 
INSERT INTO ratings VALUES ('00000028', '00000002', 5.0); 
INSERT INTO ratings VALUES ('00000035', '00000003', 5.0); 
INSERT INTO ratings VALUES ('00000005', '00000041', 5.0); 


-- -- SQL STATEMENT TESTING (Unable to access branch on my computer, so testing here). ALL STILL WORK. 
-- SELECT course.dept, course.cnum, course.title, course.credit_hours, 
--     course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room 
--     FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) 
--         JOIN sec_time ON course_section.CRN = sec_time.CRN 
--         JOIN time_slot ON sec_time.TSID = time_slot.TSID 
--         JOIN sec_room ON course_section.CRN = sec_room.CRN 
--     WHERE course_section.semester = 'Fall' AND course_section.year = '2025'
--     ORDER BY course_section.dept, course_section.cnum;

-- SELECT course.dept, course.cnum, course.title, course.credit_hours, 
--     course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room, 
--     course_section.semester, course_section.year
--     FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) 
--         JOIN sec_time ON course_section.CRN = sec_time.CRN 
--         JOIN time_slot ON sec_time.TSID = time_slot.TSID 
--         JOIN sec_room ON course_section.CRN = sec_room.CRN 
--     ORDER BY course_section.dept, course_section.cnum;

-- SELECT course_section.dept, course_section.cnum, course_section.CRN, users.first_name, users.last_name 
--     FROM course_section JOIN teaches ON course_section.CRN = teaches.CRN 
--         JOIN users ON teaches.UID = users.UID 
--     WHERE course_section.semester = 'Fall' AND course_section.year = '2025' AND users.user_type = 'instructor'
--     ORDER BY course_section.dept, course_section.cnum;

-- -- Full table showing all info for class for certain semester including instructor
-- SELECT course.dept, course.cnum, course.title, course.credit_hours, 
-- course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room, 
-- users.first_name, users.last_name 
-- FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) 
--     JOIN teaches ON course_section.CRN = teaches.CRN 
--     JOIN users ON teaches.UID = users.UID 
--     JOIN sec_time ON course_section.CRN = sec_time.CRN 
--     JOIN time_slot ON sec_time.TSID = time_slot.TSID 
--     JOIN sec_room ON course_section.CRN = sec_room.CRN 
-- WHERE course_section.semester = 'Fall' AND course_section.year = '2025' AND users.user_type = 'instructor'
-- ORDER BY course_section.dept, course_section.cnum;

-- -- Full table showing all info for class for all semesters including instructor
SELECT course.dept, course.cnum, course.title, course.credit_hours, 
course_section.sec_num, course_section.CRN, time_slot.start_time, time_slot.end_time, time_slot.day, sec_room.building, sec_room.room, 
users.first_name, users.last_name, course_section.semester, course_section.year
FROM course JOIN course_section ON (course.dept = course_section.dept AND course.cnum = course_section.cnum) 
    JOIN teaches ON course_section.CRN = teaches.CRN 
    JOIN users ON teaches.UID = users.UID 
    JOIN sec_time ON course_section.CRN = sec_time.CRN 
    JOIN time_slot ON sec_time.TSID = time_slot.TSID 
    JOIN sec_room ON course_section.CRN = sec_room.CRN 
    WHERE users.user_type = 'instructor'
ORDER BY course_section.dept, course_section.cnum;

-- SQL Statement for getting student info. 
SELECT users.UID, users.first_name, users.last_name, grad_student.degree_program, grad_student.grad_year, users.department
    FROM users JOIN grad_student ON users.UID = grad_student.SID
    ORDER BY users.UID;

-- SQL Statement for getting all classes all students are taking for transcripts 
SELECT grad_student.SID, users.first_name, users.last_name, course_section.CRN, course_section.dept, course_section.cnum, 
    course.title, course.credit_hours, course_section.semester, course_section.year, takes.grade
    FROM users JOIN grad_student ON users.UID = grad_student.SID
        JOIN takes ON takes.SID = grad_student.SID 
        JOIN course_section ON takes.CRN = course_section.CRN
        JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum)
    ORDER BY grad_student.SID;

-- SQL Statement for getting transcript for specific student (should change student name to question part in Python.)
SELECT grad_student.SID, users.first_name, users.last_name, course_section.CRN, course_section.dept, course_section.cnum, 
    course.title, course.credit_hours, course_section.semester, course_section.year, takes.grade
    FROM users JOIN grad_student ON users.UID = grad_student.SID
        JOIN takes ON takes.SID = grad_student.SID 
        JOIN course_section ON takes.CRN = course_section.CRN
        JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum)
    WHERE grad_student.SID = '88888888'
    ORDER BY grad_student.SID;

-- SQL statement for transcrupt in transcripts code. 
SELECT takes.SID, takes.CRN, takes.grade, course_section.dept, course_section.cnum, course_section.semester, course_section.year, 
    course.title, course.credit_hours, profs.first_name, profs.last_name 
    FROM takes JOIN course_section ON takes.CRN = course_section.CRN 
        JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) 
        JOIN teaches ON course_section.CRN = teaches.CRN 
        JOIN users AS profs ON teaches.UID = profs.UID 
    WHERE takes.SID = '00000001' AND profs.user_type = 'instructor';

SELECT takes.SID, takes.CRN, takes.grade, course_section.dept, course_section.cnum, course_section.CRN, course_section.semester, 
    course_section.year, course.title, course.credit_hours, profs.UID, profs.first_name, profs.last_name 
    FROM takes JOIN course_section ON takes.CRN = course_section.CRN 
        JOIN course ON (course_section.dept = course.dept AND course_section.cnum = course.cnum) 
        JOIN teaches ON course_section.CRN = teaches.CRN 
        JOIN users AS profs ON teaches.UID = profs.UID 
    WHERE takes.SID = '00000001' AND profs.user_type = 'instructor';

SELECT UID, AVG(rating) AS Rating FROM ratings GROUP BY UID;
SELECT MAX(room), department.building 
  FROM department JOIN classroom ON department.building = classroom.building
  WHERE department.dep_name = 'CSCI';