# HPC_Submission_Tools

Repo for tools to help with slurm submission and management within ARCHIE-WeST HPC cluster

## Install

From cloning repo

```
git clone https://www.github.com/RossJamesUrquhart/HPC_submission_tools
pip install .
```

From PyPi

```
pip install HPC-submission-tools
```

## Usage

```
from HPC_submission_tools import JobSubmitter
JobSubmitter = JobSubmitter()

JobSubmitter.submit_jobs([path/to/sbatch/files], additional_ext=None)

```

The ```additional_ext``` keyword will take a list of any extensions not already considered by the script to search for those to mvoe alongside the sbatch files.
