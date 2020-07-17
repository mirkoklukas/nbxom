#!/bin/sh

#SBATCH --out=io/runner_out__%A
#SBATCH --error=io/runner_err__%A

job_0=`sbatch --array=1-10%50 job.sh | awk '{ print $4 }'`
job_1=`sbatch --array=11-20%50 --dependency=afterok:$job_0 job.sh | awk '{ print $4 }'`
