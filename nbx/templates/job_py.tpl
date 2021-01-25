#!/bin/sh

{% for k,v in job_header %}#SBATCH --{{k}}={{v}}
{% endfor %}

{% for a,b in symlinks%}ln -sfn {{a}} {{b}}
{% endfor %} 
source /etc/profile.d/modules.sh
module add openmind/singularity
export SINGULARITY_CACHEDIR=/om2/user/`whoami`/.singularity
singularity exec -B /om:/om,/om5:/om5,/om2:/om2,{{nbx_folder}}:/omx{% for a,b in bind%},{{a}}:{{b}}{% endfor %} \
                                {{simg}} \
                                python {{experiment}} \
                                --job-id   $SLURM_ARRAY_JOB_ID \
                                --task-id  $(($SLURM_ARRAY_TASK_ID + $task_offset)) \
                                --results-dir {{results_dir}}