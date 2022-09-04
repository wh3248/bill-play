module load anaconda3/2021.11
VENV=~/PFB_VENV
if [ -d $VENV ]
then
    echo "Use virtual environment"
    source $VENV/bin/activate
    cd /home/wh3248/workspaces/parflow/pftools/python/parflow/tools/tests
else
    echo "Create virtual environment"
    python -m venv $VENV
    source $VENV/bin/activate
    python -m pip install --upgrade pip
    pip install -r ~/base_requirements.txt
fi
