-- MySQL dump 10.13  Distrib 8.0.28, for Linux (x86_64)
--
-- Host: localhost    Database: quicky
-- ------------------------------------------------------
-- Server version	8.0.28-0ubuntu0.20.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `A_id` int NOT NULL AUTO_INCREMENT,
  `L_name` varchar(250) NOT NULL,
  `M_name` varchar(250) NOT NULL,
  `F_name` varchar(250) NOT NULL,
  `A_email` text NOT NULL,
  `A_pass` text CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `dept` text NOT NULL,
  `A_num` varchar(10) NOT NULL,
  `A_gender` varchar(1) NOT NULL,
  `img` text NOT NULL,
  PRIMARY KEY (`A_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'MISTRY','RAKESH','BHAVYA','admin@somaiya.edu','12345678','Information Technology','9999999999','M','');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `dept_id` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `dept_name` varchar(70) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `dept_short` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `dept_intake` int NOT NULL,
  `dept_seat_filled` int NOT NULL,
  `duration` int NOT NULL COMMENT 'Yrs',
  PRIMARY KEY (`dept_id`),
  UNIQUE KEY `dept_id` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES ('ST2201','COMPUTER ENGINEERING','CSE',120,120,4),('ST2202','INFORMATION TECHNOLOGY','IT',60,60,4),('ST2203','ELECTRONICS','ETRX',60,60,4),('ST2204','ELECTRONICS AND TELECOMMUNICATION','EXTC',120,120,4),('ST2207','ARTIFICIAL INTELLIGENCE AND DATA SCIENCE','AI-DS',60,60,4);
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `electives`
--

DROP TABLE IF EXISTS `electives`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `electives` (
  `course_code` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `sub_name_long` text CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `sub_name_short` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `sem` varchar(5) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `sub_type` int NOT NULL DEFAULT '1' COMMENT ' 1-Theory,0-Practical ',
  `elective_category` int DEFAULT NULL,
  `marks` int NOT NULL DEFAULT '0' COMMENT ' 1-Termtset marks 0-no marks ',
  `dept_id` varchar(20) NOT NULL,
  PRIMARY KEY (`course_code`,`sem`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `electives`
--

LOCK TABLES `electives` WRITE;
/*!40000 ALTER TABLE `electives` DISABLE KEYS */;
INSERT INTO `electives` VALUES ('1UILC8041','PROJECT MANAGEMENT','PM','sem8',1,18,1,'ST2202'),('1UILC8042','FINANCE MANAGEMENT','FM','sem8',1,18,1,'ST2202'),('1UITDLC6052','IOT DATA ANALYTICS','IOT-DA','sem6',1,21,1,'ST2202'),('1UITDLC6053','IMAGE PROCESSING','IP','sem6',1,21,1,'ST2202'),('1UITDLC8021','NATURAL LANGUAGE PROCESSING','NLP','sem8',1,1,1,'ST2202'),('1UITDLC8022','CLOUD SECURITY','CS','sem8',1,1,1,'ST2202'),('1UITDLC8031','EXPLAINABLE AI & RESPONSIBLE AI','EXAI','sem8',1,3,1,'ST2202'),('1UITDLC8033','AUGMENTED REALITY - VIRTUAL REALITY','ARVR','sem8',1,3,1,'ST2202');
/*!40000 ALTER TABLE `electives` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `electives_category`
--

DROP TABLE IF EXISTS `electives_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `electives_category` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(50) NOT NULL,
  `sem` varchar(5) NOT NULL,
  `dept_id` varchar(10) NOT NULL,
  PRIMARY KEY (`category_id`) USING BTREE,
  UNIQUE KEY `cat_name` (`cat_name`,`sem`,`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `electives_category`
--

LOCK TABLES `electives_category` WRITE;
/*!40000 ALTER TABLE `electives_category` DISABLE KEYS */;
INSERT INTO `electives_category` VALUES (21,'Department level elective','sem6','ST2202'),(1,'Departmental 1','sem8','ST2202'),(3,'Departmental 2','sem8','ST2202'),(14,'Instituitional','sem7','ST2202'),(18,'Instituitional','sem8','ST2202');
/*!40000 ALTER TABLE `electives_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `F_id` varchar(10) NOT NULL,
  `Designation` varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `L_name` text NOT NULL,
  `F_name` text NOT NULL,
  `M_name` text NOT NULL,
  `F_email` text NOT NULL,
  `F_password` text NOT NULL,
  `dept` text NOT NULL,
  `F_num` varchar(10) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `img` text NOT NULL,
  `first_login` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`F_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES ('220075','Mr','BHOR','HARSH','NAMDEV','hbhor@somaiya.edu','$2b$12$Tevg2N8W80UkCWdky7ucP.JJuEx7.Q4a5GwEoyGw6fbiVuao2QZjW','INFORMATION TECHNOLOGY','9221376428','M','220081.png',0),('220081','Prof.','SHAH','NASIM','BANU','nshah@somaiya.edu','$2b$12$rqGL9juGQzhz.xq.wKulv.HexRInUzSxnneICQk6V1sbc3bH26CrC','INFORMATION TECHNOLOGY','9821154828','F','220081.jpg',1),('220082','Prof.','SAWANT','PRASHANT','FATHER','prashant27@somaiya.edu','$2b$12$xmXO3Vc3Zm4rmvVJVQzGEucmWqyMDEXjYs4madLYiNuVKG0IsOq3m','INFORMATION TECHNOLOGY','9897987822','M','ps.jpg',1),('222222','Dr','Kotecha','Radhika','Nikhil','radhika.kotecha@somaiya.edu','$2b$12$7hIe9z0i6yXjtTB.mOT8k.IXe1zreejnYZmN37doKADW05EurmnOO','INFORMATION TECHNOLOGY','7698558637','F','220081.png',0);
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions`
--

DROP TABLE IF EXISTS `questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions` (
  `q_id` int NOT NULL AUTO_INCREMENT,
  `q_no` int NOT NULL,
  `question` text NOT NULL,
  `ans_type` int DEFAULT NULL COMMENT '0-mcq.1-oneline,2-descriptive',
  `opt1` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `opt2` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `opt3` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `opt4` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `correct_opt` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `q_time` text NOT NULL,
  `points` int DEFAULT NULL,
  `quiz_id` text NOT NULL,
  PRIMARY KEY (`q_id`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (69,1,'1+1=?',0,'1','2','4','3','option2','',1,'56'),(71,1,'1+1=?',1,NULL,NULL,NULL,NULL,NULL,'',1,'63'),(72,1,'1+1=?',1,NULL,NULL,NULL,NULL,NULL,'',1,'63'),(75,1,'1+1=?',1,NULL,NULL,NULL,NULL,NULL,'',1,'64'),(81,2,'2+2=?',0,'2','6','4','-','option3','',2,'64'),(82,3,'3+3=?',0,'3','4','5','6','option4','',2,'64'),(83,4,'4+4=?',0,'5','6','8','-','option3','',2,'64'),(84,5,'5*5=?',0,'10','20','30','25','option4','',2,'64'),(86,1,'1+1=?',0,'2','4','6','-','option1','',1,'68'),(87,2,'2+2=?',1,NULL,NULL,NULL,NULL,NULL,'',2,'68'),(91,1,'1+2=?',1,NULL,NULL,NULL,NULL,NULL,'',5,'69'),(92,1,'According to the Project Management Institute (PMI), project management is defined as “the application of knowledge, _____, _____, and techniques to project activities to meet the project requirements”',0,'skills, analysis','tools, analysis','analysis, theories','skills, tools','option4','',1,'70'),(93,2,'What is the first step in project planning?',0,'Establish the objectives and scope.','Determine the budget.','Select the team organizational model.','Determine project constraints.','option1','',1,'70'),(94,3,'While assessing your project processes, you have identified some uncontrolled process variations. Which of the following would be the appropriate chart you may use for this purpose?',0,'Pareto diagram','PERT chart','Control chart','HR personnel chart','option3','',1,'70'),(95,4,'Once the project is approved and moves into the planning stage, what happens in the next phase of the project life cycle?',0,'Agreements for risk sharing need to be concluded.','The total risk on the project typically reduces as activities are performed without loss.','Risks must be weighed against the potential benefit of the project’s success in order to decide if the project should be chosen.','Risks are identified with each major group of activities.','option4','',1,'70'),(96,5,'According to Bruce Tuckman’s five stages of team development, project team members compete for control at which stage?',0,'Forming','Storming','Norming','Performing','option2','',1,'70'),(97,6,'Under which of the following conditions would teams be more effective than individuals?',0,'When speed is important','When the activities involved in solving the problem are very detailed','When the actual document needs to be written','When innovation is required','option4','',1,'70'),(98,7,'Which of the following defines what tasks the project resources are expected to accomplish and, just as importantly, what is not part of the project team’s responsibilities?',0,'Punch list','Check sheet','Scope document','Project logic diagram','option3','',1,'70'),(99,8,' Fill in the blank. There is _______ correlation between project complexity and project risk.',0,'an unknown','a positive','no','a negative','option2','',1,'70'),(100,9,'A project budget estimate that is developed with the least amount of knowledge is known as which of the following?',0,'Rough order of magnitude (ROM) estimate','Scope of work estimate','Conceptual estimate','Line estimate','option3','',1,'70'),(101,10,'What is the first step in developing a risk management plan?',0,'Analyze the risks.','Estimate the likelihood of the risks occurring.','Identify potential project risks.','Develop a risk mitigation plan.','option3','',1,'70'),(102,1,'What type of computing technology refers to services and applications that typically run on a distributed network through virtualized resources?',0,'Distributed Computing','Cloud Computing','Soft Computing','Parallel Computing','option2','',5,'71'),(103,2,'Which one of the following options can be considered as the Cloud?',0,'Hadoop','Intranet','Web Applications','All of the mentioned','option1','',5,'71'),(104,3,'Cloud computing is a kind of abstraction which is based on the notion of combining physical resources and represents them as _______resources to users.',0,'Real','Cloud','Virtual','none of the mentioned','option3','',5,'71'),(105,4,'Which of the following has many features of that is now known as cloud computing?',0,'Web Service','Softwares','All of the mentioned','Internet','option4','',5,'71'),(106,5,'Which one of the following cloud concepts is related to sharing and pooling the resources?',0,'Polymorphism','Virtualization','Abstraction','None of the mentioned','option2','',5,'71');
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quiz_det`
--

DROP TABLE IF EXISTS `quiz_det`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quiz_det` (
  `quiz_id` int NOT NULL AUTO_INCREMENT,
  `q_title` text NOT NULL,
  `q_dept` text NOT NULL,
  `q_sem` text NOT NULL,
  `q_sub` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `q_batch` text NOT NULL,
  `q_date` text NOT NULL,
  `quiz_type` varchar(1) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL COMMENT '0-subjective,1-other',
  `q_timer` int DEFAULT NULL,
  `q_time_start` text NOT NULL,
  `q_time_end` text NOT NULL,
  `q_time_division` text CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `show_answer` int NOT NULL COMMENT '1-yes,0-no',
  `fac_inserted` text NOT NULL,
  `switch_limit` int NOT NULL,
  `desc_time` int DEFAULT NULL,
  `quiz_status` int DEFAULT NULL,
  `quiz_started` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`quiz_id`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quiz_det`
--

LOCK TABLES `quiz_det` WRITE;
/*!40000 ALTER TABLE `quiz_det` DISABLE KEYS */;
INSERT INTO `quiz_det` VALUES (64,'Testing-2','IT','5','','All','2021-11-07','1',0,'12:00','15:00','-',0,'222222',5,15,1,0),(68,'Testing-5','IT','5','','All','2021-12-10','1',0,'13:00','02:00','-',1,'222222',5,15,1,0),(69,'IA-3','IT','8','BIG DATA ANALYTICS','All','2022-02-28','0',0,'13:00','15:00','-',0,'220081',5,NULL,1,0),(70,'IA','IT','8','PROJECT MANAGEMENT','All','2022-03-05','0',0,'10:10','12:00','-',0,'220081',5,NULL,1,0),(71,'Cloud Computing','IT','8','','All','2022-03-07','1',0,'14:00','15:00','-',0,'220082',5,NULL,1,0);
/*!40000 ALTER TABLE `quiz_det` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `quiz_responses`
--

DROP TABLE IF EXISTS `quiz_responses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `quiz_responses` (
  `response_id` int NOT NULL AUTO_INCREMENT,
  `one_line_ans` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `selected_opt` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `desc_ans_name` varchar(250) DEFAULT NULL,
  `desc_ans_file` varchar(250) DEFAULT NULL,
  `ques_type` text NOT NULL,
  `quiz_start` text NOT NULL,
  `time_per_ques` text NOT NULL,
  `user_inserted` text NOT NULL,
  `ques_id` text NOT NULL,
  `quiz_id` text NOT NULL,
  PRIMARY KEY (`response_id`)
) ENGINE=InnoDB AUTO_INCREMENT=213 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quiz_responses`
--

LOCK TABLES `quiz_responses` WRITE;
/*!40000 ALTER TABLE `quiz_responses` DISABLE KEYS */;
INSERT INTO `quiz_responses` VALUES (89,NULL,'option2,option2,option1',NULL,NULL,'0,0,0','03:02:05','0:00:06,0:11:05,0:00:06','2220190371','64,63,65','54'),(90,NULL,'option1,option2',NULL,NULL,'0,0','13:02:34','0:00:10,0:00:23','2220190371','67,66','55'),(172,'2','option4,option3',NULL,NULL,'1,0,0','13:18:44','0:00:03,0:00:04,0:00:02','2220190371','75,84,81','64');
/*!40000 ALTER TABLE `quiz_responses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `score`
--

DROP TABLE IF EXISTS `score`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `score` (
  `score_id` int NOT NULL AUTO_INCREMENT,
  `user` text NOT NULL,
  `username` text,
  `roll` text,
  `user_score` text NOT NULL,
  `total_points` text NOT NULL,
  `ques_points` text NOT NULL,
  `total_time_taken` text,
  `time_submitted` text NOT NULL,
  `quiz_id` text NOT NULL,
  `quiz_attempted` text NOT NULL COMMENT '0-not attempted,\r\n1-attempted\r\n',
  `stud_img` text,
  `pending_chk` int NOT NULL,
  PRIMARY KEY (`score_id`)
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `score`
--

LOCK TABLES `score` WRITE;
/*!40000 ALTER TABLE `score` DISABLE KEYS */;
INSERT INTO `score` VALUES (102,'2220190371','BHAVYA MISTRY','33','7','12','5,2','00:00:07','00:53:23','64','1','/static/profile_pics/student_images/IT/Last-Year/semester_8/2220190371/2220190371.jpg',0),(126,'2220180163','KRISH DESAI','10','0','10','','00:00:34','10:50:02','70','1','/static/images/man.png',0);
/*!40000 ALTER TABLE `score` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `S_id` varchar(10) NOT NULL,
  `S_pass` text NOT NULL,
  `L_name` text NOT NULL,
  `F_name` text NOT NULL,
  `M_name` text NOT NULL,
  `roll` int NOT NULL,
  `batch` int NOT NULL,
  `S_email` text NOT NULL,
  `KT` int NOT NULL DEFAULT '0',
  `Type` int DEFAULT '0' COMMENT '0: For First Year, 1: for Direct Second year',
  `S_num` varchar(10) NOT NULL,
  `P_email` text NOT NULL,
  `P_num` varchar(10) NOT NULL,
  `current_sem` int NOT NULL,
  `image` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `gender` varchar(1) NOT NULL,
  `dept` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `electives` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `first_login` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`S_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES ('2220180163','$2b$12$j3OYiKRZnOqEKszWmLXdoOSQo1VgQwB309mW4VsUeTTsh3JUucjXi','DESAI','KRISH','TUSHAR',10,1,'krish.desai@somaiya.edu',0,0,'9619746376','krish_father@gmail.com','9819160674',8,'2220190371.png','M','IT','1UILC8041',1),('2220180274','$2b$12$E68TO0VwyCPP/SpAPiEtc.cPCymDoB/xjPGDIUnTXV7N3snG1eQF.','PAREKH','HET','NILESH',43,2,'het.parekh@somaiya.edu',0,0,'9619746376','het.father@gmail.com','9819160676',8,'','M','IT','1UILC8041',1),('2220190037','$2b$12$N./mJWKdFQflvqVON1wqw.JilIWEychfjkbZdWc4PynRPP6Z97ZC.','CHAPLOT','TEJAS','RAJENDRA',5,1,'tejas.chaplot@somaiya.edu',0,0,'7506438666','rajendra123@gmail.com','9819160676',6,'2220190037.jpg','M','IT','1UITDLC6052',1),('2220190371','$2b$12$209aK21v7zPaITX59.b1juhGRC3UqyPz/B0goe0KS5s2kOx55OkqW','MISTRY','BHAVYA','RAKESH',33,1,'bhavya.mistry@somaiya.edu',0,1,'9987263368','rakesh.mistry@gmail.com','9820331552',8,'2220190371.png','M','IT',NULL,0);
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subject` (
  `course_code` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `sub_name_long` text NOT NULL,
  `sub_name_short` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `sem` varchar(5) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `sub_type` int NOT NULL COMMENT '1-Theory,0-Practical',
  `is_elective` int NOT NULL DEFAULT '0' COMMENT '0-not Elective,1-elective',
  `elective_of` int NOT NULL DEFAULT '1' COMMENT '1-Compulsory, Else - elective',
  `marks` int NOT NULL COMMENT '1-Termtset marks 0-no marks',
  `dept_id` varchar(20) NOT NULL,
  PRIMARY KEY (`course_code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subject`
--

LOCK TABLES `subject` WRITE;
/*!40000 ALTER TABLE `subject` DISABLE KEYS */;
INSERT INTO `subject` VALUES ('1UITC301','APPLICATIONS OF MATHEMATICS IN ENGINEERING – I','AM-III','sem3',1,0,1,1,'ST2202'),('1UITC302','DATA STRUCTURES AND ANALYSIS','DSA','sem3',1,0,1,1,'ST2202'),('1UITC801','BIG DATA ANALYTICS','BDA','sem8',1,0,1,1,'ST2202'),('1UITL801','BIG DATA ANALYSIS LAB','BDA-LAB','sem8',0,0,1,0,'ST2202');
/*!40000 ALTER TABLE `subject` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-03-11 12:26:11
