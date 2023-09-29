# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 10:22:56 2023

@author: Ross James

Script for calling in to submit jobs.
The script will creat a directory from the base name of the job,
move the associated files to that directory and then submit them.

Usage:
    
from job_submitter import JobSubmitter
    
job_submitter = JobSubmitter()
job_submitter.submit_job(["path/to/your/task.sh"], additional_ext: list else None)

╭╮╱╭┳━━━┳━━━╮╱╱╭━━━╮╱╱╭╮╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╭━━━━╮╱╱╱╱╭╮
┃┃╱┃┃╭━╮┃╭━╮┃╱╱┃╭━╮┃╱╱┃┃╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱┃╭╮╭╮┃╱╱╱╱┃┃
┃╰━╯┃╰━╯┃┃╱╰╯╱╱┃╰━━┳╮╭┫╰━┳╮╭┳┳━━┳━━┳┳━━┳━╮╱╱╰╯┃┃┣┻━┳━━┫┃╭━━╮
┃╭━╮┃╭━━┫┃╱╭┳━━╋━━╮┃┃┃┃╭╮┃╰╯┣┫━━┫━━╋┫╭╮┃╭╮┳━━╮┃┃┃╭╮┃╭╮┃┃┃━━┫
┃┃╱┃┃┃╱╱┃╰━╯┣━━┫╰━╯┃╰╯┃╰╯┃┃┃┃┣━━┣━━┃┃╰╯┃┃┃┣━━╯┃┃┃╰╯┃╰╯┃╰╋━━┃
╰╯╱╰┻╯╱╱╰━━━╯╱╱╰━━━┻━━┻━━┻┻┻┻┻━━┻━━┻┻━━┻╯╰╯╱╱╱╰╯╰━━┻━━┻━┻━━╯
"""

import os
import pathlib
import shutil

class JobSubmitter:
    def __init__(self):
        self.submitted = 0
        self.i = 0
        self.extensions = [".inp", 
                           ".sh", 
                           ".out", 
                           ".opt", 
                           "_original.opt", 
                           "_original.out", 
                           ".xyz"]

    def submit_jobs(self, tasks: list, additional_ext = None):
        
        if additional_ext != None:
            self.extensions = self.extensions + additional_ext
        
        for task in tasks:
            task_path = pathlib.Path(task)
            name = task_path.stem.replace(".sh", "")
            stripped_name = name
            

            cdir = os.path.abspath(".")
            folder = task_path.parent

            os.chdir(folder)
            stripped_folder = os.path.join(folder, stripped_name)
            os.makedirs(stripped_folder, exist_ok=True)

            for ext in self.extensions:
                source = f"{name}{ext}"
                if os.path.exists(source):
                    shutil.move(source, os.path.join(stripped_folder, source))

            os.chdir(stripped_folder)
            os.system(f"sbatch {name}.sh")
            os.chdir(cdir)

            self.submitted += 1
            self.i += 1
            print(f"{self.i} Jobs have been submitted\n")