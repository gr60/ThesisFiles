import sqlite3
from config import DBNAME


def resetDB():
    conn = sqlite3.connect(DBNAME, timeout=10)

    c = conn.cursor()

    #Check interaction
    c.execute("DROP TABLE IF EXISTS DRUG_DRUG_INTERACTION")
    c.execute("DROP TABLE IF EXISTS PRESC_INTERACTION")
    c.execute("DROP TABLE IF EXISTS DRUG_ALTERNATIVE")
    c.execute("DROP TABLE IF EXISTS PRESCRIPTION_PROCESSED")

    #Check alternative
    c.execute("DROP TABLE IF EXISTS PRESCRIPTION_MODELS")
    c.execute("DROP TABLE IF EXISTS TIMEOUT_PRESCRIPTIONS")

    #Check reschedule
    c.execute("DROP TABLE IF EXISTS PRESCRIPTION_RESCHEDULED")
    
    #Auxiliar tables
    c.execute("DROP TABLE IF EXISTS PRESCRIPTION")
    c.execute("DROP TABLE IF EXISTS PATIENT")
    c.execute("DROP TABLE IF EXISTS PATIENT_EXAMS")
    c.execute("DROP TABLE IF EXISTS PATIENT_PREVIOUS_DISEASES")


    #Check interaction

    table = """ CREATE TABLE IF NOT EXISTS PRESCRIPTION_PROCESSED (
                CD_PATIENT VARCHAR(255),
                CD_PRESCRIPTION VARCHAR(255)
            ); """

    c.execute(table)


    #Check interaction
    table = """ CREATE TABLE IF NOT EXISTS PRESC_INTERACTION (
                CD_PATIENT VARCHAR(255) ,
                CD_PRESCRIPTION VARCHAR(255),
                DRUG VARCHAR(255),
                INTER_DRUG_NUM INT,
                INTERACTION1 VARCHAR(255),
                INTERACTION2 VARCHAR(255),
                INTERACTION3 VARCHAR(255),
                INTERACTION4 VARCHAR(255),
                QOE VARCHAR(255),
                SOR VARCHAR(255),
                DETAIL VARCHAR(500),
                RECOMMENDATION VARCHAR(500),
                ALTERNATIVE CHAR(3)
                
            ); """
    c.execute(table)

    #Check interaction
    table = """ CREATE TABLE IF NOT EXISTS DRUG_DRUG_INTERACTION (
                CD_PATIENT VARCHAR(255) ,
                CD_PRESCRIPTION VARCHAR(255),
                DRUG1 VARCHAR(255),
                DRUG2 VARCHAR(255)
            ); """
    c.execute(table)


    #Check interaction
    table = """ CREATE TABLE IF NOT EXISTS DRUG_ALTERNATIVE (
                CD_PATIENT VARCHAR(255) ,
                CD_PRESCRIPTION VARCHAR(255),
                DRUG VARCHAR(255),
                ALTERNATIVE VARCHAR(255)
            ); """
    c.execute(table)

    #Check alternative
    table = """ CREATE TABLE IF NOT EXISTS PRESCRIPTION_MODELS (
                CD_PATIENT VARCHAR(255) ,
                CD_PRESCRIPTION VARCHAR(255),
                MODEL VARCHAR(255)
            ); """
    c.execute(table)

    #Check alternative
    table = """ CREATE TABLE IF NOT EXISTS TIMEOUT_PRESCRIPTIONS (
                CD_PATIENT VARCHAR(255),
                CD_PRESCRIPTION VARCHAR(255)
                
            ); """
    c.execute(table)


    #Check rescheduling
    table = """ CREATE TABLE IF NOT EXISTS PRESCRIPTION_RESCHEDULED (
                CD_PATIENT VARCHAR(255) ,
                CD_PRESCRIPTION VARCHAR(255),
                SAT  VARCHAR(255),
                MODEL VARCHAR(255)
            ); """

    c.execute(table)




    table = """ CREATE TABLE IF NOT EXISTS PATIENT (
                CD_PATIENT VARCHAR(255) ,
                AGE VARCHAR(255),
                GENDER VARCHAR(255),
                DT_Admission VARCHAR(255),
                DT_discharge VARCHAR(255),
                CLINIC VARCHAR(255),
                discharge_reason VARCHAR(255),
                MAIN_PROCEDURE VARCHAR(255),
                CID  VARCHAR(255)
            ); """

    c.execute(table)

    table = """ CREATE TABLE IF NOT EXISTS PATIENT_EXAMS (
                CD_PATIENT VARCHAR(255) ,
                seq_Result VARCHAR(255),
                nm_Exam VARCHAR(255),
                qt_Result VARCHAR(255),
                dt_Result VARCHAR(255)
            ); """

    c.execute(table)

    table = """ CREATE TABLE IF NOT EXISTS PATIENT_PREVIOUS_DISEASES (
                CD_PATIENT VARCHAR(255) ,
                nm_Disease VARCHAR(255)
            ); """

    c.execute(table)


    table = """ CREATE TABLE IF NOT EXISTS PRESCRIPTION (
                CD_PATIENT VARCHAR(255),
                CD_PRESCRIPTION VARCHAR(255),
                DRUG VARCHAR(255),
                DOSE VARCHAR(255),
                FREQUENCY VARCHAR(255),
                SCHEDULE VARCHAR(255),
                START_DATE VARCHAR(255),
                END_DATE VARCHAR(255),
                FIXEDTIME VARCHAR(255),
                DS_INTERVAL VARCHAR(255),
                TYPE_DRUG VARCHAR(255),
                DRUG_UNIT VARCHAR(255),
                DS_DRUG_ORIGINAL VARCHAR(255),
                Drug_Lenght VARCHAR(255),
                ROUTE VARCHAR(255),
                composeName VARCHAR(255),
                presc_day VARCHAR(255),
                CRITICAL_PATIENT,
                FIRST_LINE,
                RELEASE
            ); """

    c.execute(table)

    conn.commit()
    conn.close()