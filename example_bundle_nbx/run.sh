#!/bin/sh

job_0=`sbatch --array=1-5%1 job.sh | awk '{ print $4 }'`
