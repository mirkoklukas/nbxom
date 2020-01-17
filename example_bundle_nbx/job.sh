#!/bin/sh

#SBATCH --job-name=example_bundle
#SBATCH -t 2:0:00
#SBATCH --ntasks=4
#SBATCH --mem-per-cpu 2000
#SBATCH --mail-type=END
#SBATCH --mail-user=me@somewhere.com
#SBATCH --out=io/out_%a
#SBATCH --error=io/err_%a

source /etc/profile.d/modules.sh
module add openmind/singularity
export SINGULARITY_CACHEDIR=/om2/user/`whoami`/.singularity
singularity exec --nv -B /om:/om,/om2:/om2,/om2/user/mklukas/nbx-experiments:/omx /om2/user/mklukas/simg/pytorch.simg \
                                python wrapper.py \
                                --job-id   $SLURM_ARRAY_JOB_ID \
                                --task-id  $SLURM_ARRAY_TASK_ID \
                                --results-dir ./results