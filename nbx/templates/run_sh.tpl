#!/bin/sh

#SBATCH --out=io/runner_out__%A
#SBATCH --error=io/runner_err__%A

{% for d in specs_array %}sbatch -W --job-name={{job_name}}_{{d[0]}} --export=ALL,task_offset={{d[3]}} --array={{d[1]}}-{{d[2]}}%{{step}} job.sh
wait
{% endfor %}