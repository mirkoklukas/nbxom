#!/bin/sh

#SBATCH --time=10:00:00
#SBATCH --partition=fiete
#SBATCH --mail-user=me@somewhere.com
#SBATCH --out=io/out_%a
#SBATCH --error=io/err_%a
#SBATCH --mail-type=END
#SBATCH --exclude=node030,node016,node015


source /etc/profile.d/modules.sh
module add openmind/singularity
export SINGULARITY_CACHEDIR=/om5/user/`whoami`/.singularity
singularity exec -B /om:/om,/om5:/om5,/om2:/om2,/om2/user/mklukas/nbx-experiments:/omx \
                                /om2/user/mklukas/simg/pytorch.simg \
                                python experiment.py \
                                --job-id   $SLURM_ARRAY_JOB_ID \
                                --task-id  $(($SLURM_ARRAY_TASK_ID + 500)) \
                                --results-dir results