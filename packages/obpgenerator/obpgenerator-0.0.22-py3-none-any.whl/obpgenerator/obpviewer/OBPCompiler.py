# Compiler and Decompiler or OBP and OBPJ files
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import json
import ntpath
import obplib.PacketHandler as PacketHandler
import obplib.FileHandler as FileHandler
import os

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Function which converts OBP files to OBPJ file - Decompiling
def convert_OBP_to_OBPJ(filename):
    f0 = filename
    f1 = f0[:-4] + ".obpj"
    print("Decompiling {0} into {1}...".format(f0, f1))
    blob = FileHandler.read_obp(f0)
    if os.path.isfile(f1):
        print(
            "A file named {0} already exists. Would you like to overwrite it? [Y/N]".format(
                f1
            )
        )
        choice = input().lower()
        if choice == "y":
            FileHandler.write_obpj(blob, f1)
        else:
            pass
    elif not os.path.isfile(f1):
        FileHandler.write_obpj(blob, f1)
    
 
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Function that converts OBPJ files to OBP files - Compiling 
def convert_OBPJ_to_OBP(filename):
    f0 = filename
    f1 = f0[:-5] + ".obp"
    print("Compiling {0} into {1}...".format(f0, f1))
    blob = FileHandler.get_segment_from_dict(f0)
    if os.path.isfile(f1):
        print(
            "A file named {0} already exists. Would you like to overwrite it? [Y/N]".format(
                f1
            )
        )
        choice = input().lower()
        if choice == "y":
            FileHandler.write_obp(blob, f1)
        else:
            pass
    elif not os.path.isfile(f1):
        FileHandler.write_obp(blob, f1)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Main section
if __name__ == '__main__':
    file_name=input('Name of file: ')

    if file_name.endswith('.obp'):
        convert_OBP_to_OBPJ(file_name)
    elif file_name.endswith('.obpj'):
        convert_OBPJ_to_OBP(file_name)
    else:
        print('Please choose a correct file')
    
