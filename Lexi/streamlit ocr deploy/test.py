with open('requirements.txt', 'r') as req_file:
    lines = req_file.readlines()

with open('en.env', 'w') as env_file:
    for line in lines:
        if line.strip():  # Ignore empty lines
            package_name, package_version = line.strip().split('==')
            env_file.write(f"{package_name.upper()}={package_version}\n")
