#!/bin/bash
#SBATCH --job-name=git_add
#SBATCH --time=1-00:00:00
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=4
#SBATCH --mem=512000
#SBATCH -o add.text
#SBATCH -e add_e.txt

python add.py

