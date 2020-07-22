#!/bin/sh

#SBATCH --out=io/runner_out__%A
#SBATCH --error=io/runner_err__%A

job_0=`sbatch --array=1-20%20 job.sh | awk '{ print $4 }'`
