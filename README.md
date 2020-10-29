# certbot-dns-constellix Documentation

The `certbot-dns-constellix` plugin is used to automate the process of
a `dns-01` challenge in Certbot to allow the requesting and renewal of SSL
certificates through the Constellix DNS API.

This is done through the process of adding and removing TXT records to the
appropriate domain in your Constellix DNS account.

## Installation

1. Install certbot for your operating system
2. Install the plugin by using `pip install certbot-dns-constellix`

## Configuration

The plugin requires an API key and secret key for the Constellix DNS API. The
key will need to have permissions to add and remove records on the domain you
want to issue certificates for.

These will need to be added to a file, eg. `constellix.ini` in the following
format:

```
certbot_dns_constellix:constellix_dns_apikey=5fb4e76f-ac91-43e5-f982458bc595
certbot_dns_constellix:constellix_dns_secretkey=47d99fd0-32e7-4e07-85b46d08e70b
certbot_dns_constellix:constellix_dns_endpoint=https://api.dns.constellix.com
```

### Caution

You should secure this file from any unauthorised access. Anyone with access
to these credentials and this file will be able to add and remove records from
your domain. You should configure the file to not be readable by any other
users on the system

## Usage

Once the plugin is installed and configured it can be used by specifying the
plugin in the certbot command and the location of the credentials file.

```
certbot certonly \
    --certbot-dns-constellix:dns-constellix \
    --certbot-dns-constellix:dns-constellix-credentials=~./constellix.ini \
    -d example.com
```

For more options please check the certbot documentation.





