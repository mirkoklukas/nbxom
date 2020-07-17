

{% for arr in arrays %}jid{{arr[0]}}=`sbatch --dependency=afterok:$jid{{arr[0]-1}} --array={{arr[1]}}-{{arr[2]}}%{{step}} job.sh | awk '{ print $4 }'`  {% if not loop.last %}
{% endif %}{% endfor %}

jid2=`sbatch --dependency=afterok:$jid1  job2.sh | awk '{ print $4 }'`