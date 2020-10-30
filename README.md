# certbot-dns-constellix Documentation

The `certbot-dns-constellix` plugin is used to automate the process of a `dns-01` challenge in Certbot to allow the requesting and renewal of SSL certificates through the Constellix DNS API.

This is done through the process of adding and removing TXT records to the appropriate domain in your Constellix DNS account. 

There are two different methods of installing, configuring and using the plugin depending on if you're using certbot installed through snapd or through your operating system's package manager.

## Certbot Installed using Snapd

If you installed certbot using snapd, do the following to install and configure the plugin:

### Installation

Run the following commands to install the plugin with snapd.

```
sudo snap install certbot-dns-constellix
sudo snap set certbot trust-plugin-with-root=ok
sudo snap connect certbot:plugin certbot-dns-constellix
```

Verify that the plugin is installed by running `certbot plugins`. You should see the `dns-constellix` plugin in the list.

### Configuration

The plugin requires an API key and secret key for the Constellix DNS API. The key will need to have permissions to add and remove records on the domain you want to issue certificates for.

These will need to be added to a file, eg. `constellix.ini` in the following format:

```
dns_constellix_apikey=5fb4e76f-ac91-43e5-f982458bc595
dns_constellix_secretkey=47d99fd0-32e7-4e07-85b46d08e70b
dns_constellix_endpoint=https://api.dns.constellix.com/v1
```

#### Caution

You should secure this file from any unauthorised access. Anyone with access to these credentials and this file will be able to add and remove records from your domain. You should configure the file to not be readable by any other users on the system

### Usage

Once the plugin is installed and configured it can be used by specifying the plugin in the `certbot` command and the location of the credentials file.

```
certbot certonly \
    --authenticator=dns-constellix \
    --dns-constellix-credentials=~./constellix.ini \
    -d example.com
```

For more options please check the certbot documentation.

## Certbot Installed using OS Package Manager/Python

If you installed certbot using your operating system's package manager (apt, yum, etc.) or directly with Python, you can install it using these instructions.

### Installation

Run the following commands to install the plugin using pip.

```
sudo python3 -m pip install certbot-dns-constellix
```

Verify that the plugin is installed by running `certbot plugins`. You should see the `dns-constellix` plugin in the list.

### Configuration

The plugin requires an API key and secret key for the Constellix DNS API. The key will need to have permissions to add and remove records on the domain you want to issue certificates for.

These will need to be added to a file, eg. `constellix.ini` in the following format:

```
certbot-dns-constellix:dns_constellix_apikey=5fb4e76f-ac91-43e5-f982458bc595
certbot-dns-constellix:dns_constellix_secretkey=47d99fd0-32e7-4e07-85b46d08e70b
certbot-dns-constellix:dns_constellix_endpoint=https://api.dns.constellix.com/v1
```

The extra `certbot-dns-constellix:` is required due to how older versions of Certbot load plugins.

#### Caution

You should secure this file from any unauthorised access. Anyone with access to these credentials and this file will be able to add and remove records from your domain. You should configure the file to not be readable by any other users on the system

### Usage

Once the plugin is installed and configured it can be used by specifying the plugin in the `certbot` command and the location of the credentials file.

```
certbot certonly \
    --authenticator=certbot-dns-constellix:dns-constellix \
    --certbot-dns-constellix:dns-constellix-credentials=~./constellix.ini \
    -d example.com
```

The extra `certbot-dns-constellix:` is required due to how older versions of Certbot load plugins.

For more options please check the certbot documentation.

