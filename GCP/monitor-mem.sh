#!/bin/bash

max_used_mem=0
output_file="mem.log"

while true; do
    # Get the total and used memory using the free command
    mem_info=$(free -m | grep Mem)
    total_mem=$(echo $mem_info | awk '{print $2}')
    used_mem=$(echo $mem_info | awk '{print $3}')

    # Update the maximum used memory if needed
    if [ $used_mem -gt $max_used_mem ]; then
        max_used_mem=$used_mem
        echo "New maximum used memory: $max_used_mem MB" > "$output_file"
    fi

    # Wait for 5 minutes before checking again
    sleep 300
done