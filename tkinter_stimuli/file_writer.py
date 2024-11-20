import json
import os
import queue
import threading
import time


class file_writer():

    def __init__(self):

        # Global variables
        self.file_path = None
        self.start_time = time.time()  # Record the start time of the program
        self.timestamps = []  # List to store the timestamps
        self.timestamps_queue = queue.Queue()  # Queue to handle timestamps

    def format_timestamp(self, ts):
        return time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(ts))

    def create_initial_file(self, custom_folder_path=None):

        start_time = time.time()
        if custom_folder_path is None:
            folder_path = os.path.join(os.path.dirname(__file__), "results", self.format_timestamp(start_time))

        if not os.path.exists(custom_folder_path):
            os.mkdir(custom_folder_path)

        self.file_path = os.path.join(custom_folder_path, "experiment_log.txt")

        """Experiment layout:
        
        Thoughts...:
            T1 can be done without having to wait for anything because we are just evaluating motion artifacts
            T5 and T4 are the most physically demanding tests, therefore, to reduce the waiting periods (and allow for stabilization of the EDA signal, we should let them at the end)
        
        Suggested sequence:
        
            15 mins - Initial period at rest (with nature scene and headphones)
            
            T1 - repetition #1
            1 min
            T1 - repetition #2
            1 min
            T1 - repetition #3
            1 min
            T1 - repetition #4
            
            3 mins - waiting period with nature scene and headphones
            
            T2 - Level 1
            T2 - Level 2
            T2 - Level 3
            T2 - Level 4

            3 mins - waiting period with nature scene and headphones

            T3 - Level 1
            T3 - Level 2
            T3 - Level 3
            T3 - Level 4
            T3 - Level 5
            T3 - Level 6
             
            3 mins - waiting period with nature scene and headphones
            
            T4 - repetition #1
            1 min waiting period
            
            T4 - repetition #2
            1 min waiting period

            T4 - repetition #3
            
            3 mins - waiting period with nature scene and headphones

            THIS ONE DEPENDS ON THE BREATHING SEQUENCE

        """
        # TODO: DECIDE THE BREATHING SEQUENCE FOR T4
        # TODO: DECIDE IF THE HAND-GRIP IS GOING TO BE MONITORED BY AN EXTERNAL SENSOR

        """
        Test type:
            Test 1 (T1): Body movement - motion artifact assessment
            Test 2 (T2): Stroop test - cognitive overload / attention
            Test 3 (T3): Maths test - cognitive overload / attention
            Test 4 (T5): Hand-grip test - SNS elicitation
            Test 5 (T4): Deep breath - SNS elicitation;
        
        Level:
            T1:
                1: lifting left arm
                2: lifting left leg
                3: lifting right arm
                4: lifting right leg
            T2:
                1: Select one of two words that match the word at the center
                2: Select from two text that match the font color of the word at the center
                3: Select one of two squares that match the word at the center
                4: Select one of two squares that match the font color of the word at the center
            T3:
                1: Summation of any two 1-digit numbers
                2: Summation of any 1-digit number with any 2-digit number
                3: Summation of any 2-digit number with any 2-digit number
                4: Summation of any 2-digit number with any 3-digit number
                5: Summation of any 3-digit number with any 3-digit number
                6: Summation of any 4-digit number with any 4-digit number (we use this to cover any person that might be really good at maths)

            T4: (ignored)
            T5: (ignored)
        
        Action:
            T1:
                1: Start of the session
                2: Start of the new level
                3: Start of the limb-lift
                4: Middle of the limb-lift
                5: End of the limb-lift
                6: End of the session
                
                Notes for in-between periods:
                    1,2 = in between 1,2 is training period
                    3,4 = raising the limb
                    4,5 = lowering the limb
                    4,2 = at-rest period
            
            T2 / T3: 
                1: Start of the session
                2: Start of the new level
                3: Presented a new sample
                4: Correct option selected
                5: Wrong option selected
                6: End of the session
                
                Notes for in-between periods: 
                1,2 = in between 1,2 is training period 
                3,4 = person's processing time 
                3,5 = person's processing time 3,5,5,4,3 (example): the person tried the wrong option twice before 
                chOosing the correct option, after which the new sample is presented. This example highlights the rule 
                in which a new sample can only be presented after the person obtains the correct answer.
            
            T4:
                ????
            T5: 
                ????
            
        """

        # Create an empty JSON file with start time
        with open(self.file_path, mode='a') as file:
            file.write("# Experiment log file\n")
            file.write("# Labels: Timestamp, Text input\n")

            # file.write("# Labels: Test (1, 2, 3, 4, 5), Level (1,...,L), Repetition No. (1,...,R), Action (1,"
            #            "...,A), Timestamp" + "\n")


            # file.write("Test" + "\t" + "Level" + "\t" + "Repetition" + "\t" + "Action" + "\t" + "Timestamp" + "\t" + "\n")

    def add_user_ID(self, user_id):
        with open(self.file_path, mode='a') as file:
            file.write("# {\"user_ID\":" + user_id + "}" + "\n")

    def add_user_anthropometric_data(self, anthropometric_data):

        # Serialize data to a single-line JSON string
        json_str = json.dumps(anthropometric_data, separators=(',', ':'))

        # Write the JSON string to a text file
        with open(self.file_path, mode='a') as file:
            file.write("# " + json_str + '\n')

    def add_timestamps(self, action, timestamp):

        entry = (action, self.format_timestamp(timestamp))

        # Add the entry to the queue
        self.timestamps_queue.put(entry)

    def save_timestamps(self):

        while True:

            try:

                # Get timestamp from the queue
                action, timestamp = self.timestamps_queue.get(timeout=1)

                msg_str = timestamp + "\t" + action + "\t"

                print(action)

                with open(self.file_path, mode='a') as file:
                    file.write(msg_str + "\n")

            except queue.Empty:
                continue