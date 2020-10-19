"""DNS Authenticator for Constellix."""
import json
import logging
import time
import hmac
import hashlib
from base64 import b64encode

import requests
import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Constellix

    This Authenticator uses the Constellix DNS REST API to fulfill a dns-01 challenge.
    """

    description = "Obtain certificates using a DNS TXT record (if you are using Constellix for DNS)."
    ttl = 60

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=120
        )
        add("credentials", help="Constellix credentials INI file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 challenge using "
            + "the Constellix DNS REST API."
        )

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            "credentials",
            "Constellix DNS API credentials INI file",
            {
                "endpoint": "API endpoint for Constellix DNS API",
                "apikey": "API Key for Constellix DNS API.",
                "secretkey": "Secret Key for Constellix DNS API.",
            },
        )

    def _perform(self, domain, validation_name, validation):
        self._get_constellix_client().add_txt_record(
            domain, validation_name, validation, self.ttl
        )

    def _cleanup(self, domain, validation_name, validation):
        self._get_constellix_client().del_txt_record(
            domain, validation_name, validation, self.ttl
        )

    def _get_constellix_client(self):
        return _ConstellixClient(
            self.credentials.conf("endpoint"),
            self.credentials.conf("apikey"),
            self.credentials.conf("secretkey"),
        )


class _ConstellixClient(object):
    """
    Encapsulates all communication with the Constellix DNS REST API.
    """

    def __init__(self, endpoint, apikey, secretkey):
        logger.debug("creating constellixclient")
        self.endpoint = endpoint
        self.apikey = apikey
        self.secretkey = secretkey
        self.session = requests.Session()
        self.session.headers.update({'x-cnsdns-apiKey': self.apikey})

    def _current_time(self):
        return str(int(time.time() * 1000))

    def _hmac_hash(self, now):
        return hmac.new(self.secretkey.encode('utf-8'), now.encode('utf-8'),
                        digestmod=hashlib.sha1).digest()

    def _updatesecurityheaders(self):
        logger.debug("generating securitytoken for request")
        now = self._current_time()
        hmac_hash = self._hmac_hash(now)
        self.session.headers.update({
            'x-cnsdns-hmac': b64encode(hmac_hash),
            'x-cnsdns-requestDate': now
        })

    def _api_request(self, method, action, data):
        url = self._get_url(action)
        self._updatesecurityheaders()
        resp = self.session.request(method, url, json=data)
        logger.debug("API Request to URL: %s %s", method, url)
        try:
            result = resp.json()
        except:
            raise errors.PluginError("API response unknown {0}".format(resp.text))
        else:
            return resp.status_code, result

    def _get_url(self, action):
        return "{0}/{1}".format(self.endpoint, action)

    def _get_server_id(self, zone_id):
        zone = self._api_request("dns_zone_get", {"primary_id": zone_id})
        return zone["server_id"]

    def add_txt_record(self, domain, record_name, record_content, record_ttl):
        """
        Add a TXT record using the supplied information.

        :param str domain: The domain to use to look up the managed zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :param int record_ttl: The record TTL (number of seconds that the record may be cached).
        :raises certbot.errors.PluginError: if an error occurs communicating with the Constellix DNS API
        """
        zone_id, zone_name = self._find_managed_zone_id(domain, record_name)
        if zone_id is None:
            raise errors.PluginError("Domain not known")
        logger.debug("domain found: %s with id: %s", zone_name, zone_id)
        o_record_name = record_name
        record_name = record_name.replace(zone_name, "")[:-1]
        logger.debug(
            "using record_name: %s from original: %s", record_name, o_record_name
        )
        record = self.get_existing_txt(zone_id, record_name, record_content)
        if record is not None:
            if record["data"] == record_content:
                logger.info("already there, id {0}".format(record["id"]))
                return
            else:
                logger.info("update {0}".format(record["id"]))
                self._update_txt_record(
                    zone_id, record["id"], record_name, record_content, record_ttl
                )
        else:
            logger.info("insert new txt record")
            self._insert_txt_record(zone_id, record_name, record_content, record_ttl)

    def del_txt_record(self, domain, record_name, record_content, record_ttl):
        """
        Delete a TXT record using the supplied information.

        :param str domain: The domain to use to look up the managed zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').
        :param str record_content: The record content (typically the challenge validation).
        :param int record_ttl: The record TTL (number of seconds that the record may be cached).
        :raises certbot.errors.PluginError: if an error occurs communicating with the Constellix DNS API
        """
        zone_id, zone_name = self._find_managed_zone_id(domain, record_name)
        if zone_id is None:
            raise errors.PluginError("Domain not known")
        logger.debug("domain found: %s with id: %s", zone_name, zone_id)
        o_record_name = record_name
        record_name = record_name.replace(zone_name, "")[:-1]
        logger.debug(
            "using record_name: %s from original: %s", record_name, o_record_name
        )
        record = self.get_existing_txt(zone_id, record_name, record_content)
        if record is not None:
            logger.debug("delete TXT record: %s", record["id"])
            self._delete_txt_record(zone_id, record["id"])

    def _prepare_data(self, record_name, record_content, record_ttl):
        return {
            "name": record_name,
            "ttl": record_ttl,
            "roundRobin": [
                {
                    "value": record_content
                }
            ]
        }

    def _insert_txt_record(self, zone_id, record_name, record_content, record_ttl):
        data = self._prepare_data(record_name, record_content, record_ttl)
        logger.debug("insert with data: %s", data)
        status_code, result = self._api_request("POST", "domains/{0}/records/txt".format(zone_id), data)

    def _update_txt_record(
        self, zone_id, primary_id, record_name, record_content, record_ttl
    ):
        data = self._prepare_data(record_name, record_content, record_ttl)
        data["primary_id"] = primary_id
        logger.debug("update with data: %s", data)
        status_code, result = self._api_request("PUT", "domains/{0}/records/txt/{1}".format(zone_id, record_id), data)

    def _delete_txt_record(self, zone_id, record_id):
        logger.debug("delete record id: %s", record_id)
        status_code, result = self._api_request("DELETE", "domains/{0}/records/txt/{1}".format(zone_id, record_id), {})

    def _find_managed_zone_id(self, domain, record_name):
        """
        Find the managed zone for a given domain.

        :param str domain: The domain for which to find the managed zone.
        :returns: The ID of the managed zone, if found.
        :rtype: str
        :raises certbot.errors.PluginError: if the managed zone cannot be found.
        """

        zone_dns_name_guesses = [record_name] + dns_common.base_domain_name_guesses(domain)

        for zone_name in zone_dns_name_guesses:
            # get the zone id
            try:
                logger.debug("looking for zone: %s", zone_name)
                status_code, result = self._api_request("GET", "domains/search?exact={0}".format(zone_name), {})
                if status_code == 200 and len(result) > 0:
                    return result[0]['id'], result[0]['name']
            except errors.PluginError as e:
                pass
        return None

    def get_existing_txt(self, zone_id, record_name, record_content):
        """
        Get existing TXT records for the record name.

        If an error occurs while requesting the record set, it is suppressed
        and None is returned.

        :param str zone_id: The ID of the managed zone.
        :param str record_name: The record name (typically beginning with '_acme-challenge.').

        :returns: TXT record value or None
        :rtype: `string` or `None`

        """
        status_code, records = self._api_request("GET", "domains/{0}/records/txt/search?exact={1}".format(zone_id, record_name), {})
        if not status_code == 200:
            return None
        for record in records:
            status_code, data = self._api_request("GET", "domains/{0}/records/txt/{1}".format(zone_id, record["id"]), {})
            fullvalue = ""
            for value in data['value']:
                fullvalue += value["value"].strip('"')
            if fullvalue == record_content:
                return data
        return None
