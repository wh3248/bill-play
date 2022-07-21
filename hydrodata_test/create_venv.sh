module load anaconda3/2021.11

# Create or activate virtual environment
if [ -d hydro_env ]
then
    echo "Use virtual environment"
    source ./hydro_env/bin/activate
    pip install -r requirements.txt
else
    echo "Create virtual environment"
    python -m venv ./hydro_env
    source ./hydro_env/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    cp patches/io.py ./hydro_env/lib/python3.9/site-packages/parflow/tools
    cp patches/pf_backend.py ./hydro_env/lib/python3.9/site-packages/parflow/tools
fi