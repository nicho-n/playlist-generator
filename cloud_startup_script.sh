# Should be fed to GCE instance: https://cloud.google.com/compute/docs/instances/startup-scripts?_gl=1*1f2mznd*_ga*MjAzMTgxMzgzMS4xNzQwMTk3NDkx*_ga_WH2QY8WWF5*MTc0MTk4NDM0OC42LjEuMTc0MTk4ODc4My41NC4wLjA.

# Install or update needed software
apt-get update
apt-get install -yq git supervisor python3-full python3-pip python3-distutils

# Add spotify credentials
export $(cat /opt/app/environmental_variables.env | xargs)

# Fetch source code
export HOME=/root
git clone git@github.com:nicho-n/playlist-generator.git /opt/app

# Install Cloud Ops Agent
sudo bash /opt/app/add-google-cloud-ops-agent-repo.sh --also-install

# Account to own server process
#useradd -m -d /home/pythonapp pythonapp

# Python environment setup
python3 -m venv /opt/app/env
/bin/bash -c "source /opt/app/env/bin/activate"
/opt/app/env/bin/pip install -r /opt/app/requirements.txt

# Set ownership to newly created account
chown -R playlist-bot:playlist-bot /opt/app

# Put supervisor configuration in proper place
cp /opt/app/python-app.conf /etc/supervisor/conf.d/python-app.conf

# Start service via supervisorctl
supervisorctl reread
supervisorctl update
