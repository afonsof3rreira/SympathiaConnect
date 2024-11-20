import sys
import time
import os

def create_exp_folder(time_stamp):

    current_script_path = os.path.abspath(sys.argv[0])
    results_folder_path, current_script_path = os.path.split(current_script_path)
    results_folder_path = os.path.join(results_folder_path, "results")

    # Check if the folder does not exist already
    if not os.path.exists(results_folder_path):
        os.makedirs(results_folder_path)
        print(f"Folder '{results_folder_path}' created successfully.")
    else:
        print(f"Folder '{results_folder_path}' already exists.")

    time_str = time.strftime('%Y-%m-%d_%H-%M-%S', time_stamp)

    sub_folder_path = os.path.join(results_folder_path, time_str)

    # Check if the folder does not exist already
    if not os.path.exists(sub_folder_path):
        os.makedirs(sub_folder_path)

    return sub_folder_path, time_str


def clean_up_folders_in_root(root_folder: str):

    # Check if the root folder exists
    if os.path.exists(root_folder):

        # Traverse all directories and files in the root folder
        for folder_name in os.listdir(root_folder):
            folder_path = os.path.join(root_folder, folder_name)

            # Only process directories (skip files)
            if os.path.isdir(folder_path):

                # Check if the folder is empty
                if not os.listdir(folder_path):  # If the folder is empty
                    os.rmdir(folder_path)  # Remove the empty folder
                    print(f"Folder {folder_path} was empty and has been deleted.")

                else:
                    # Check if the x.csv file exists in the folder
                    csv_file = os.path.join(folder_path, f"{folder_name}.csv")

                    if os.path.exists(csv_file):
                        # Check if the csv file has less than 3 lines
                        with open(csv_file, 'r') as file:
                            lines = file.readlines()
                            if len(lines) < 3:
                                # Delete the folder and the file if the csv has less than 3 lines
                                os.remove(csv_file)  # Remove the csv file
                                os.rmdir(folder_path)  # Remove the folder
                                print(f"Folder {folder_path} and its contents have been deleted (csv file had less than 3 lines).")

                    else:
                        print(f"{csv_file} does not exist inside the folder.")
    else:
        print(f"Root folder {root_folder} does not exist.")


def clean_up_folder(folder_path: str, file_path):
    print("CLEAN UP WAS CALLED")

    # Check if the folder exists
    if os.path.exists(folder_path):

        # Check if the folder is empty
        if not os.listdir(folder_path):  # If the folder is empty
            os.rmdir(folder_path)  # Remove the empty folder
            print(f"Folder {folder_path} was empty and has been deleted.")

        else:

            # Check if the csv file has less than 3 lines
            with open(file_path, 'r') as file:
                lines = file.readlines()

                if len(lines) < 3:
                    # Delete the folder and the file if the csv has less than 3 lines
                    os.remove(file_path)  # Remove the csv file
                    os.rmdir(folder_path)  # Remove the folder
                    print(
                        f"Folder {folder_path} and its contents have been deleted (csv file had less than 3 lines).")
    else:
        print(f"Folder {folder_path} does not exist.")
