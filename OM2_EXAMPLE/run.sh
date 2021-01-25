#!/bin/sh

#SBATCH --out=io/runner_out__%A
#SBATCH --error=io/runner_err__%A

sbatch -W --job-name=nbxjob_0 --export=ALL,task_offset=0 --array=1-500%17 job.sh
wait
sbatch -W --job-name=nbxjob_1 --export=ALL,task_offset=500 --array=1-500%17 job.sh
wait
sbatch -W --job-name=nbxjob_2 --export=ALL,task_offset=1000 --array=1-500%17 job.sh
wait
sbatch -W --job-name=nbxjob_3 --export=ALL,task_offset=1500 --array=1-500%17 job.sh
wait
sbatch -W --job-name=nbxjob_4 --export=ALL,task_offset=2000 --array=1-500%17 job.sh
wait
sbatch -W --job-name=nbxjob_5 --export=ALL,task_offset=2500 --array=1-500%17 job.sh
wait
sbatch -W --job-name=nbxjob_6 --export=ALL,task_offset=3000 --array=1-453%17 job.sh
wait
