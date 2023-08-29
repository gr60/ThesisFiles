# ThesisFiles
Application Directories:

    /data/patient_data: Stores patient data including exams, patient records, prescriptions, and previous diseases that are imported into the CDSS.

    /inference_engine: Contains inference engine-related components.

        config: Defines constants for the database (DB) name and ontology version.

        main: Responsible for creating the DB, inserting patient data, checking for inappropriate medications, suggesting alternative prescriptions, and rescheduling drugs.

        ie_beers_criteria_interactions: Integrates patient data with the ontology and Pellet reasoner using lib owlready2. Retrieves results from the reasoner using SPARQL queries and stores them in the CDSS DB.

        ie_smt_alternative_solver: Selects prescription drugs and their alternatives from the CDSS DB and inputs them into the Alternative solver (z3_alternativeDrug). Retrieves results from the solver and stores them in the CDSS DB.

        ie_smt_rescheduling_solver: Selects drug interactions, frequency, and timing information from the CDSS DB. Retrieves Tmax values from the ontology. Inputs this data into the rescheduling solver (z3_scheduling). Stores solver results in the CDSS DB.

        z3_alternativeDrug: Receives data from ie_smt_alternative_solver. Constructs a Z3 model to check for prescriptions without inappropriate drugs. Returns the result to ie_smt_alternative_solver.

        z3_scheduling: Receives data from ie_smt_rescheduling_solver. Constructs a Z3 model to reschedule drugs to maximize the distance between Tmax values.

Other Directories:

    Import_files: Auxiliary file for importing patient data.

    result_queries: Executes queries on the CDSS DB to collect results and saves them in XLS files in the /results/CDSS directory.

    /inference_engine/Util: Contains auxiliary files for the CDSS DB.

    /inference_engine/ontology_files: Stores ontology files, including the Beers Criteria ontology and patient data ontologies.

    /results/CDSS: Stores results obtained from result_queries.
