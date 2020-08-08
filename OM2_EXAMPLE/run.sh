#!/bin/sh

#SBATCH --out=io/runner_out__%A
#SBATCH --error=io/runner_err__%A

job_0=`sbatch --array=1-500%17 job_0.sh | awk '{ print $4 }'`
job_1=`sbatch --array=1-500%17 --dependency=afterok:$job_0 job_1.sh | awk '{ print $4 }'`
job_2=`sbatch --array=1-500%17 --dependency=afterok:$job_1 job_2.sh | awk '{ print $4 }'`
job_3=`sbatch --array=1-500%17 --dependency=afterok:$job_2 job_3.sh | awk '{ print $4 }'`
job_4=`sbatch --array=1-500%17 --dependency=afterok:$job_3 job_4.sh | awk '{ print $4 }'`
job_5=`sbatch --array=1-500%17 --dependency=afterok:$job_4 job_5.sh | awk '{ print $4 }'`
job_6=`sbatch --array=1-453%17 --dependency=afterok:$job_5 job_6.sh | awk '{ print $4 }'`
