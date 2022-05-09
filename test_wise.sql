-- MySQL dump 10.13  Distrib 8.0.27, for Linux (x86_64)
--
-- Host: localhost    Database: quicky
-- ------------------------------------------------------
-- Server version	8.0.27-0ubuntu0.20.04.1

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
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `F_id` int NOT NULL,
  `L_name` text NOT NULL,
  `F_name` text NOT NULL,
  `M_name` text NOT NULL,
  `F_email` text NOT NULL,
  `F_password` text NOT NULL,
  `dept` text NOT NULL,
  `F_num` varchar(10) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `img` text NOT NULL,
  PRIMARY KEY (`F_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES (220081,'Shah','Nasim','Banu','nshah@somaiya.edu','32145678','Information Technology','9821154828','F','https://www.kjsieit.in/sims/images/facdp/1609156302Nasim-Photo.jpg'),(222222,'Kotecha','Radhika','Nikhil','radhika.kotecha@somaiya.edu','32145678','Information Technology','7698558637','F','https://www.kjsieit.in/sims/images/facdp/1596654541radhika.jpg');
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
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (59,1,'1+1=?',0,'1','2','3','-','option2','',1,'51'),(60,2,'2+2=?',0,'2','6','4','8','option3','',2,'51'),(61,3,'4+4=?',1,NULL,NULL,NULL,NULL,NULL,'',2,'51'),(62,1,'1+1=?',0,'2','3','4','5','option1','00:30:00',1,'53'),(69,1,'1+1=?',0,'1','2','4','3','option2','',1,'56'),(70,2,'2+2=?',0,'5','6','4','5','option3','00:30:00',5,'53'),(71,1,'1+1=?',1,NULL,NULL,NULL,NULL,NULL,'',1,'63'),(72,1,'1+1=?',1,NULL,NULL,NULL,NULL,NULL,'',1,'63'),(75,1,'1+1=?',1,NULL,NULL,NULL,NULL,NULL,'',1,'64'),(81,2,'2+2=?',0,'2','6','4','-','option3','',2,'64'),(82,3,'3+3=?',0,'3','4','5','6','option4','',2,'64'),(83,4,'4+4=?',0,'5','6','8','-','option3','',2,'64'),(84,5,'5*5=?',0,'10','20','30','25','option4','',2,'64'),(86,1,'1+1=?',0,'2','4','6','-','option1','',1,'68'),(87,2,'2+2=?',1,NULL,NULL,NULL,NULL,NULL,'',2,'68');
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
  `desc_time` int NOT NULL,
  `quiz_status` int DEFAULT NULL,
  `quiz_started` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`quiz_id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quiz_det`
--

LOCK TABLES `quiz_det` WRITE;
/*!40000 ALTER TABLE `quiz_det` DISABLE KEYS */;
INSERT INTO `quiz_det` VALUES (51,'Exam1','IT','6','','All','2021-05-22','1',0,'15:00','15:30','-',1,'220081',0,0,1,0),(53,'Exam2','IT','5','','All','2021-12-17','1',1,'03:59','05:00','-',1,'220081',5,0,1,1),(64,'Testing-2','IT','5','','All','2021-11-07','1',0,'12:00','15:00','-',0,'222222',5,15,1,0),(68,'Testing-5','IT','5','','All','2021-12-10','1',0,'09:35','10:00','-',1,'222222',5,15,1,0);
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
) ENGINE=InnoDB AUTO_INCREMENT=173 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `quiz_responses`
--

LOCK TABLES `quiz_responses` WRITE;
/*!40000 ALTER TABLE `quiz_responses` DISABLE KEYS */;
INSERT INTO `quiz_responses` VALUES (78,'8','option3,option2',NULL,NULL,'1,0,0','15:50:42','0:00:04,0:00:04,0:00:05','2220190371','61,60,59','51'),(89,NULL,'option2,option2,option1',NULL,NULL,'0,0,0','03:02:05','0:00:06,0:11:05,0:00:06','2220190371','64,63,65','54'),(90,NULL,'option1,option2',NULL,NULL,'0,0','13:02:34','0:00:10,0:00:23','2220190371','67,66','55'),(172,'2','option4,option3',NULL,NULL,'1,0,0','13:18:44','0:00:03,0:00:04,0:00:02','2220190371','75,84,81','64');
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
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `score`
--

LOCK TABLES `score` WRITE;
/*!40000 ALTER TABLE `score` DISABLE KEYS */;
INSERT INTO `score` VALUES (57,'2220190371','BHAVYA MISTRY','33','3','5','0,2,1','00:00:13','15:50:55','51','1','https://www.kjsieit.in/sims/images/studentdp/1596348948BHAVYA MISTRY PHOTO.jpg',1),(62,'2220190371','BHAVYA MISTRY','33','3','3','1,1,1','00:11:17','03:13:22','54','1','https://www.kjsieit.in/sims/images/studentdp/1596348948BHAVYA MISTRY PHOTO.jpg',0),(63,'2220190371','BHAVYA MISTRY','33','2','2','1,1','00:00:33','13:03:07','55','1','https://www.kjsieit.in/sims/images/studentdp/1596348948BHAVYA MISTRY PHOTO.jpg',0),(64,'2220190371','BHAVYA MISTRY','33','0','1','','00:00:45','10:17:26','56','1','https://www.kjsieit.in/sims/images/studentdp/1596348948BHAVYA MISTRY PHOTO.jpg',0),(90,'2220190371','BHAVYA MISTRY','33','5','9','1.0,2.0,2.0','00:00:09','13:18:53','64','1','/static/images/man.png',0);
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
  `KT` int NOT NULL,
  `Type` int DEFAULT NULL COMMENT '0: For First Year, 1: for Direct Second year',
  `S_num` varchar(10) NOT NULL,
  `P_email` text NOT NULL,
  `P_num` varchar(10) NOT NULL,
  `current_sem` int NOT NULL,
  `image` text NOT NULL,
  `gender` varchar(1) NOT NULL,
  `dept` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `elective1` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `elective2` text CHARACTER SET latin1 COLLATE latin1_swedish_ci,
  `first_login` int default 0,
  PRIMARY KEY (`S_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES ('2220180163','12345678','DESAI','KRISH','TUSHAR',10,1,'krish.desai@somaiya.edu',0,0,'9619746376','','',5,'','M','IT','',''),('2220180274','12345678','PAREKH','HET','NILESH',43,1,'het.parekh@somaiya.edu',0,0,'9619746376','','',5,'','M','IT','',''),('2220190037','9819160674','CHAPLOT','TEJAS','RAJENDRA',5,1,'tejas.chaplot@somaiya.edu',0,NULL,'7506438666','rajendra123@gmail.com','9819160674',5,'anti_ragging.png','M','IT',NULL,NULL),('2220190371','12345678','MISTRY','BHAVYA','RAKESH',33,2,'bhavya.mistry@somaiya.edu',0,0,'9987263368','rakesh.mistry1974@gmail.com','9820331552',5,'https://www.kjsieit.in/sims/images/studentdp/1596348948BHAVYA%20MISTRY%20PHOTO.jpg','M','IT','',''),('2220190372','12345678','PATEL','YASH','NILESH',45,2,'patel.yn@somaiya.edu',0,0,'9987263368','','',5,'','M','IT','','');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subject` (
  `u_key` int NOT NULL AUTO_INCREMENT,
  `sub_name` varchar(20) NOT NULL,
  `subject_name` varchar(30) NOT NULL,
  `sem` varchar(20) NOT NULL,
  `F_id` int NOT NULL,
  `year` int NOT NULL,
  `sub_type` int NOT NULL COMMENT '1-Theory,0-Practical',
  `is_elective` int NOT NULL COMMENT '0-not Elective,1-elective',
  `elective_of` int NOT NULL COMMENT '1-Normal,2-Department,3-Institute',
  `marks` int NOT NULL COMMENT '1-Termtset marks 0-no marks',
  `dept_id` varchar(20) NOT NULL,
  PRIMARY KEY (`u_key`)
) ENGINE=InnoDB AUTO_INCREMENT=148 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subject`
--

LOCK TABLES `subject` WRITE;
/*!40000 ALTER TABLE `subject` DISABLE KEYS */;
INSERT INTO `subject` VALUES (1,'ITC301','AM3','sem3',0,0,1,0,1,1,'ST2202'),(2,'ITC302','LD','sem3',0,0,1,0,1,1,'ST2202'),(3,'ITC303','DSA','sem3',0,0,1,0,1,1,'ST2202'),(4,'ITC304','DBMS','sem3',0,0,1,0,1,1,'ST2202'),(5,'ITC305','PCOM','sem3',0,0,1,0,1,1,'ST2202'),(6,'TNP3','TNP3','sem3',0,0,1,0,1,0,'ST2202'),(7,'ITL301','DDL','sem3',0,0,0,0,1,0,'ST2202'),(8,'ITL302','DSL','sem3',0,0,0,0,1,0,'ST2202'),(9,'ITL303','SQLL','sem3',0,0,0,0,1,0,'ST2202'),(10,'ITL304','JAVA','sem3',0,0,0,0,1,0,'ST2202'),(11,'pcomtut','pcomtut','sem3',0,0,0,0,1,0,'ST2202'),(12,'ITC401','AM4','sem4',0,0,1,0,1,1,'ST2202'),(13,'ITC402','CN','sem4',0,0,1,0,1,1,'ST2202'),(14,'ITC403','OS','sem4',0,0,1,0,1,1,'ST2202'),(15,'ITC404','COA','sem4',0,0,1,0,1,1,'ST2202'),(16,'ITC405','AT','sem4',0,0,1,0,1,1,'ST2202'),(17,'TNP4','TNP4','sem4',0,0,1,0,1,0,'ST2202'),(18,'ITL401','NL','sem4',0,0,0,0,1,0,'ST2202'),(19,'ITL402','UL','sem4',0,0,0,0,1,0,'ST2202'),(20,'ITL403','MPL','sem4',0,0,0,0,1,0,'ST2202'),(21,'ITL404','PYTHON','sem4',0,0,0,0,1,0,'ST2202'),(22,'ATT','ATT','sem4',0,0,0,0,1,0,'ST2202'),(23,'ITC501','MEP','sem5',0,0,1,0,1,1,'ST2202'),(24,'ITC502','INP','sem5',0,0,1,0,1,1,'ST2202'),(25,'ITC503','ADMT','sem5',0,0,1,0,1,1,'ST2202'),(26,'ITC504','CNS','sem5',0,0,1,0,1,1,'ST2202'),(27,'ITDLO5011','ADSA','sem5',0,0,1,1,2,1,'ST2202'),(28,'ITDLO5012','IP','sem5',0,0,1,0,1,1,'ST2202'),(29,'ITDLO5013','ECOMM','sem5',0,0,1,1,2,1,'ST2202'),(30,'ITDLO5014','ITES','sem5',0,0,1,1,2,1,'ST2202'),(31,'ITDLO5015','CGVR','sem5',0,0,1,1,2,1,'ST2202'),(32,'TNP5','TNP5','sem5',0,0,1,0,1,0,'ST2202'),(33,'ITL501','INPL','sem5',0,0,0,0,1,0,'ST2202'),(34,'ITL502','SEC','sem5',0,0,0,0,1,0,'ST2202'),(35,'ITL503','OLAP','sem5',0,0,0,0,1,0,'ST2202'),(36,'ITL504','IOT','sem5',0,0,0,0,1,0,'ST2202'),(37,'ITL505','BCEP','sem5',0,0,0,0,1,0,'ST2202'),(38,'ITC601','SEPM','sem6',7,2017,1,0,1,1,'ST2202'),(39,'ITC602','DMBI','sem6',6,2017,1,0,1,1,'ST2202'),(40,'ITC603','CCS','sem6',5,2017,1,0,1,1,'ST2202'),(41,'ITC604','WN','sem6',1,2017,1,0,1,1,'ST2202'),(42,'ITDLO6021','AINP','sem6',0,0,1,1,2,1,'ST2202'),(43,'ITDLO6022','SA','sem6',0,0,1,1,2,1,'ST2202'),(44,'ITDLO6023','DF','sem6',4,2017,1,1,2,1,'ST2202'),(45,'ITDLO6024','MS','sem6',0,0,1,1,2,1,'ST2202'),(46,'ITDLO6025','GI','sem6',2,2017,1,1,2,1,'ST2202'),(47,'TNP6','TNP6','sem6',9,2017,1,0,1,0,'ST2202'),(48,'ITL601','SDL','sem6',0,0,0,0,1,0,'ST2202'),(49,'ITL602','BIL','sem6',0,0,0,0,1,0,'ST2202'),(50,'ITL603','CSDL','sem6',0,0,0,0,1,0,'ST2202'),(51,'ITL604','SNL','sem6',0,0,0,0,1,0,'ST2202'),(52,'ITL605','MiPr','sem6',0,0,0,0,1,0,'ST2202'),(53,'ITC701','ENDS','sem7',0,0,1,0,1,1,'ST2202'),(54,'ITC702','INFS','sem7',0,0,1,0,1,1,'ST2202'),(55,'ITC703','AI','sem7',0,0,1,0,1,1,'ST2202'),(56,'ITDLO7031','SAN','sem7',0,0,1,1,2,1,'ST2202'),(57,'ITDLO7032','MAD','sem7',0,0,1,1,2,1,'ST2202'),(58,'ITDLO7033','HPC','sem7',0,0,1,1,2,1,'ST2202'),(59,'ITDLO7034','STQA','sem7',0,0,1,1,2,1,'ST2202'),(60,'ITDLO7035','SC','sem7',0,0,1,1,2,1,'ST2202'),(61,'INST1','PLM','sem7',0,0,1,1,3,1,'ST2202'),(62,'INST2','RE','sem7',0,0,1,1,3,1,'ST2202'),(63,'TNP7','TNP7','sem7',0,0,1,0,1,0,'ST2202'),(64,'ITL701','NDL','sem7',0,0,0,0,1,0,'ST2202'),(65,'ITL702','ASL','sem7',0,0,0,0,1,0,'ST2202'),(66,'ITL703','ISL','sem7',0,0,0,0,1,0,'ST2202'),(67,'ITL704','AADL','sem7',0,0,0,0,1,0,'ST2202'),(68,'ITL705','Pro1','sem7',0,0,0,0,1,0,'ST2202'),(69,'ITC801','BDA','sem8',0,0,1,0,1,1,'ST2202'),(70,'ITC802','IOE','sem8',8,2016,1,0,1,1,'ST2202'),(71,'ITDLO8041','UID','sem8',0,0,1,1,2,1,'ST2202'),(72,'ITDLO8042','IRS','sem8',0,0,1,1,2,1,'ST2202'),(73,'ITDLO8043','KM','sem8',0,0,1,1,2,1,'ST2202'),(74,'ITDLO8044','ROB','sem8',0,0,1,1,2,1,'ST2202'),(75,'ITDLO8045','ERP','sem8',0,0,1,1,2,1,'ST2202'),(76,'INST1','PM','sem8',0,0,1,1,3,1,'ST2202'),(77,'INST2','FM','sem8',0,0,1,1,3,1,'ST2202'),(78,'TNP8','TNP8','sem8',0,0,1,0,1,0,'ST2202'),(79,'ITL801','BDL','sem8',0,0,0,0,1,0,'ST2202'),(80,'ITL802','IOEL','sem8',0,0,0,0,1,0,'ST2202'),(81,'ITL803','DOL','sem8',0,0,0,0,1,0,'ST2202'),(82,'ITL804','RL','sem8',0,0,0,0,1,0,'ST2202'),(83,'ITL805','Pro2','sem8',0,0,0,0,1,0,'ST2202'),(84,'INST3','MIS','sem7',0,0,1,1,3,1,'ST2202'),(85,'INST4','DOE','sem7',0,0,1,1,3,1,'ST2202'),(86,'INST5','CSL','sem7',0,0,1,1,3,1,'ST2202'),(87,'INST6','DMMM','sem7',0,0,1,1,3,1,'ST2202'),(88,'INST7','EAM','sem7',0,0,1,1,3,1,'ST2202'),(89,'DE','DMMM','sem7',0,0,1,1,3,1,'ST2202'),(90,'INST3','EDM','sem8',0,0,1,1,3,1,'ST2202'),(91,'INST4','HRM','sem8',0,0,1,1,3,1,'ST2202'),(92,'INST5','PECSR','sem8',0,0,1,1,3,1,'ST2202'),(93,'INST6','RM','sem8',0,0,1,1,3,1,'ST2202'),(145,'INST7','IPRAP','sem8',0,0,1,1,3,1,'ST2202'),(146,'INST8','DBM','sem8',0,0,1,1,3,1,'ST2202'),(147,'INST9','EM','sem8',0,0,1,1,3,1,'ST2202');
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

-- Dump completed on 2022-01-12 19:41:48
