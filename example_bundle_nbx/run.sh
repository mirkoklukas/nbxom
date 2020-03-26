#!/bin/sh

#SBATCH --out=io/runner_out__%A
#SBATCH --error=io/runner_err__%A

job_0=`sbatch --array=1-4%2 job.sh | awk '{ print $4 }'`
echo "Running jobs 1 - 4 ... "
job_1=`sbatch --array=5-8%2 --dependency=afterok:$job_0 job.sh | awk '{ print $4 }'`
echo "Running jobs 5 - 8 ... "
echo "done."